import plotly.graph_objects as go

from app.analytics import intent_color_vec


def build_timeline_figure(df):
      if df.empty:
            return go.Figure()

      colors = intent_color_vec(df["intent_score"])
      sizes = (df["duration"].clip(0, 300) / 300 * 18 + 5).tolist()

      hover = [
            f"<b>{row['title'][:50]}</b><br>"
            f"{row['url'][:60]}<br>"
            f"Score: {row['intent_score']:+.2f} | {row['duration']:.1f}s<br>"
            f"Session {row['session_id']}"
            for _, row in df.iterrows()
      ]

      fig = go.Figure()
      fig.add_trace(go.Scatter(
            x=df["visit_time_dt"],
            y=df["intent_score"],
            mode="markers+lines",
            marker=dict(color=colors, size=sizes, line=dict(width=0)),
            line=dict(color="#1f2130", width=1),
            hovertext=hover,
            hoverinfo="text",
            customdata=df["visit_id"].tolist(),
      ))

      fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Space Mono", color="#555878", size=10),
            showlegend=False,
            margin=dict(l=40, r=16, t=16, b=40),
            xaxis=dict(gridcolor="#1a1c28", zeroline=False, showline=False),
            yaxis=dict(
                  gridcolor="#1a1c28",
                  zeroline=True,
                  zerolinecolor="#2a2d3e",
                  range=[-16, 16],
                  title="intent score",
            ),
            hovermode="closest",
            clickmode="event",
      )
      return fig


def build_timeline(df):
      return build_timeline_figure(df)
