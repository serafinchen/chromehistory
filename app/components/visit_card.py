from dash import html

from app.analytics import intent_color


def make_visit_card(row, role="active"):
      score = row["intent_score"]
      color = intent_color(score)
      duration = row["duration"]
      duration_label = f"{duration:.1f}s" if duration < 60 else f"{duration / 60:.1f}m"

      tags = []
      transition_core = row["transition_core"]
      if isinstance(transition_core, list) and transition_core:
            for transition in transition_core[:2]:
                  tags.append(html.Span(transition, className="vc-tag hi"))
      elif isinstance(transition_core, str) and transition_core:
            tags.append(html.Span(transition_core, className="vc-tag hi"))

      if row.get("is_no_store"):
            tags.append(html.Span("NO-STORE", className="vc-tag warn"))
      if row.get("is_personalized"):
            tags.append(html.Span("AUTH", className="vc-tag warn"))

      response_code = row.get("response_code")
      if response_code and response_code not in (200, 304, None):
            tags.append(html.Span(f"HTTP {response_code}", className="vc-tag danger"))

      tags.append(html.Span(duration_label, className="vc-tag"))
      tags.append(html.Span(row["visit_time"][11:19], className="vc-tag"))

      return html.Div(
            className=f"visit-card {role}",
            id={"type": "visit-card", "index": int(row["visit_id"])},
            children=[
                  html.Div(f"{score:+.1f}", className="vc-score", style={"color": color}),
                  html.Div(row["title"][:60], className="vc-title"),
                  html.Div(row["url"][:70], className="vc-url"),
                  html.Div(className="vc-meta", children=tags),
            ],
      )
