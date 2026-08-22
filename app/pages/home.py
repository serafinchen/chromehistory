import dash
from dash import ALL, Input, Output, State, callback, ctx, dcc, html
from app.components.drilldown import build_drilldown, empty_drilldown
from app.components.nav_graph import build_nav_graph
from app.components.nav_graph_legend import build_legend
from app.data import dashboard_summary, load_df

dash.register_page(
      __name__,
      path="/"
)

df = load_df()

summary = dashboard_summary(df)

sessions = sorted(
      df["session_id"].unique()
)

latest_session = int(
      df.sort_values(
            "visit_time"
      ).iloc[-1]["session_id"]
)

layout = html.Div(
      id="root",
      children=[
            html.Div(
                  className="header",
                  children=[
                        html.Div(
                              className="header-title",
                              children=[
                                    "HISTORY",
                                    html.Span(
                                          " ANALYSER"
                                    )
                              ]
                        ),
                        html.Div(
                              className="header-meta",
                              children=(
                                    f"{summary['total_visits']} visits • "
                                    f"{summary['total_sessions']} sessions"
                              )
                        )
                  ]
            ),
            html.Div(
                  className="controls",
                  children=[
                        dcc.Dropdown(
                              id="session-filter",
                              options=[
                                    {
                                          "label": "All Sessions",
                                          "value": -1
                                    }
                              ]
                              +
                              [
                                    {
                                          "label": f"Session {s}",
                                          "value": int(s)
                                    }
                                    for s in sessions
                              ],
                              value=latest_session,
                              clearable=False,
                              style={
                                    "width": "180px"
                              }
                        ),
                        
                  ]
            ),
            html.Div(
                  className="main",
                  children=[
                        html.Div(
                              className="panel-drilldown",
                              children=[
                                    html.Div(
                                          className="panel-header",
                                          children=[
                                                html.Span(
                                                      "VISIT DETAILS",
                                                      className="panel-title"
                                                ),
                                                html.Span(
                                                      id="drilldown-badge",
                                                      className="panel-badge",
                                                      children="select a visit"
                                                )
                                          ]
                                    ),
                                    html.Div(
                                          id="drilldown-content",
                                          className="drilldown-body",
                                          children=[
                                                empty_drilldown()
                                          ]
                                    ),
                              ]
                        ),
                                                html.Div(
                              className="panel",
                              children=[
                                    html.Div(
                                          className="panel-header",
                                          children=[
                                                html.Span(
                                                      "SESSION GRAPH",
                                                      className="panel-title"
                                                ),
                                                html.Span(
                                                      id="graph-badge",
                                                      className="panel-badge"
                                                )
                                          ]
                                    ),
                                    html.Div(
                                          className="graph-with-legend",
										style={
											"display": "flex",
											"flexDirection": "row",
											"gap": "12px",
											"flex": "1 1 auto",
											"minHeight": 0
										},
                                          children=[
                                                dcc.Graph(
                                                      id="nav-graph",
                                                      config={
                                                            "displayModeBar": False
                                                      },
                                                      style={
                                                            "flex": "1 1 auto",
                                                            "minWidth": 0,
                                                            "height": "100%"
                                                      }
                                                ),
                                                build_legend()
                                          ]
                                    )
                              ]
                        )
                  ]
            ),
            dcc.Store(
                  id="selected-visit-id",
                  data=int(
                        df.sort_values(
                              "visit_time"
                        ).iloc[-1]["rec_id"]
                  )
            )
      ]
)


@callback(
      Output(
            "selected-visit-id",
            "data"
      ),
      Input(
            {
                  "type": "visit-card",
                  "id": ALL
            },
            "n_clicks"
      ),
      State(
            {
                  "type": "visit-card",
                  "id": ALL
            },
            "id"
      ),
      prevent_initial_call=True
)
def select_card(clicks, id):

      triggered = ctx.triggered_id

      if not triggered:
            return None

      return triggered["id"]


@callback(
      Output(
            "selected-visit-id",
            "data",
            allow_duplicate=True
      ),
      Input(
            "nav-graph",
            "clickData"
      ),
      prevent_initial_call=True
)
def graph_click(data):
      if not data or not data.get("points"):
            return None

      return data["points"][0]["customdata"]

@callback(
      Output(
            "nav-graph",
            "figure"
      ),
      Output(
            "graph-badge",
            "children"
      ),
      Input(
            "session-filter",
            "value"
      ),
      Input(
            "selected-visit-id",
            "data"
      )
)
def update_graph(
      session,
      selected,
      limit=500
):
      filtered = df.copy()

      if session != -1:
            filtered = filtered[
                  filtered.session_id == session
            ]

      filtered = (
            filtered
            .sort_values("visit_time")
            .head(limit)
      )

      fig = build_nav_graph(
            filtered,
            selected
      )

      return (
            fig,
            f"{len(filtered)} visits"
      )

@callback(
      Output(
            "drilldown-content",
            "children"
      ),
      Output(
            "drilldown-badge",
            "children"
      ),
      Input(
            "selected-visit-id",
            "data"
      )
)
def update_drilldown(rec_id):
      return build_drilldown(df, rec_id)
