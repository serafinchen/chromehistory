import plotly.graph_objects as go
import networkx as nx
from analytics import intent_color_vec


def build_nav_graph(G, selected_id=None):
      pos = nx.spring_layout(G, seed=42)

      edge_x, edge_y = [], []
      for u, v in G.edges():
            x0, y0 = pos[u]
            x1, y1 = pos[v]
            edge_x += [x0, x1, None]
            edge_y += [y0, y1, None]

      node_x = [pos[n][0] for n in G.nodes()]
      node_y = [pos[n][1] for n in G.nodes()]

      scores = [G.nodes[n]["intent_score"] for n in G.nodes()]

      fig = go.Figure()

      fig.add_trace(go.Scatter(x=edge_x, y=edge_y, mode="lines"))
      fig.add_trace(go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers",
            marker=dict(color=intent_color_vec(scores))
      ))

      return fig