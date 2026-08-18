import math

import networkx as nx
import pandas as pd
import plotly.graph_objects as go

from app.analytics import visit_type_color
from app.components.nav_graph_style import (
	ADDRESS_BAR_BORDER_WIDTH,
	CACHED_SYMBOL_SUFFIX,
	EDGE_STYLE,
	ERROR_BORDER_COLOR,
	NORMAL_BORDER_WIDTH,
	transition_symbol,
	transition_label,
)

MAX_GRAPH_NODES = 50

def _parse_transition(row):
	core = row.get("transition_core")
	if not core or (isinstance(core, float) and pd.isna(core)):
		core = "UNKNOWN"

	qual_str = row.get("transition_qualifier") or ""
	if isinstance(qual_str, float) and pd.isna(qual_str):
		qual_str = ""
	qualifiers = qual_str.split("|") if qual_str else []

	return core, qualifiers


def _is_error_row(row):
	code = row.get("response_code")

	if code is None or (isinstance(code, float) and pd.isna(code)):
		return False

	return code >= 400


def build_visit_graph(df, limit=MAX_GRAPH_NODES):

	graph = nx.DiGraph()

	df = df.sort_values("visit_time_dt").copy()

	#Calculate if no duration (for circle size)
	if "duration_sec" not in df.columns:
		if "visit_duration" in df.columns:
			df["duration_sec"] = df["visit_duration"]
		else:
			df["duration_sec"] = (
				df["visit_time_dt"].shift(-1) - df["visit_time_dt"]
			).dt.total_seconds()

			df["duration_sec"] = df["duration_sec"].fillna(0).clip(0, 3600)

	if len(df) > limit:
		df = df.tail(limit)

	id_set = set(df["rec_id"])

	for _, row in df.iterrows():
		core, qualifiers = _parse_transition(row)

		tags = [core, *qualifiers]

		graph.add_node(
			row["rec_id"],
			title=row["title"],
			url=row["url"],
			time=row["visit_time"],
			time_dt=row["visit_time_dt"],
			duration=row["duration_sec"],
			tags=tags,
			core=core,
			qualifiers=qualifiers,
			cached=bool(row.get("cached", False)),
			is_error=_is_error_row(row),
			response_code=row.get("response_code"),
			content_type=row.get("content_type"),
		)

		if row["from_visit_id"] in id_set:
			graph.add_edge(
				row["from_visit_id"],
				row["rec_id"],
				etype="nav",
			)

		if row["opener_visit_id"] in id_set:
			graph.add_edge(
				row["opener_visit_id"],
				row["rec_id"],
				etype="tab",
			)

	return graph, id_set


#Positions
def _timeline_layout(graph):
	nodes = sorted(graph.nodes(), key=lambda n: graph.nodes[n]["time_dt"])
	lane_of = {}
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
			lane = lane_of[nav_parent] if nav_parent in lane_of else next_lane
			if nav_parent not in lane_of:
				next_lane += 1

		elif tab_parent is not None:
			lane = next_lane
			next_lane += 1

		else:
			lane = next_lane
			next_lane += 1

		lane_of[node] = lane
		pos[node] = (graph.nodes[node]["time_dt"].timestamp(), -lane)

	return pos, lane_of


def _classify_nav_edge(graph, target):
	qualifiers = [q.upper() for q in graph.nodes[target]["qualifiers"]]

	if any("REDIRECT" in q for q in qualifiers):
		return "redirect"

	if any("FORWARD_BACK" in q for q in qualifiers):
		return "back_forward"

	return "lane"

#Creating the Graph
def build_nav_graph(df, selected_id=None):

	graph, id_set = build_visit_graph(df)

	if len(graph.nodes) == 0:
		return go.Figure()

	pos, lane_of = _timeline_layout(graph)

	fig = go.Figure()

	nav_edges_by_lane = {}
	redirect_x, redirect_y = [], []
	back_forward_x, back_forward_y = [], []
	tab_x, tab_y = [], []

	for source, target, data in graph.edges(data=True):
		x0, y0 = pos[source]
		x1, y1 = pos[target]

		if data["etype"] == "tab":
			tab_x += [x0, x1, None]
			tab_y += [y0, y1, None]
			continue

		kind = _classify_nav_edge(graph, target)

		if kind == "redirect":
			redirect_x += [x0, x1, None]
			redirect_y += [y0, y1, None]
		elif kind == "back_forward":
			back_forward_x += [x0, x1, None]
			back_forward_y += [y0, y1, None]
		else:
			lane = lane_of[target]
			bucket = nav_edges_by_lane.setdefault(lane, ([], []))
			bucket[0].extend([x0, x1, None])
			bucket[1].extend([y0, y1, None])

	for lane, (xs, ys) in nav_edges_by_lane.items():
		fig.add_trace(
			go.Scatter(
				x=xs,
				y=ys,
				mode="lines",
				line=dict(color="#888888", width=2),
				hoverinfo="none",
				showlegend=False,
			)
		)

	#Different Lines between nodes (tab, back_forward, redirect)
	fig.add_trace(
		go.Scatter(
			x=tab_x,
			y=tab_y,
			mode="lines",
			line=EDGE_STYLE["tab"],
			hoverinfo="none",
			showlegend=False,
		)
	)

	fig.add_trace(
		go.Scatter(
			x=back_forward_x,
			y=back_forward_y,
			mode="lines",
			line=EDGE_STYLE["back_forward"],
			hoverinfo="none",
			showlegend=False,
		)
	)

	fig.add_trace(
		go.Scatter(
			x=redirect_x,
			y=redirect_y,
			mode="lines",
			line=EDGE_STYLE["redirect"],
			hoverinfo="none",
			showlegend=False,
		)
	)

	node_ids = list(graph.nodes())

	# Node size grows sublinearly with visit duration, keeping long visits readable.
	node_sizes = [
		8 + min(math.sqrt(max(graph.nodes[n]["duration"], 0) / 20), 12)
		for n in node_ids
	]

	#node coloaber wird 
	node_colors = []
	for n in node_ids:
		tags = graph.nodes[n]["tags"]
		node_colors.append(visit_type_color(tags))

	if selected_id and selected_id in id_set:
		node_sizes = [
			size * 2.2 if n == selected_id else size
			for n, size in zip(node_ids, node_sizes)
		]

	node_symbols = []
	for n in node_ids:
		symbol = transition_symbol(graph.nodes[n]["core"])
		if graph.nodes[n]["cached"] and not symbol.endswith("-open"):
			symbol += CACHED_SYMBOL_SUFFIX
		node_symbols.append(symbol)

	node_line_colors = []
	node_line_widths = []
	for n in node_ids:
		node = graph.nodes[n]
		qualifiers = [q.upper() for q in node["qualifiers"]]

		if node["is_error"]:
			node_line_colors.append(ERROR_BORDER_COLOR)
		else:
			node_line_colors.append("#888888")

		if any("ADDRESS_BAR" in q for q in qualifiers):
			node_line_widths.append(ADDRESS_BAR_BORDER_WIDTH)
		else:
			node_line_widths.append(NORMAL_BORDER_WIDTH)

	hover = [
		f"""<b>{graph.nodes[n]["title"][:60]}</b><br>{str(graph.nodes[n]["time"])[11:16]} · {transition_label(graph.nodes[n]["core"])}"""
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
				line=dict(color=node_line_colors, width=node_line_widths),
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
