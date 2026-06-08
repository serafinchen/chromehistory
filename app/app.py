from dash import Dash, html, dcc
import pandas as pd
from loader import load_history, load_cache
from history import normalize, PROFILE_PATH, CACHE_PATHS
from analytics import add_sessions
from components.timeline import build_timeline
from components.nav_graph import build_nav_graph


history_raw = load_history(PROFILE_PATH)
cache_data = load_cache(CACHE_PATHS["chrome"])

visits = normalize(history_raw, cache_data)


df = pd.DataFrame([v.__dict__ for v in visits])
df["visit_time_dt"] = pd.to_datetime(df["visit_time"])
df = add_sessions(df)

app = Dash(__name__, title="History Analyser")

app.layout = html.Div(style="style.css"[
      dcc.Graph(id="timeline", figure=build_timeline(df)),
      dcc.Graph(id="graph", figure=build_nav_graph(None))
])

if __name__ == "__main__":
      app.run(debug=True)
      