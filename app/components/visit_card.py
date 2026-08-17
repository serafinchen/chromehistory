from dash import html

from app.mapping import MatchType

def format_duration(seconds):
      if seconds is None: return "-"

      seconds = float(seconds)

      if seconds < 60: return f"{seconds:.1f}s"

      minutes = seconds / 60

      if minutes < 60: return f"{minutes:.1f}m"

      hours = minutes / 60

      return f"{hours:.1f}h"


def make_visit_card(row, role="active", html_content=None):

      duration = format_duration(
            row.get("duration", 0)
      )
      cache_children = []

      if row["match_type"] != MatchType.NONE:
            cache_children = [
                  html.Div(
                        f"RESPONSE CODE: {row['response_code']}"
                        if row.get("response_code") is not None
                        else "No Response Code",
                        className="cache_visit",
                  ),

                  html.Div(
                        f"CONTENT TYPE: {row['content_type']}"
                        if row.get("content_type")
                        else "No Content Type",
                        className="cache_visit",
                  ),

                  html.Div(
                        f"CONTENT LANGUAGE: {row['content_language']}"
                        if row.get("content_language")
                        else "No Content Language",
                        className="cache_visit",
                  ),

                  html.Div(
                        f"PERSONALIZED: {row['is_probably_personalized']}",
                        className="cache_visit",
                  ),

                  html.Div(
                        f"NO STORE: {row['is_no_store']}",
                        className="cache_visit",
                  ),

                  html.Div(
                        f"AGE: {row['age']}"
                        if row.get("age") is not None
                        else "No Age",
                        className="cache_visit",
                  ),

                  html.Div(
                        f"LAST MODIFIED: {row['last_modified']}"
                        if row.get("last_modified")
                        else "No Last Modified",
                        className="cache_visit",
                  ),

                  html.Div(
                        f"CONTENT LENGTH: {row['content_length']} bytes"
                        if row.get("content_length") is not None
                        else "No Content Length",
                        className="cache_visit",
                  ),

                  html.Div(
                        f"DOMAIN ASSET COUNT: {row['domain_asset_count']}",
                        className="cache_visit",
                  ),

                  html.Div(
                        f"DOMAIN TOTAL BYTES: {row['domain_total_bytes']} bytes",
                        className="cache_visit",
                  ),
            ]
            if html_content:
                  cache_children.append(
                        html.Details(
                              className="cache_html_details",
                              children=[
                                    html.Summary(
                                          "RENDERED HTML",
                                          className="cache_html_toggle",
                                    ),
                                    html.Iframe(
                                          srcDoc=html_content,
                                          sandbox="allow-same-origin",
                                          className="cache_html_frame",
                                          style={
                                                "width": "100%",
                                                "height": "500px",
                                                "border": "1px solid #444",
                                                "marginTop": "8px",
                                          },
                                    ),
                              ],
                        )
                  )
      else:
            cache_children = [
                  html.Div(
                        "No cache data found",
                        className="cache_visit cache_none",
                  )
            ]

      return html.Div(
            className=f"visit-card {role}",

            id={
                  "type": "visit-card",
                  "index": int(row["rec_id"])
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
                        f"ID: {row['rec_id']}" 
                        if row.get("rec_id") is not None 
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
                        f"DURATION: {duration}s",
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

                  html.Div("Cache Data with the same URL", className="cache-header",),

                  *cache_children,

                  
            ]
      )
