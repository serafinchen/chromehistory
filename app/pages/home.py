import dash
from dash import ALL, Input, Output, State, callback, ctx, dcc, html
from datetime import datetime, timedelta
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
            "visit_time_dt"
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
                                    "BROWSER",
                                    html.Span(
                                          " SESSION EXPLORER"
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
                        dcc.DatePickerRange(
                              id="date-filter",
                              display_format="YYYY-MM-DD"
                        ),
                        dcc.Dropdown(
                              id="duration-filter",
                              options=[
                                    {
                                          "label": "All Durations",
                                          "value": -1
                                    },
                                    {
                                          "label": "> 10 sec",
                                          "value": 10
                                    },
                                    {
                                          "label": "> 30 sec",
                                          "value": 30
                                    },
                                    {
                                          "label": "> 60 sec",
                                          "value": 60
                                    },
                                    {
                                          "label": "> 5 min",
                                          "value": 300
                                    }
                              ],
                              value=-1,
                              clearable=False,
                              style={
                                    "width": "180px"
                              }
                        )
                  ]
            ),
            html.Div(
                  className="main",
                  children=[
                        html.Div(
                              className="panel",
                              children=[
                                    html.Div(
                                          className="panel-header",
                                          children=[
                                                html.Span(
                                                      "VISITS",
                                                      className="panel-title"
                                                ),
                                                html.Span(
                                                      id="table-count",
                                                      className="panel-badge"
                                                )
                                          ]
                                    ),
                                    html.Div(
                                          id="visit-list",
                                          className="panel-body"
                                    )
                              ]
                        ),
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
                                    html.Div(
                                          id="drilldown-stats",
                                          className="stats-row"
                                    )
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
                                                "height": "100%",
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
                              "visit_time_dt"
                        ).iloc[-1]["visit_id"]
                  )
            )
      ]
)


@callback(
      Output(
            "visit-list",
            "children"
      ),
      Output(
            "table-count",
            "children"
      ),
      Input(
            "session-filter",
            "value"
      ),
      Input(
            "duration-filter",
            "value"
      ),
      Input(
            "date-filter",
            "start_date"
      ),
      Input(
            "date-filter",
            "end_date"
      )
)
def update_visits(
      session,
      duration,
      start,
      end
):

      filtered = df.copy()

      if session != -1:
            filtered = filtered[
                  filtered.session_id == session
            ]

      if duration != -1:
            filtered = filtered[
                  filtered.duration >= duration
            ]

      if start:
            start_dt = datetime.fromisoformat(start)
            filtered = filtered[filtered.visit_time_dt >= start_dt]

      if end:
            end_dt = datetime.fromisoformat(end) + timedelta(days=1)
            filtered = filtered[filtered.visit_time_dt < end_dt]

      filtered = filtered.sort_values(
            "visit_time_dt",
            ascending=False
      )

      cards = []

      for _, row in filtered.iterrows():

            cards.append(
                  html.Div(
                        className="visit-card",
                        id={
                              "type": "visit-card",
                              "id": int(row.visit_id)
                        },
                        n_clicks=0,
                        children=[
                              html.Div(
                                    row.title,
                                    className="vc-title"
                              ),
                              html.Div(
                                    row.url,
                                    className="vc-url"
                              ),
                              html.Div(
                                    [
                                          html.Span(
                                                row.domain,
                                                className="vc-tag"
                                          ),
                                          html.Span(
                                                f"{row.duration:.1f}s",
                                                className="vc-tag hi"
                                          ),
                                          html.Span(
                                                f"Session {row.session_id}",
                                                className="vc-tag"
                                          )
                                    ],
                                    className="vc-meta"
                              )
                        ]
                  )
            )

      return (
            cards,
            f"{len(cards)} visits"
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
def select_card(
      clicks,
      ids
):

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
def graph_click(
      data
):

      if not data:
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
      domain=None,
      limit=500
):
      filtered = df.copy()

      if session != -1:
            filtered = filtered[
                  filtered.session_id == session
            ]

      if domain:
            filtered = filtered[
                  filtered.domain == domain
            ]

      filtered = (
            filtered
            .sort_values("visit_time_dt")
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
            "drilldown-stats",
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
def update_drilldown(
      visit_id
):

      return build_drilldown(
            df,
            visit_id
      )