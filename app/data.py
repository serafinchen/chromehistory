from dataclasses import asdict
from urllib.parse import urlparse

import pandas as pd

from app.analytics import add_sessions
from app.history import CACHE_PATHS, PROFILE_PATH, normalize
from app.loader import load_cache, load_history


def load_df():
      history_raw = load_history(PROFILE_PATH)
      cache_data = load_cache(CACHE_PATHS["chrome"])
      visits = normalize(history_raw, cache_data)

      df = pd.DataFrame([asdict(v) for v in visits])
      df["domain"] = df["url"].apply(lambda u: urlparse(u).netloc)
      df["visit_time_dt"] = pd.to_datetime(df["visit_time"])
      df["duration"] = df["visit_duration_seconds"]
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
            "high_intent": len(df[df["intent_score"] >= 5])
      }
