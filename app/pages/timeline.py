import dash
import plotly.graph_objects as go
from dash import Input, Output, callback, callback_context, dcc, html

from app.components.drilldown import build_drilldown, empty_drilldown
from app.components.nav_graph import build_nav_graph, build_visit_graph
from app.components.timeline import build_timeline_figure
from app.data import dashboard_summary, filter_visits, load_df

dash.register_page(__name__, path="/")

df = load_df()
summary = dashboard_summary(df)
last_session_id = int(df["session_id"].max()) if not df.empty else -1


layout = html.Div(id="root", children=[
      html.Div(className="header", children=[
            html.Div(className="header-title", children=[
                  "CHROME", html.Span(" HISTORY")
            ]),
            html.Div(className="header-meta", children=[
                  (
                        f"{summary['total_visits']} visits - "
                        f"{summary['total_sessions']} sessions"
                  )
            ]),
      ]),

      html.Div(className="controls", children=[
            html.Span("Session", className="ctrl-label"),
            dcc.Dropdown(
                  id="session-filter",
                  options=[{"label": "All sessions", "value": -1}]
                  + [
                        {"label": f"Session {session}", "value": session}
                        for session in sorted(df["session_id"].unique())
                  ],
                  value=last_session_id,
                  clearable=False,
                  style={"width": "160px", "fontSize": "12px"},
            ),
      ]),

      html.Div(className="main", children=[
            html.Div(className="panel", children=[
                  html.Div(className="panel-header", children=[
                        html.Span("TIMELINE", className="panel-title"),
                        html.Span(id="timeline-badge", className="panel-badge"),
                  ]),
                  html.Div(className="panel-body", children=[
                        dcc.Graph(
                              id="timeline-graph",
                              style={"height": "100%"},
                              config={"displayModeBar": False},
                        ),
                  ]),
            ]),

            html.Div(className="panel-drilldown", children=[
                  html.Div(className="panel-header", children=[
                        html.Span("DRILL-DOWN", className="panel-title"),
                        html.Span("click a node", className="panel-badge", id="drilldown-badge"),
                  ]),
                  html.Div(
                        className="drilldown-body",
                        id="drilldown-content",
                        children=[empty_drilldown()],
                  ),
                  html.Div(className="stats-row", id="drilldown-stats"),
            ]),

            html.Div(className="panel", children=[
                  html.Div(className="panel-header", children=[
                        html.Span("NAVIGATION GRAPH", className="panel-title"),
                        html.Span(id="graph-badge", className="panel-badge"),
                  ]),
                  html.Div(className="panel-body", children=[
                        dcc.Graph(
                              id="nav-graph",
                              style={"height": "100%"},
                              config={"displayModeBar": False},
                        ),
                  ]),
            ]),
      ]),

      dcc.Store(id="selected-visit-id"),
])


@callback(
      Output("timeline-graph", "figure"),
      Output("timeline-badge", "children"),
      Input("session-filter", "value"),
)
def update_timeline(session_id):
      filtered = filter_visits(df, session_id)
      if filtered.empty:
            return go.Figure(), "0 visits"

      return build_timeline_figure(filtered), f"{len(filtered)} visits"


@callback(
      Output("nav-graph", "figure"),
      Output("graph-badge", "children"),
      Input("session-filter", "value"),
      Input("selected-visit-id", "data"),
)
def update_nav_graph(session_id, selected_id):
      filtered = filter_visits(df, session_id)
      if filtered.empty:
            return go.Figure(), "0 nodes"

      graph, _ = build_visit_graph(filtered)
      if len(graph.nodes) == 0:
            return go.Figure(), "0 nodes"

      return build_nav_graph(filtered, selected_id), f"{len(graph.nodes)} nodes - {len(graph.edges)} edges"


@callback(
      Output("selected-visit-id", "data"),
      Input("timeline-graph", "clickData"),
      Input("nav-graph", "clickData"),
)
def store_selected(timeline_click, graph_click):
      ctx = callback_context
      if not ctx.triggered:
            return None

      trigger = ctx.triggered[0]["prop_id"]
      click = timeline_click if "timeline" in trigger else graph_click
      if not click:
            return None

      points = click.get("points", [])
      if not points:
            return None

      customdata = points[0].get("customdata")
      return int(customdata) if customdata is not None else None


@callback(
      Output("drilldown-content", "children"),
      Output("drilldown-stats", "children"),
      Output("drilldown-badge", "children"),
      Input("selected-visit-id", "data"),
)
def update_drilldown(visit_id):
      return build_drilldown(df, visit_id)
