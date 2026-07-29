import networkx as nx
import plotly.graph_objects as go

from app.analytics import intent_color_vec

MAX_GRAPH_NODES = 100


def build_visit_graph(df, limit=MAX_GRAPH_NODES):
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
            time_dt=row["visit_time_dt"],
        )
        if row["from_visit_id"] in id_set:
            graph.add_edge(row["from_visit_id"], row["visit_id"], etype="nav")
        if row["opener_visit_id"] in id_set:
            graph.add_edge(row["opener_visit_id"], row["visit_id"], etype="tab")

    return graph, id_set


def _timeline_layout(graph):
    """
    Ordnet die Knoten chronologisch von links nach rechts an.

    Jede "Spur" (Lane) auf der y-Achse entspricht in etwa einem
    zusammenhaengenden Browsing-Strang:
      - "nav"-Kanten (Navigation im selben Tab) bleiben in derselben Spur
      - "tab"-Kanten (neuer Tab geoeffnet) erzeugen eine neue Spur
        -> Verzweigungen werden dadurch sofort sichtbar
    """
    nodes_by_time = sorted(graph.nodes(), key=lambda n: graph.nodes[n]["time_dt"])

    lane_of = {}
    lane_free_at = {}  # lane -> Zeit-Index der letzten Belegung (fuer Wiederverwendung)
    pos = {}

    next_lane = 0

    def free_lane(exclude=None):
        nonlocal next_lane
        candidate = next(
            (
                lane for lane, last_used in lane_free_at.items()
                if last_used < i - 1 and lane != exclude
            ),
            None,
        )
        if candidate is None:
            candidate = next_lane
            next_lane += 1
        return candidate

    for i, node in enumerate(nodes_by_time):
        preds = list(graph.predecessors(node))
        nav_parent = next((p for p in preds if graph.edges[p, node]["etype"] == "nav"), None)
        tab_parent = next((p for p in preds if graph.edges[p, node]["etype"] == "tab"), None)

        if nav_parent is not None:
            # Fortsetzung im selben Tab -> gleiche Spur wie der Parent
            lane = lane_of[nav_parent]
        elif tab_parent is not None:
            # Neuer Tab wurde aus einem bestehenden Visit geoeffnet -> neue/wiederverwendete Spur
            lane = free_lane(exclude=lane_of.get(tab_parent))
        else:
            # Neue Wurzel (kein bekannter Vorgaenger)
            lane = free_lane()

        lane_of[node] = lane
        lane_free_at[lane] = i
        pos[node] = (i, -lane)

    return pos


def build_nav_graph(df, selected_id=None):
    graph, id_set = build_visit_graph(df)
    if len(graph.nodes) == 0:
        return go.Figure()

    pos = _timeline_layout(graph)

    nav_edge_x, nav_edge_y = [], []
    tab_edge_x, tab_edge_y = [], []
    for source, target, data in graph.edges(data=True):
        x0, y0 = pos[source]
        x1, y1 = pos[target]
        if data["etype"] == "nav":
            nav_edge_x += [x0, x1, None]
            nav_edge_y += [y0, y1, None]
        else:
            tab_edge_x += [x0, x1, None]
            tab_edge_y += [y0, y1, None]

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
        f"{graph.nodes[node_id]['time']}<br>"
        f"Score: {graph.nodes[node_id]['score']:+.2f}"
        for node_id in node_ids
    ]

    fig = go.Figure()

    # Navigation im selben Tab: durchgezogene Linie
    fig.add_trace(go.Scatter(
        x=nav_edge_x,
        y=nav_edge_y,
        mode="lines",
        line={"color": "#3a3d55", "width": 1.5},
        hoverinfo="none",
        showlegend=False,
    ))

    # Neuer Tab geoeffnet: gepunktete Linie
    fig.add_trace(go.Scatter(
        x=tab_edge_x,
        y=tab_edge_y,
        mode="lines",
        line={"color": "#1f2130", "width": 1, "dash": "dot"},
        hoverinfo="none",
        showlegend=False,
    ))

    fig.add_trace(go.Scatter(
        x=[pos[node_id][0] for node_id in node_ids],
        y=[pos[node_id][1] for node_id in node_ids],
        mode="markers",
        marker={"color": node_colors, "size": node_sizes, "line": {"width": 0}},
        hovertext=hover,
        hoverinfo="text",
        customdata=node_ids,
        showlegend=False,
    ))

    # ein paar Zeit-Ticks auf der x-Achse zur Orientierung
    tick_step = max(1, len(node_ids) // 10)
    tick_nodes = sorted(graph.nodes(), key=lambda n: pos[n][0])[::tick_step]

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Space Mono", "color": "#555878", "size": 10},
        showlegend=False,
        margin={"l": 8, "r": 20, "t": 8, "b": 30},
        xaxis={
            "visible": True,
            "showgrid": False,
            "zeroline": False,
            "tickmode": "array",
            "tickvals": [pos[n][0] for n in tick_nodes],
            "ticktext": [str(graph.nodes[n]["time"])[11:16] for n in tick_nodes],
            "tickfont": {"size": 9},
        },
        yaxis={"visible": False},
        hovermode="closest",
        clickmode="event",
    )
    return fig