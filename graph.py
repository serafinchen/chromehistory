from ccl_chromium_reader import ChromiumProfileFolder
import networkx as nx
from pyvis.network import Network
import webbrowser
import os

def build_chrome_history_graph(profile_path, limit=200):
      G = nx.DiGraph()

      with ChromiumProfileFolder(profile_path) as profile:
            history = list(profile.iterate_history_records())

      history.sort(key=lambda h: h.visit_time, reverse=True)
      history = history[:limit]
      
      lookup = {h.rec_id: h for h in history}

      for h in history:
            G.add_node(
                  h.rec_id,
                  url=h.url,
                  title=h.title,
                  visit_time=str(h.visit_time)
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

            net.add_node(
                  n,
                  label=title[:30] if title else str(n),
                  title=url,
                  size=10
            )

      for u, v, data in G.edges(data=True):
            net.add_edge(
                  u,
                  v,
                  title=data.get("type", ""),
                  arrows="to"
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