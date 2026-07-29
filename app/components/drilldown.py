import pandas as pd
from dash import html

from app.components.visit_card import make_visit_card


def empty_drilldown():
      return html.Div(
            className="empty-state",
            children=[
                  html.Div("📄", className="empty-icon"),
                  html.Div(
                  "Select a visit to inspect its navigation.",
                  className="empty-text",
                  ),
            ],
      )


def build_drilldown(df, visit_id):

      if visit_id is None:
            return empty_drilldown(), [], "select a visit"

      row_df = df[df["visit_id"] == visit_id]

      if row_df.empty:
            return html.Div("Visit not found"), [], "-"

      row = row_df.iloc[0]

      ancestors = []

      current = row

      visited = set()

      while True:

            parent_id = current["from_visit_id"]

            if pd.isna(parent_id) or parent_id == 0:
                  parent_id = current["opener_visit_id"]

            if pd.isna(parent_id) or parent_id == 0:
                  break

            if parent_id in visited:
                  break

            visited.add(parent_id)

            parent = df[df["visit_id"] == parent_id]

            if parent.empty:
                  break

            parent = parent.iloc[0]

            ancestors.insert(0, parent)

            current = parent



      children = pd.concat(
            [
                  df[df["from_visit_id"] == visit_id],
                  df[df["opener_visit_id"] == visit_id],
            ]
      )

      children = (
            children
            .drop_duplicates("visit_id")
            .sort_values("visit_time_dt")
      )


      content = []

      if ancestors:

            content.append(
                  html.Div(
                  "Navigation Path",
                  className="section-label",
                  )
            )

            for ancestor in ancestors:

                  content.append(
                  make_visit_card(
                        ancestor,
                        "ancestor",
                  )
                  )

                  content.append(
                  html.Div(
                        "↓",
                        className="nav-arrow",
                  )
                  )

      content.append(
            html.Div(
                  "Selected Visit",
                  className="section-label",
            )
      )

      content.append(
            make_visit_card(
                  row,
                  "active",
            )
      )

      if not children.empty:

            content.append(
                  html.Div(
                  "Visited Next",
                  className="section-label",
                  )
            )

            for _, child in children.iterrows():

                  edge = "Opened in new tab"

                  if child["from_visit_id"] == visit_id:
                        edge = "Navigation"

                  content.append(
                  html.Div(
                        edge,
                        className="section-subtitle",
                  )
                  )

                  content.append(
                  html.Div(
                        "↓",
                        className="nav-arrow",
                  )
                  )

                  content.append(
                  make_visit_card(
                        child,
                        "child",
                  )
                  )

      duration = float(row["duration"])

      if duration < 60:
            duration_text = f"{duration:.1f} s"
      else:
            duration_text = f"{duration/60:.1f} min"

      stats = html.Div(

            className="stats-row",

            children=[

                  html.Div(

                  className="stat-box",

                  children=[

                        html.Div(
                              row["visit_time_dt"].strftime("%H:%M:%S"),
                              className="stat-val",
                        ),

                        html.Div(
                              "TIME",
                              className="stat-lbl",
                        ),
                  ],
                  ),

                  html.Div(

                  className="stat-box",

                  children=[

                        html.Div(
                              duration_text,
                              className="stat-val",
                        ),

                        html.Div(
                              "DURATION",
                              className="stat-lbl",
                        ),
                  ],
                  ),

                  html.Div(

                  className="stat-box",

                  children=[

                        html.Div(
                              f"S{row['session_id']}",
                              className="stat-val",
                        ),

                        html.Div(
                              "SESSION",
                              className="stat-lbl",
                        ),
                  ],
                  ),

                  html.Div(

                  className="stat-box",

                  children=[

                        html.Div(
                              row["domain"],
                              className="stat-val",
                        ),

                        html.Div(
                              "DOMAIN",
                              className="stat-lbl",
                        ),
                  ],
                  ),

                  html.Div(

                  className="stat-box",

                  children=[

                        html.Div(
                              str(len(children)),
                              className="stat-val",
                        ),

                        html.Div(
                              "CHILDREN",
                              className="stat-lbl",
                        ),
                  ],
                  ),

            ],
      )

      return (
            content,
            stats,
            f"Visit {visit_id}",
      )