import networkx as nx
import plotly.graph_objects as go
import plotly.colors as pcolors
import textwrap
from app.analytics import decode_core, decode_qualifier, visit_type_color

MAX_GRAPH_NODES = 100

LANE_PALETTE = (
	pcolors.qualitative.Set3
	+ pcolors.qualitative.Pastel
	+ pcolors.qualitative.Set2
)


def build_visit_graph(df, limit=MAX_GRAPH_NODES):

	graph = nx.DiGraph()

	df = df.sort_values("visit_time_dt").copy()

	if "duration_sec" not in df.columns:
		df["duration_sec"] = (
			df["visit_time_dt"].shift(-1) - df["visit_time_dt"]
		).dt.total_seconds()

		df["duration_sec"] = df["duration_sec"].fillna(0).clip(0, 3600)

	if len(df) > limit:
		df = df.tail(limit)

	id_set = set(df["visit_id"])

	for _, row in df.iterrows():
		tags = [
			*decode_core(int(row.get("transition", 0))),
			*decode_qualifier(int(row.get("transition_qualifiers", 0))),
		]

		graph.add_node(
			row["visit_id"],
			title=row["title"],
			url=row["url"],
			score=row.get("intent_score", 0),
			time=row["visit_time"],
			time_dt=row["visit_time_dt"],
			duration=row["duration_sec"],
			tags=tags,
		)

		if row["from_visit_id"] in id_set:
			graph.add_edge(
				row["from_visit_id"],
				row["visit_id"],
				etype="nav",
				tags=tags,
			)

		if row["opener_visit_id"] in id_set:
			graph.add_edge(
				row["opener_visit_id"],
				row["visit_id"],
				etype="tab",
				tags=tags,
			)

	return graph, id_set


def _is_redirect(tags):
	return any("REDIRECT" in str(t).upper() for t in tags)


def _lane_color(lane_id):
	return LANE_PALETTE[lane_id % len(LANE_PALETTE)]


def _timeline_layout(graph):
	nodes = sorted(graph.nodes(), key=lambda n: graph.nodes[n]["time_dt"])

	lane_of = {}
	lane_origin = {}

	pos = {}

	next_lane = 0

	for node in nodes:
		preds = list(graph.predecessors(node))

		nav_parent = next(
			(p for p in preds if graph.edges[p, node]["etype"] == "nav"), None
		)

		tab_parent = next(
			(p for p in preds if graph.edges[p, node]["etype"] == "tab"), None
		)

		if nav_parent is not None:
			if nav_parent in lane_of:
				lane = lane_of[nav_parent]
			else:
				lane = next_lane
				next_lane += 1
			origin = "continue"

		elif tab_parent is not None:
			lane = next_lane
			next_lane += 1
			origin = "tab"

		else:
			lane = next_lane
			next_lane += 1
			origin = "isolated"

		lane_of[node] = lane
		lane_origin[node] = origin

		pos[node] = (graph.nodes[node]["time_dt"].timestamp(), -lane)

	return pos, lane_of, lane_origin


def build_nav_graph(df, selected_id=None):

	graph, id_set = build_visit_graph(df)

	if len(graph.nodes) == 0:
		return go.Figure()

	pos, lane_of, lane_origin = _timeline_layout(graph)

	fig = go.Figure()
	nav_edges_by_lane = {}
	redirect_x, redirect_y = [], []
	tab_x, tab_y = [], []

	for source, target, data in graph.edges(data=True):
		x0, y0 = pos[source]
		x1, y1 = pos[target]
		tags = data.get("tags", [])

		if data["etype"] == "nav":
			if _is_redirect(tags):
				redirect_x += [x0, x1, None]
				redirect_y += [y0, y1, None]
			else:
				lane = lane_of[target]
				bucket = nav_edges_by_lane.setdefault(lane, ([], []))
				bucket[0].extend([x0, x1, None])
				bucket[1].extend([y0, y1, None])
		else:
			tab_x += [x0, x1, None]
			tab_y += [y0, y1, None]

	for lane, (xs, ys) in nav_edges_by_lane.items():
		fig.add_trace(
			go.Scatter(
				x=xs,
				y=ys,
				mode="lines",
				line=dict(color=_lane_color(lane), width=2),
				hoverinfo="none",
				showlegend=False,
			)
		)

	fig.add_trace(
		go.Scatter(
			x=tab_x,
			y=tab_y,
			mode="lines",
			line=dict(color="#555878", width=1.3, dash="dot"),
			hoverinfo="none",
			showlegend=False,
		)
	)

	fig.add_trace(
		go.Scatter(
			x=redirect_x,
			y=redirect_y,
			mode="lines",
			line=dict(color="#ff8a3d", width=2.5, dash="dash"),
			hoverinfo="none",
			showlegend=False,
		)
	)


	node_ids = list(graph.nodes())

	node_sizes = [8 + min(graph.nodes[n]["duration"] / 20, 40) for n in node_ids]

	node_colors = []
	for n in node_ids:
		tags = graph.nodes[n]["tags"]
		node_colors.append(visit_type_color(tags))

	if selected_id and selected_id in id_set:
		node_sizes = [
			size * 2.2 if n == selected_id else size
			for n, size in zip(node_ids, node_sizes)
		]

	symbol_map = {
		"continue": "circle",
		"tab": "square",
		"isolated": "diamond",
	}
	node_symbols = [symbol_map[lane_origin[n]] for n in node_ids]
	node_line_colors = [_lane_color(lane_of[n]) for n in node_ids]

	hover = [
		f"""
		<b>{graph.nodes[n]["title"][:60]}</b><br>
		{graph.nodes[n]["time"]}<br>
		Duration: {graph.nodes[n]["duration"]:.0f}s<br>
		Lane-Origin: {lane_origin[n]}<br>
		URL:<br>
		{'<br>'.join(textwrap.wrap(graph.nodes[n]["url"], width=50))}
		"""
		for n in node_ids
	]

	fig.add_trace(
		go.Scatter(
			x=[pos[n][0] for n in node_ids],
			y=[pos[n][1] for n in node_ids],
			mode="markers",
			marker=dict(
				color=node_colors,
				size=node_sizes,
				symbol=node_symbols,
				line=dict(color=node_line_colors, width=2),
			),
			hovertext=hover,
			hoverinfo="text",
			customdata=node_ids,
			showlegend=False,
		)
	)

	tick_nodes = sorted(graph.nodes(), key=lambda n: pos[n][0])

	tick_step = max(1, len(tick_nodes) // 10)

	tick_nodes = tick_nodes[::tick_step]

	fig.update_layout(
		paper_bgcolor="rgba(0,0,0,0)",
		plot_bgcolor="rgba(0,0,0,0)",
		font=dict(family="Space Mono", color="#555878", size=10),
		margin=dict(l=8, r=20, t=8, b=30),
		xaxis=dict(
			showgrid=False,
			zeroline=False,
			tickmode="array",
			tickvals=[pos[n][0] for n in tick_nodes],
			ticktext=[str(graph.nodes[n]["time"])[11:16] for n in tick_nodes],
		),
		yaxis=dict(visible=False),
		hovermode="closest",
		clickmode="event",
	)

	return fig