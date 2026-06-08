import pandas as pd
from app.history import normalize, PROFILE_PATH, CACHE_PATHS
from app.analytics import add_sessions
from dataclasses import asdict
from urllib.parse import urlparse
from app.loader import load_history, load_cache

def load_df():
      history_raw = load_history(PROFILE_PATH)
      cache_data = load_cache(CACHE_PATHS["chrome"])
      visits = normalize(history_raw, cache_data)

      df = pd.DataFrame([asdict(v) for v in visits])
      df["visit_time_dt"] = pd.to_datetime(df["visit_time"])
      df = add_sessions(df)

      df = df.sort_values("visit_time_dt").reset_index(drop=True)
      return df