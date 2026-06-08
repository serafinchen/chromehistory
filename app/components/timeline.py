import plotly.graph_objects as go
from analytics import intent_color_vec


def build_timeline(df):
      fig = go.Figure()

      fig.add_trace(go.Scatter(
            x=df["visit_time_dt"],
            y=df["intent_score"],
            mode="markers+lines",
            marker=dict(
                  color=intent_color_vec(df["intent_score"]),
                  size=8
            ),
            customdata=df["visit_id"]
      ))

      fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False
      )

      return fig