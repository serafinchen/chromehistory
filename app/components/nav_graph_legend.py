import base64

from dash import html

from app.components.nav_graph_style import (
	CACHED_LABEL,
	EDGE_STYLE,
	ERROR_BORDER_COLOR,
	ERROR_LABEL,
	FRESH_LABEL,
	TRANSITION_LABELS,
	TRANSITION_SYMBOLS,
)

BG = "#1f2130"
FG = "#8f93b3"
FG_DIM = "#555878"
FONT = "Space Mono, monospace"

_ICON_SIZE = 18


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


def _symbol_icon(symbol, color=FG, filled=True):

	s = _ICON_SIZE
	c = s / 2

	base_open = symbol.endswith("-open")
	name = symbol.replace("-open", "")

	fill = color if (filled and not base_open) else "none"
	stroke = color
	sw = "1.5" if name in ("star", "hourglass") else "2"

	if name == "circle":
		inner = f'<circle cx="{c}" cy="{c}" r="{c - 2}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" />'
	elif name == "diamond":
		pts = f"{c},2 {s - 2},{c} {c},{s - 2} 2,{c}"
		inner = f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" />'
	elif name == "square":
		inner = f'<rect x="3" y="3" width="{s - 6}" height="{s - 6}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" />'
	elif name == "star":
		pts = "9,1 11,7 17,7 12,11 14,17 9,13 4,17 6,11 1,7 7,7"
		inner = f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" />'
	elif name == "triangle-up":
		pts = f"{c},2 {s - 2},{s - 2} 2,{s - 2}"
		inner = f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" />'
	elif name == "pentagon":
		pts = "9,1 17,7 14,17 4,17 1,7"
		inner = f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" />'
	elif name == "hexagon":
		pts = "5,2 13,2 17,9 13,16 5,16 1,9"
		inner = f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" />'
	elif name == "hourglass":
		pts = "3,2 15,2 3,16 15,16"
		inner = f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" />'
	else:
		inner = f'<circle cx="{c}" cy="{c}" r="{c - 2}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" />'

	return _svg_img(inner)


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
		_row(_symbol_icon(TRANSITION_SYMBOLS[core]), TRANSITION_LABELS[core])
		for core in TRANSITION_SYMBOLS
	]

	cache_rows = [
		_row(_symbol_icon("circle", filled=True), FRESH_LABEL),
		_row(_symbol_icon("circle", filled=False), CACHED_LABEL),
	]

	border_rows = [
		_row(
			_symbol_icon("circle", color=ERROR_BORDER_COLOR, filled=False),
			ERROR_LABEL,
		),
	]

	edge_rows = [
		_row(_edge_icon("#888888"), "lane"),
		_row(_edge_icon(**EDGE_STYLE["redirect"]), "redirect"),
		_row(_edge_icon(**EDGE_STYLE["back_forward"]), "back_forward"),
		_row(_edge_icon(**EDGE_STYLE["tab"]), "tab"),
	]

	return html.Div(
		[
			_section("Transition", transition_rows),
			_section("Edges/Relationships", edge_rows),
			_section("Cache-Status", cache_rows),
			_section("Border", border_rows),
		],
		style={
			"backgroundColor": BG,
			"padding": "14px 16px",
			"borderRadius": "8px",
			"fontFamily": FONT,
			"width": "260px",
		},
	)
