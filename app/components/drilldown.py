import pandas as pd
from dash import html

from app.analytics import intent_color
from app.components.visit_card import make_visit_card


def empty_drilldown():
      return html.Div(className="empty-state", children=[
            html.Div("o", className="empty-icon"),
            html.Div(
                  "Click any point in the timeline\nor graph to inspect the navigation chain.",
                  className="empty-text",
            ),
      ])


def build_drilldown(df, visit_id):
      if visit_id is None:
            return empty_drilldown(), [], "click a node"

      row_q = df[df["visit_id"] == visit_id]
      if row_q.empty:
            return html.Div("Visit not found"), [], "-"

      row = row_q.iloc[0]

      ancestors = []
      current = row
      for _ in range(5):
            parent_id = current["from_visit_id"] or current["opener_visit_id"]
            if not parent_id or parent_id == 0:
                  break

            parent = df[df["visit_id"] == parent_id]
            if parent.empty:
                  break

            ancestors.insert(0, parent.iloc[0])
            current = parent.iloc[0]

      children_from = df[df["from_visit_id"] == visit_id]
      children_opener = df[df["opener_visit_id"] == visit_id]
      children = pd.concat([children_from, children_opener]).drop_duplicates("visit_id")
      children = children.sort_values("visit_time").head(8)

      content = []
      if ancestors:
            content.append(html.Div("ancestors", className="section-label"))
            for ancestor in ancestors:
                  content.append(make_visit_card(ancestor, "ancestor"))
                  content.append(html.Div("v", className="nav-arrow"))

      content.append(html.Div("selected", className="section-label"))
      content.append(make_visit_card(row, "active"))

      if not children.empty:
            content.append(html.Div("children", className="section-label"))
            for _, child in children.iterrows():
                  content.append(html.Div("v", className="nav-arrow"))
                  content.append(make_visit_card(child, "child"))

      score = row["intent_score"]
      duration = row["duration"]
      session = row["session_id"]

      stats = html.Div(className="stats-row", children=[
            html.Div(className="stat-box", children=[
                  html.Div(
                        f"{score:+.1f}",
                        className="stat-val",
                        style={"color": intent_color(score)},
                  ),
                  html.Div("INTENT", className="stat-lbl"),
            ]),
            html.Div(className="stat-box", children=[
                  html.Div(
                        f"{duration:.0f}s" if duration < 60 else f"{duration / 60:.1f}m",
                        className="stat-val",
                  ),
                  html.Div("DURATION", className="stat-lbl"),
            ]),
            html.Div(className="stat-box", children=[
                  html.Div(f"S{session}", className="stat-val"),
                  html.Div("SESSION", className="stat-lbl"),
            ]),
            html.Div(className="stat-box", children=[
                  html.Div(str(len(children)), className="stat-val"),
                  html.Div("CHILDREN", className="stat-lbl"),
            ]),
      ])

      return content, stats, f"visit {visit_id}"
