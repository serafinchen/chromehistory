from ccl_chromium_reader import ChromiumProfileFolder
import networkx as nx
from pyvis.network import Network
import webbrowser
import os
from app.analytics import compute_intent_score, score_to_color
from app.history import normalize, HistoryVisit
      
def build_chrome_history_graph(visits: list[HistoryVisit], limit=200) -> nx.DiGraph:
      G = nx.DiGraph()
      visits.sort(key=lambda v:v.visit_time, reverse=True)

      visits = visits[:limit]

      lookup = {
            visit.visit_id: visit
            for visit in visits
      }

      for v in visits:
            G.add_node(
                  v.visit_id,
                  url=v.url,
                  title=v.title,
                  visit_time=v.visit_time,
                  visit_duration=v.visit_duration_seconds,
                  intent_score=v.intent_score
            )

            #navigation
            if v.from_visit_id in lookup:
                  parent = lookup[v.from_visit_id]
                  G.add_edge(parent.visit_id, v.visit_id, type="from_visit")
            
            #opened in new tab
            if v.opener_visit_id in lookup:
                  opener = lookup[v.opener_visit_id]
                  G.add_edge(opener.visit_id, v.visit_id, type="opener")

      return G

def plot_history_pyvis(G: nx.DiGraph, output_file: str = "chrome_history.html") -> None:
      net = Network(
            height="800px",
            width="100%",
            directed=True,
            bgcolor="#ffffff",
            font_color="black"
      )

      #Nodes
      for n, data in G.nodes(data=True):
            title = data.get("title", "")
            url = data.get("url", "")
            time = data.get("visit_time", "")
            score = data.get("intent_score", 0)

            tooltip = f"""
            <b>{title}</b><br>
            URL: {url}<br>
            Time: {time}<br>
            Intent Score: {score}
            """

            net.add_node(
                  n,
                  label=title[:30] if title else str(n),
                  title=tooltip,
                  size=10 + abs(score) * 2,
                  color = score_to_color(score)
            )

      #Edges
      for u, v, data in G.edges(data=True):
            u_score = G.nodes[u].get("intent_score", 0)
            v_score = G.nodes[v].get("intent_score", 0)

            edge_score = (u_score + v_score) / 2


            color = score_to_color(edge_score)
            width = max(1, abs(edge_score))

            net.add_edge(
                  u,
                  v,
                  title=f"Edge intent score: {edge_score:.2f}",
                  arrows="to",
                  color=color,
                  width=width
            )

      net.set_options("""
      var options = {
            "physics": {
                  "forceAtlas2Based": {
                        "gravitationalConstant": -50,
                        "centralGravity": 0.01,
                        "springLength": 100
                  },
                  "solver": "forceAtlas2Based",
                  "stabilization": {
                        "iterations": 50
                  }
            }
      }
      """)

      
      net.write_html(output_file, open_browser=False)

      webbrowser.open("file://" + os.path.abspath(output_file))
      