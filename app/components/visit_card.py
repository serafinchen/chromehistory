from dash import html


def transition_tags(row):

      tags = []

      transition = row.get("transition_core")

      if isinstance(transition, str) and transition:
            tags.append(transition)

      if row.get("opener_visit_id"):
            tags.append("NEW_TAB")

      elif row.get("from_visit_id"):
            tags.append("LINK")

      else:
            tags.append("DIRECT")

      return tags


def format_duration(seconds):

      if seconds is None:
            return "-"

      seconds = float(seconds)

      if seconds < 60:
            return f"{seconds:.1f}s"

      minutes = seconds / 60

      if minutes < 60:
            return f"{minutes:.1f}m"

      hours = minutes / 60

      return f"{hours:.1f}h"


def make_visit_card(row, role="active"):

      duration = format_duration(
            row.get("duration", 0)
      )

      tags = []

      for transition in transition_tags(row):

            tags.append(

                  html.Span(
                  transition,
                  className="vc-tag hi",
                  )

            )

      if row.get("is_no_store"):

            tags.append(

                  html.Span(
                  "NO-STORE",
                  className="vc-tag warn",
                  )

            )


      if row.get("is_personalized"):

            tags.append(

                  html.Span(
                  "AUTH",
                  className="vc-tag warn",
                  )

            )


      response = row.get("response_code")

      if response and response not in (200, 304):

            tags.append(

                  html.Span(
                  f"HTTP {response}",
                  className="vc-tag danger",
                  )

            )

      tags.extend(

            [

                  html.Span(
                  duration,
                  className="vc-tag",
                  ),

                  html.Span(
                  row["visit_time_dt"].strftime("%H:%M:%S"),
                  className="vc-tag",
                  ),

                  html.Span(
                  f"S{row['session_id']}",
                  className="vc-tag",
                  ),

            ]

      )

      return html.Div(

            className=f"visit-card {role}",

            id={
                  "type": "visit-card",
                  "index": int(row["visit_id"])
            },

            children=[


                  html.Div(

                  row["title"][:70]
                  if row.get("title")
                  else "Untitled",

                  className="vc-title",

                  ),


                  html.Div(

                  row["domain"],

                  className="vc-domain",

                  ),


                  html.Div(

                  row["url"][:100],

                  className="vc-url",

                  ),


                  html.Div(

                  className="vc-meta",

                  children=tags,

                  ),

            ],

      )