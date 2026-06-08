import dash
from dash import html, dcc, Input, Output, callback
from data import load_df
from components.timeline import build_timeline
from app.analytics import intent_color

df = load_df()

dash.register_page(__name__, path="/")

layout = html.Div([
      html.H1("Timeline"),

      dcc.Slider(
            id="intent-threshold",
            min=-15, max=15, step=0.5, value=-15
      ),

      dcc.Graph(id="timeline")
])


@callback(
      Output("timeline", "figure"),
      Input("intent-threshold", "value")
)
def update(thresh):
      d = df[df["intent_score"] >= thresh]
      return build_timeline(d)
