import networkx as nx
import plotly.graph_objects as go

from app.analytics import intent_color_vec


def build_visit_graph(df, limit=300):
      graph = nx.DiGraph()
      top = df.nlargest(min(limit, len(df)), "intent_score")
      id_set = set(top["visit_id"])

      for _, row in top.iterrows():
            graph.add_node(
                  row["visit_id"],
                  title=row["title"],
                  score=row["intent_score"],
                  url=row["url"],
                  time=row["visit_time"],
            )
            if row["from_visit_id"] in id_set:
                  graph.add_edge(row["from_visit_id"], row["visit_id"], etype="nav")
            if row["opener_visit_id"] in id_set:
                  graph.add_edge(row["opener_visit_id"], row["visit_id"], etype="tab")

      return graph, id_set


def build_nav_graph(df, selected_id=None):
      graph, id_set = build_visit_graph(df)
      if len(graph.nodes) == 0:
            return go.Figure()

      pos = nx.spring_layout(graph, k=2.5, iterations=40, seed=42)

      edge_x, edge_y = [], []
      for source, target in graph.edges():
            x0, y0 = pos[source]
            x1, y1 = pos[target]
            edge_x += [x0, x1, None]
            edge_y += [y0, y1, None]

      node_ids = list(graph.nodes())
      node_scores = [graph.nodes[node_id]["score"] for node_id in node_ids]
      node_colors = intent_color_vec(node_scores)
      node_sizes = [8 + abs(score) * 1.5 for score in node_scores]

      if selected_id and selected_id in id_set:
            node_sizes = [
                  size * 2.2 if node_id == selected_id else size
                  for node_id, size in zip(node_ids, node_sizes)
            ]
            node_colors = [
                  "#ffffff" if node_id == selected_id else color
                  for node_id, color in zip(node_ids, node_colors)
            ]

      hover = [
            f"<b>{graph.nodes[node_id]['title'][:40]}</b><br>"
            f"Score: {graph.nodes[node_id]['score']:+.2f}"
            for node_id in node_ids
      ]

      fig = go.Figure()
      fig.add_trace(go.Scatter(
            x=edge_x,
            y=edge_y,
            mode="lines",
            line=dict(color="#1f2130", width=1),
            hoverinfo="none",
      ))
      fig.add_trace(go.Scatter(
            x=[pos[node_id][0] for node_id in node_ids],
            y=[pos[node_id][1] for node_id in node_ids],
            mode="markers",
            marker=dict(color=node_colors, size=node_sizes, line=dict(width=0)),
            hovertext=hover,
            hoverinfo="text",
            customdata=node_ids,
      ))
      fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Space Mono", color="#555878", size=10),
            showlegend=False,
            margin=dict(l=8, r=8, t=8, b=8),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            hovermode="closest",
            clickmode="event",
      )
      return fig
