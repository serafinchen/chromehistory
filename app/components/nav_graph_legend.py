import base64

from dash import html

from app.components.nav_graph_style import (
	EDGE_STYLE,
	TRANSITION_COLORS,
	TRANSITION_LABELS,
	NORMAL_BORDER_WIDTH,
	ADDRESS_BAR_BORDER_WIDTH,
)

BG = "#1f2130"
FG = "#8f93b3"
FG_DIM = "#555878"
FONT = "Space Mono, monospace"

_ICON_SIZE = 18

def _color_icon(color):
	s = _ICON_SIZE
	c = s / 2

	inner = (
		f'<circle cx="{c}" cy="{c}" r="{c - 3}" '
		f'fill="{color}" stroke="{color}" stroke-width="1.5" />'
	)

	return _svg_img(inner)


def _svg_img(inner, size=_ICON_SIZE):
	svg = (
		f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" '
		f'width="{size}" height="{size}">{inner}</svg>'
	)

	b64 = base64.b64encode(svg.encode("utf-8")).decode("ascii")

	return html.Img(
		src=f"data:image/svg+xml;base64,{b64}",
		style={
			"width": f"{size}px",
			"height": f"{size}px",
			"flexShrink": 0,
			"display": "block",
		},
	)


def _dash_to_svg(dash):
	return {
		None: "",
		"dash": "5,3",
		"dot": "1,3",
		"longdash": "8,3",
		"solid": "",
	}.get(dash, "")


def _edge_icon(color, dash=None, width=2):
	s = _ICON_SIZE
	dasharray = _dash_to_svg(dash)
	dash_attr = f'stroke-dasharray="{dasharray}"' if dasharray else ""

	inner = (
		f'<line x1="1" y1="{s / 2}" x2="{s - 1}" y2="{s / 2}" '
		f'stroke="{color}" stroke-width="{width}" {dash_attr} />'
	)

	return _svg_img(inner)

def _node_border_icon(width):
	s = _ICON_SIZE
	c = s / 2

	inner = (
		f'<circle cx="{c}" cy="{c}" r="{c - 3}" '
		f'fill="none" stroke="{FG}" stroke-width="{width}" />'
	)

	return _svg_img(inner)


def _row(icon, label):
	return html.Div(
		[
			html.Div(icon, style={"marginRight": "10px", "display": "flex", "alignItems": "center"}),
			html.Span(label, style={"fontSize": "12px", "color": FG}),
		],
		style={"display": "flex", "alignItems": "center", "marginBottom": "6px"},
	)


def _section(title, rows):
	return html.Div(
		[
			html.Div(
				title,
				style={
					"fontSize": "11px",
					"color": FG_DIM,
					"textTransform": "uppercase",
					"letterSpacing": "0.05em",
					"marginBottom": "8px",
					"marginTop": "14px",
				},
			),
			*rows,
		]
	)


def build_legend():

	transition_rows = [
		_row(
			_color_icon(TRANSITION_COLORS[core]),
			TRANSITION_LABELS.get(core, core),
		)
		for core in TRANSITION_COLORS
	]

	edge_rows = [
		_row(_edge_icon("#888888"), "other"),
		_row(_edge_icon(**EDGE_STYLE["redirect"]), "redirect"),
		_row(_edge_icon(**EDGE_STYLE["back_forward"]), "back_forward"),
		_row(_edge_icon(**EDGE_STYLE["tab"]), "tab"),
	]

	border_rows = [
		_row(_node_border_icon(NORMAL_BORDER_WIDTH), "normal"),
		_row(_node_border_icon(ADDRESS_BAR_BORDER_WIDTH), "via address bar"),
	]

	return html.Div(
		[
			_section("Transition", transition_rows),
			_section("Edges / Relationships", edge_rows),
			_section("Node border", border_rows),
		],
		style={
			"backgroundColor": BG,
			"padding": "14px 16px",
			"borderRadius": "8px",
			"fontFamily": FONT,
			"flex": "0 0 260px",
			"width": "260px",
			"height": "100%",
			"minHeight": 0,
			"overflowY": "auto",
			"overflowX": "hidden",
		},
	)
