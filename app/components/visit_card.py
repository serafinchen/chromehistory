from dash import html

def format_duration(seconds):
      if seconds is None: return "-"

      seconds = float(seconds)

      if seconds < 60: return f"{seconds:.1f}s"

      minutes = seconds / 60

      if minutes < 60: return f"{minutes:.1f}m"

      hours = minutes / 60

      return f"{hours:.1f}h"


def make_visit_card(row, role="active"):

      duration = format_duration(
            row.get("duration", 0)
      )

      return html.Div(
            className=f"visit-card {role}",

            id={
                  "type": "visit-card",
                  "index": int(row["visit_id"])
            },

            children=[
                  #History Dataclass
                  html.Div(
                        f"TITLE: {row['title'][:70]}"
                        if row.get("title")
                        else "No Title",
                        className="history_visit",
                  ),

                  html.Div(
                        f"DOMAIN: {row['domain']}"
                        if row.get("domain")
                        else "No Domain",
                        className="history_visit",
                              ),

                  html.Div(
                        f"URL: {row['url'][:70]}"
                        if row.get("url")
                        else "No URL",
                        className="history_visit",
                  ),                              

                  html.Div(
                        f"ID: {row['visit_id']}" 
                        if row.get("visit_id") is not None 
                        else "No ID",
                        className="history_visit",
                  ),

                  html.Div(
                        f"TIME: {row['visit_time']}"
                        if row.get("visit_time")
                        else "No Visit Time",
                        className="history_visit",
                  ),

                  html.Div(
                        f"DURATION: {row['visit_duration_seconds']}s"
                        if row.get("visit_duration_seconds") is not None
                        else "No Duration",
                        className="history_visit",
                  ),

                  html.Div(
                        f"FROM: {row['from_visit_id']}"
                        if row.get("from_visit_id") is not None
                        else "No Parent Visit",
                        className="history_visit",
                  ),

                  html.Div(
                        f"OPENER: {row['opener_visit_id']}"
                        if row.get("opener_visit_id") is not None
                        else "No Opener Visit",
                        className="history_visit",
                  ),

                  html.Div(
                        f"TRANSITION: {row['transition_core']} / {row['transition_qualifier']}"
                        if row.get("transition_core")
                        else "No Transition",
                        className="history_visit",
                  ),

                  html.Div(
                        f"INTENT: {row['intent_score']:.2f}"
                        if row.get("intent_score") is not None
                        else "No Intent Score",
                        className="history_visit",
                  ),

                  
            ]
      )
