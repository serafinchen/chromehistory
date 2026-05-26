from ccl_chromium_reader import ChromiumProfileFolder
import networkx as nx
from pyvis.network import Network
import webbrowser
import os
from history import compute_intent_score

def score_to_color(score):
      if score >= 3:
            return "#2eccb7" 
      elif score >= 1:
            return "#f1c40f"
      elif score >= 0:
            return "#95a5a6"
      else:
            return "#e74c3c"

      
def build_chrome_history_graph(profile_path, limit=200):
      G = nx.DiGraph()

      with ChromiumProfileFolder(profile_path) as profile:
            history = list(profile.iterate_history_records())

      history.sort(key=lambda h: h.visit_time, reverse=True)
      history = history[:limit]
      
      lookup = {h.rec_id: h for h in history}
      score = compute_intent_score()

      for h in history:
            G.add_node(
                  h.rec_id,
                  url=h.url,
                  title=h.title,
                  visit_time=str(h.visit_time),
                  intent_score=score
            )

            if h.from_visit_id in lookup:
                  parent = lookup[h.from_visit_id]
                  G.add_edge(
                  parent.rec_id,
                  h.rec_id,
                  type="from_visit",
                  transition=str(h.transition)
                  )

            if h.opener_visit_id in lookup:
                  opener = lookup[h.opener_visit_id]
                  G.add_edge(
                  opener.rec_id,
                  h.rec_id,
                  type="opener"
                  )

      return G

def plot_history_pyvis(G, output_file="chrome_history.html"):
      net = Network(
            height="800px",
            width="100%",
            directed=True,
            bgcolor="#ffffff",
            font_color="black"
      )

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

            for u, v, data in G.edges(data=True):
                  edge_score = (G.nodes[u]["intent_score"] + G.nodes[v]["intent_score"]) / 2

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