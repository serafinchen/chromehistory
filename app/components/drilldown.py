import pandas as pd
from dash import html
from app.cache import get_cached_body
from app.components.visit_card import make_visit_card
from app.data import get_profile

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


def _load_html_for_row(row):
      if not row.get("is_html") or not row.get("raw_key"):
            return None
      body = get_cached_body(get_profile(), row["raw_key"])
      if body is None:
            return None
      try:
            return body.decode("utf-8", errors="replace")
      except Exception:
            return None


def build_drilldown(df, visit_id):

      if visit_id is None:
            return empty_drilldown(), "select a visit"

      row_df = df[df["visit_id"] == visit_id]

      if row_df.empty:
            return html.Div("Visit not found"), "-"

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
                        html_content=_load_html_for_row(ancestor),
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
                  row,
                  "active",
                  html_content=_load_html_for_row(row),
            )
      )

      if not children.empty:

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
                        html_content=_load_html_for_row(child),
                  )
                  )


      return (
            content,
            f"Visit {visit_id}",
      )
