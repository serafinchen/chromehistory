from dataclasses import asdict
from urllib.parse import urlparse

import pandas as pd
from ccl_chromium_reader import ChromiumProfileFolder

from app.analytics import add_sessions
from app.cache import load_cache_entries
from app.config import PROFILE_PATH
from app.history import load_history_entries
from app.mapping import MatchedVisit, match_history_with_cache

_profile_singleton: ChromiumProfileFolder | None = None

def get_profile() -> ChromiumProfileFolder:
      global _profile_singleton

      if _profile_singleton is None:
            _profile_singleton = ChromiumProfileFolder(PROFILE_PATH)

      return _profile_singleton

def _visit_to_row(v: MatchedVisit) -> dict:
      row = asdict(v.history)
      row.update(
            {
                  "match_type": v.match_type.value,
                  "response_code": v.response_code,
                  "content_type": v.content_type,
                  "content_language": v.content_language,
                  "is_probably_personalized": v.is_probably_personalized,
                  "is_no_store": v.is_no_store,
                  "age": v.age,
                  "raw_key": v.raw_key,
                  "is_html": v.is_html,
                  "last_modified": v.last_modified,
                  "content_length": v.content_length,
                  "domain_asset_count": v.domain_asset_count,
                  "domain_total_bytes": v.domain_total_bytes,
                  "is_error": v.is_error,
            }
      )
      return row


def load_df():
      profile = get_profile()
      history_entries = load_history_entries(PROFILE_PATH)
      cache_entries = load_cache_entries(profile)
      visits = match_history_with_cache(history_entries, cache_entries)

      df = pd.DataFrame([_visit_to_row(v) for v in visits])
      df["domain"] = df["url"].apply(lambda u: urlparse(u).netloc)
      df["visit_time_dt"] = pd.to_datetime(df["visit_time"])
      df["duration"] = df["visit_duration"]
      df = add_sessions(df)

      return df.sort_values("visit_time_dt").reset_index(drop=True)


def filter_visits(df, session_id):
      filtered = df
      if session_id != -1:
            filtered = filtered[filtered["session_id"] == session_id]
      return filtered


def dashboard_summary(df):

      return {
            "total_visits": len(df),
            "total_sessions": df["session_id"].nunique(),
      }
