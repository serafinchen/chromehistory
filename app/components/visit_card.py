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
                        f"response_code: {row['response_code']}"
                        if row.get("response_code") is not None
                        else "No response_code",
                        className="cache_visit",
                  ),

                  html.Div(
                        f"content_type: {row['content_type']}"
                        if row.get("content_type")
                        else "No content_type",
                        className="cache_visit",
                  ),

                  html.Div(
                        f"content_language: {row['content_language']}"
                        if row.get("content_language")
                        else "No content_language",
                        className="cache_visit",
                  ),

                  html.Div(
                        f"is_probably_personalized: {row['is_probably_personalized']}",
                        className="cache_visit",
                  ),

                  html.Div(
                        f"is_no_store: {row['is_no_store']}",
                        className="cache_visit",
                  ),

                  html.Div(
                        f"age: {row['age']}"
                        if row.get("age") is not None
                        else "No age",
                        className="cache_visit",
                  ),

                  html.Div(
                        f"last_modified: {row['last_modified']}"
                        if row.get("last_modified")
                        else "No last_modified",
                        className="cache_visit",
                  ),

                  html.Div(
                        f"content_length: {row['content_length']} bytes"
                        if row.get("content_length") is not None
                        else "No content_length",
                        className="cache_visit",
                  ),

                  html.Div(
                        f"domain_asset_count: {row['domain_asset_count']}",
                        className="cache_visit",
                  ),

                  html.Div(
                        f"domain_total_bytes: {row['domain_total_bytes']} bytes",
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
                        f"title: {row['title'][:70]}"
                        if row.get("title")
                        else "No title",
                        className="history_visit",
                  ),

                  html.Div(
                        f"domain: {row['domain']}"
                        if row.get("domain")
                        else "No domain",
                        className="history_visit",
                              ),

                  html.Div(
                        f"url: {row['url'][:70]}"
                        if row.get("url")
                        else "No url",
                        className="history_visit",
                  ),                              

                  html.Div(
                        f"ID: {row['rec_id']}" 
                        if row.get("rec_id") is not None 
                        else "No rec_id",
                        className="history_visit",
                  ),

                  html.Div(
                        f"visit_time: {row['visit_time']}"
                        if row.get("visit_time")
                        else "No Visit Time",
                        className="history_visit",
                  ),

                  html.Div(
                        f"duration: {duration}s",
                        className="history_visit",
                  ),

                  html.Div(
                        f"from_visit_id: {row['from_visit_id']}"
                        if row.get("from_visit_id") is not None
                        else "No from_visit_id",
                        className="history_visit",
                  ),

                  html.Div(
                        f"opener_visit_id: {row['opener_visit_id']}"
                        if row.get("opener_visit_id") is not None
                        else "No opener_visit_id",
                        className="history_visit",
                  ),

                  html.Div(
                        f"transition_core / transition_qualifier: {row['transition_core']} / {row['transition_qualifier']}"
                        if row.get("transition_core")
                        else "No transition_core / transition_qualifier",
                        className="history_visit",
                  ),

                  html.Div("Cache Data with the same URL", className="cache-header",),

                  *cache_children,

                  
            ]
      )
