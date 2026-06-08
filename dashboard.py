import dash
from dash import dcc, html, Input, Output, State, callback_context
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import networkx as nx
from urllib.parse import urlparse
import json

# ── Import your existing modules ──────────────────────────────────────────────
from history import load_history, load_cache, normalize, PROFILE_PATH, CACHE_PATHS
from graph import build_chrome_history_graph
from helpers import score_to_color

# ── Load data ─────────────────────────────────────────────────────────────────
print("Loading history...")
history_raw = load_history(PROFILE_PATH)
cache_data  = load_cache(CACHE_PATHS["chrome"])
visits      = normalize(history_raw, cache_data)
visits.sort(key=lambda v: v.visit_time)

df = pd.DataFrame([{
      "visit_id":               v.visit_id,
      "url":                    v.url,
      "domain":                 urlparse(v.url).netloc,
      "title":                  v.title,
      "visit_time":             v.visit_time,
      "duration":               v.visit_duration_seconds,
      "intent_score":           v.intent_score,
      "transition_core":        v.transition_core,
      "transition_qualifier":   v.transition_qualifier,
      "from_visit_id":          v.from_visit_id,
      "opener_visit_id":        v.opener_visit_id,
      "cached":                 v.cached,
      "content_type":           v.content_type,
      "is_personalized":        getattr(v, "is_personalized", False),
      "is_no_store":            getattr(v, "is_no_store", False),
      "response_code":          v.response_code,
      "asset_count":            getattr(v, "asset_count", 0),
      "total_bytes":            getattr(v, "total_bytes", 0),
} for v in visits])

df["visit_time_dt"] = pd.to_datetime(df["visit_time"])

# ── Color helpers ──────────────────────────────────────────────────────────────
def intent_color(score):
      if score >= 10:  return "#00ff9d"
      elif score >= 5: return "#7fff7f"
      elif score >= 2: return "#ffd700"
      elif score >= 0: return "#888ea8"
      elif score >= -5:return "#ff8c42"
      else:            return "#ff3d5a"

def intent_color_vec(scores):
      return [intent_color(s) for s in scores]

# ── Session segmentation ───────────────────────────────────────────────────────
SESSION_GAP = 30 * 60  # 30 min
df = df.sort_values("visit_time_dt").reset_index(drop=True)
session_ids = [0]
for i in range(1, len(df)):
      gap = (df.loc[i, "visit_time_dt"] - df.loc[i-1, "visit_time_dt"]).total_seconds()
      session_ids.append(session_ids[-1] + (1 if gap > SESSION_GAP else 0))
df["session_id"] = session_ids

# ── App ────────────────────────────────────────────────────────────────────────
app = dash.Dash(__name__, title="History Intelligence")

app.index_string = '''
<!DOCTYPE html>
<html>
<head>
    {%metas%}
    <title>{%title%}</title>
    {%favicon%}
    {%css%}
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

        :root {
            --bg:        #08090d;
            --surface:   #0f1117;
            --surface2:  #161820;
            --border:    #1f2130;
            --accent:    #00ff9d;
            --accent2:   #7b5cff;
            --danger:    #ff3d5a;
            --warn:      #ffd700;
            --text:      #e2e4ef;
            --muted:     #555878;
            --font-mono: 'Space Mono', monospace;
            --font-head: 'Syne', sans-serif;
        }

        html, body { height: 100%; background: var(--bg); color: var(--text); font-family: var(--font-mono); font-size: 13px; }

        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: var(--bg); }
        ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }

        #root { display: flex; flex-direction: column; height: 100vh; overflow: hidden; }

        /* ── Header ── */
        .header {
            display: flex; align-items: center; justify-content: space-between;
            padding: 12px 24px;
            border-bottom: 1px solid var(--border);
            background: var(--surface);
            flex-shrink: 0;
        }
        .header-title {
            font-family: var(--font-head);
            font-size: 18px; font-weight: 800; letter-spacing: -0.5px;
            color: var(--accent);
        }
        .header-title span { color: var(--text); }
        .header-meta { color: var(--muted); font-size: 11px; }

        /* ── Controls bar ── */
        .controls {
            display: flex; align-items: center; gap: 16px;
            padding: 10px 24px;
            border-bottom: 1px solid var(--border);
            background: var(--surface);
            flex-shrink: 0;
            flex-wrap: wrap;
        }
        .ctrl-label { color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: 1px; white-space: nowrap; }

        .dash-slider .rc-slider-rail    { background: var(--border); }
        .dash-slider .rc-slider-track   { background: var(--accent2); }
        .dash-slider .rc-slider-handle  { border-color: var(--accent2); background: var(--bg); }

        /* ── Main layout ── */
        .main {
            display: grid;
            grid-template-columns: 1fr 340px;
            grid-template-rows: 1fr 1fr;
            gap: 1px;
            flex: 1;
            overflow: hidden;
            background: var(--border);
        }

        .panel {
            background: var(--surface);
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }
        .panel-header {
            padding: 10px 16px 8px;
            border-bottom: 1px solid var(--border);
            display: flex; align-items: center; justify-content: space-between;
            flex-shrink: 0;
        }
        .panel-title {
            font-family: var(--font-head);
            font-size: 11px; font-weight: 600;
            text-transform: uppercase; letter-spacing: 2px;
            color: var(--muted);
        }
        .panel-badge {
            font-size: 10px; padding: 2px 8px;
            background: var(--surface2); border: 1px solid var(--border);
            border-radius: 2px; color: var(--accent);
        }
        .panel-body { flex: 1; overflow: hidden; position: relative; }

        /* ── Drilldown panel (right column, spans 2 rows) ── */
        .panel-drilldown {
            grid-row: 1 / 3;
            background: var(--surface);
            display: flex; flex-direction: column;
            overflow: hidden;
        }
        .drilldown-body {
            flex: 1; overflow-y: auto; padding: 12px 16px;
        }

        /* ── Visit cards ── */
        .visit-card {
            border: 1px solid var(--border);
            border-radius: 4px;
            padding: 10px 12px;
            margin-bottom: 8px;
            background: var(--surface2);
            cursor: pointer;
            transition: border-color 0.15s;
            position: relative;
        }
        .visit-card:hover { border-color: var(--accent2); }
        .visit-card.active { border-color: var(--accent); }
        .visit-card.ancestor { border-color: var(--accent2); opacity: 0.7; }
        .visit-card.child { border-color: var(--muted); opacity: 0.6; }

        .vc-score {
            position: absolute; top: 10px; right: 10px;
            font-size: 11px; font-weight: 700;
            font-family: var(--font-head);
        }
        .vc-title { font-size: 12px; font-weight: 700; color: var(--text); margin-bottom: 4px; padding-right: 40px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .vc-url   { font-size: 10px; color: var(--muted); margin-bottom: 6px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .vc-meta  { display: flex; gap: 8px; flex-wrap: wrap; }
        .vc-tag   { font-size: 10px; padding: 1px 6px; border-radius: 2px; background: var(--surface); border: 1px solid var(--border); color: var(--muted); }
        .vc-tag.hi { border-color: var(--accent); color: var(--accent); }
        .vc-tag.warn { border-color: var(--warn); color: var(--warn); }
        .vc-tag.danger { border-color: var(--danger); color: var(--danger); }

        .nav-arrow {
            text-align: center; color: var(--border); font-size: 18px;
            margin: 2px 0; user-select: none;
        }
        .section-label {
            font-size: 10px; text-transform: uppercase; letter-spacing: 1.5px;
            color: var(--muted); margin: 10px 0 6px;
        }

        /* ── Stats row ── */
        .stats-row {
            display: flex; gap: 1px;
            border-top: 1px solid var(--border);
            flex-shrink: 0;
        }
        .stat-box {
            flex: 1; padding: 8px 12px;
            background: var(--surface2);
            text-align: center;
        }
        .stat-val { font-family: var(--font-head); font-size: 16px; font-weight: 800; color: var(--accent); }
        .stat-lbl { font-size: 10px; color: var(--muted); margin-top: 2px; }

        .empty-state {
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            height: 100%; color: var(--muted); gap: 8px;
        }
        .empty-icon { font-size: 32px; }
        .empty-text { font-size: 11px; text-align: center; line-height: 1.6; }

        /* ── Plotly overrides ── */
        .js-plotly-plot .plotly { background: transparent !important; }
        .modebar { display: none !important; }
    </style>
</head>
<body>
    <div id="root">
        {%app_entry%}
    </div>
    <footer>
        {%config%}
        {%scripts%}
        {%renderer%}
    </footer>
</body>
</html>
'''

# ── Layout ─────────────────────────────────────────────────────────────────────
total_visits  = len(df)
total_sessions= df["session_id"].nunique()
high_intent   = len(df[df["intent_score"] >= 5])
anomalies     = len(df[(df["is_no_store"] == True) | (df["response_code"].isin([403, 404, 500]))])

app.layout = html.Div(id="root", children=[

      # Header
      html.Div(className="header", children=[
            html.Div(className="header-title", children=[
                  "HISTORY", html.Span(" INTELLIGENCE")
            ]),
            html.Div(className="header-meta", children=[
                  f"{total_visits} visits · {total_sessions} sessions · {high_intent} high-intent · {anomalies} anomalies"
            ]),
      ]),

      # Controls
      html.Div(className="controls", children=[
            html.Span("Intent threshold", className="ctrl-label"),
            dcc.Slider(
                  id="intent-threshold",
                  min=-15, max=15, step=0.5, value=-15,
                  marks={-15: "-15", -5: "-5", 0: "0", 5: "5", 15: "15"},
                  className="dash-slider",
                  tooltip={"placement": "top"},
                  updatemode="drag",
            ),
            html.Span("Session", className="ctrl-label"),
            dcc.Dropdown(
                  id="session-filter",
                  options=[{"label": f"All sessions", "value": -1}] +
                          [{"label": f"Session {s}", "value": s} for s in sorted(df["session_id"].unique())],
                  value=-1,
                  clearable=False,
                  style={"width": "160px", "fontSize": "12px"},
            ),
      ]),

      # Main grid
      html.Div(className="main", children=[

            # ── Top-left: Timeline ──────────────────────────────────────────
            html.Div(className="panel", children=[
                  html.Div(className="panel-header", children=[
                        html.Span("TIMELINE", className="panel-title"),
                        html.Span(id="timeline-badge", className="panel-badge"),
                  ]),
                  html.Div(className="panel-body", children=[
                        dcc.Graph(id="timeline-graph", style={"height": "100%"},
                                  config={"displayModeBar": False}),
                  ]),
            ]),

            # ── Right column: Drilldown ─────────────────────────────────────
            html.Div(className="panel-drilldown", children=[
                  html.Div(className="panel-header", children=[
                        html.Span("DRILL-DOWN", className="panel-title"),
                        html.Span("click a node", className="panel-badge", id="drilldown-badge"),
                  ]),
                  html.Div(className="drilldown-body", id="drilldown-content", children=[
                        html.Div(className="empty-state", children=[
                              html.Div("◎", className="empty-icon"),
                              html.Div("Click any point in the timeline\nor graph to inspect the navigation chain.", className="empty-text"),
                        ])
                  ]),
                  html.Div(className="stats-row", id="drilldown-stats"),
            ]),

            # ── Bottom-left: Graph ──────────────────────────────────────────
            html.Div(className="panel", children=[
                  html.Div(className="panel-header", children=[
                        html.Span("NAVIGATION GRAPH", className="panel-title"),
                        html.Span(id="graph-badge", className="panel-badge"),
                  ]),
                  html.Div(className="panel-body", children=[
                        dcc.Graph(id="nav-graph", style={"height": "100%"},
                                  config={"displayModeBar": False}),
                  ]),
            ]),
      ]),

      dcc.Store(id="selected-visit-id"),
])


# ── Helpers ────────────────────────────────────────────────────────────────────
def filter_df(intent_thresh, session_id):
      d = df[df["intent_score"] >= intent_thresh]
      if session_id != -1:
            d = d[d["session_id"] == session_id]
      return d


def make_visit_card(row, role="active"):
      score = row["intent_score"]
      col   = intent_color(score)
      dur   = row["duration"]
      dur_s = f"{dur:.1f}s" if dur < 60 else f"{dur/60:.1f}m"

      tags = []
      tc = row["transition_core"]
      if isinstance(tc, list) and tc:
            for t in tc[:2]:
                  tags.append(html.Span(t, className="vc-tag hi"))
      elif isinstance(tc, str) and tc:
            tags.append(html.Span(tc, className="vc-tag hi"))

      if row.get("is_no_store"):
            tags.append(html.Span("NO-STORE", className="vc-tag warn"))
      if row.get("is_personalized"):
            tags.append(html.Span("AUTH", className="vc-tag warn"))
      rc = row.get("response_code")
      if rc and rc not in (200, 304, None):
            tags.append(html.Span(f"HTTP {rc}", className="vc-tag danger"))
      tags.append(html.Span(dur_s, className="vc-tag"))
      tags.append(html.Span(row["visit_time"][11:19], className="vc-tag"))

      return html.Div(className=f"visit-card {role}",
            id={"type": "visit-card", "index": int(row["visit_id"])},
            children=[
                  html.Div(f"{score:+.1f}", className="vc-score", style={"color": col}),
                  html.Div(row["title"][:60], className="vc-title"),
                  html.Div(row["url"][:70],  className="vc-url"),
                  html.Div(className="vc-meta", children=tags),
            ])


# ── Callbacks ──────────────────────────────────────────────────────────────────

@app.callback(
      Output("timeline-graph", "figure"),
      Output("timeline-badge", "children"),
      Input("intent-threshold", "value"),
      Input("session-filter",   "value"),
)
def update_timeline(thresh, session_id):
      d = filter_df(thresh, session_id)
      if d.empty:
            return go.Figure(), "0 visits"

      colors = intent_color_vec(d["intent_score"])
      sizes  = (d["duration"].clip(0, 300) / 300 * 18 + 5).tolist()

      hover = [
            f"<b>{row['title'][:50]}</b><br>"
            f"{row['url'][:60]}<br>"
            f"Score: {row['intent_score']:+.2f} | {row['duration']:.1f}s<br>"
            f"Session {row['session_id']}"
            for _, row in d.iterrows()
      ]

      fig = go.Figure()
      fig.add_trace(go.Scatter(
            x=d["visit_time_dt"],
            y=d["intent_score"],
            mode="markers+lines",
            marker=dict(color=colors, size=sizes, line=dict(width=0)),
            line=dict(color="#1f2130", width=1),
            hovertext=hover,
            hoverinfo="text",
            customdata=d["visit_id"].tolist(),
      ))

      # Anomaly markers
      anomaly_mask = (d["is_no_store"] == True) | (d["response_code"].isin([403, 404, 500]))
      da = d[anomaly_mask]
      if not da.empty:
            fig.add_trace(go.Scatter(
                  x=da["visit_time_dt"],
                  y=da["intent_score"],
                  mode="markers",
                  marker=dict(color="#ff3d5a", size=14, symbol="diamond",
                              line=dict(color="#ff3d5a", width=2)),
                  hoverinfo="skip",
                  name="anomaly",
            ))

      fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Space Mono", color="#555878", size=10),
            showlegend=False,
            margin=dict(l=40, r=16, t=16, b=40),
            xaxis=dict(gridcolor="#1a1c28", zeroline=False, showline=False),
            yaxis=dict(gridcolor="#1a1c28", zeroline=True, zerolinecolor="#2a2d3e",
                       range=[-16, 16], title="intent score"),
            hovermode="closest",
            clickmode="event",
      )
      return fig, f"{len(d)} visits"


@app.callback(
      Output("nav-graph", "figure"),
      Output("graph-badge", "children"),
      Input("intent-threshold", "value"),
      Input("session-filter",   "value"),
      Input("selected-visit-id", "data"),
)
def update_nav_graph(thresh, session_id, selected_id):
      d = filter_df(thresh, session_id)
      if d.empty:
            return go.Figure(), "0 nodes"

      limit = min(300, len(d))
      d_top = d.nlargest(limit, "intent_score")
      id_set = set(d_top["visit_id"])

      G = nx.DiGraph()
      for _, row in d_top.iterrows():
            G.add_node(row["visit_id"],
                       title=row["title"], score=row["intent_score"],
                       url=row["url"], time=row["visit_time"])
            if row["from_visit_id"] in id_set:
                  G.add_edge(row["from_visit_id"], row["visit_id"], etype="nav")
            if row["opener_visit_id"] in id_set:
                  G.add_edge(row["opener_visit_id"], row["visit_id"], etype="tab")

      if len(G.nodes) == 0:
            return go.Figure(), "0 nodes"

      pos = nx.spring_layout(G, k=2.5, iterations=40, seed=42)

      edge_x, edge_y = [], []
      for u, v in G.edges():
            x0, y0 = pos[u]; x1, y1 = pos[v]
            edge_x += [x0, x1, None]; edge_y += [y0, y1, None]

      node_x = [pos[n][0] for n in G.nodes()]
      node_y = [pos[n][1] for n in G.nodes()]
      node_scores = [G.nodes[n]["score"] for n in G.nodes()]
      node_colors = intent_color_vec(node_scores)
      node_sizes  = [8 + abs(s) * 1.5 for s in node_scores]
      node_ids    = list(G.nodes())

      # Highlight selected
      if selected_id and selected_id in id_set:
            node_sizes  = [s * 2.2 if nid == selected_id else s for nid, s in zip(node_ids, node_sizes)]
            node_colors = ["#ffffff" if nid == selected_id else c for nid, c in zip(node_ids, node_colors)]

      hover = [
            f"<b>{G.nodes[n]['title'][:40]}</b><br>Score: {G.nodes[n]['score']:+.2f}"
            for n in G.nodes()
      ]

      fig = go.Figure()
      fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y, mode="lines",
            line=dict(color="#1f2130", width=1),
            hoverinfo="none",
      ))
      fig.add_trace(go.Scatter(
            x=node_x, y=node_y, mode="markers",
            marker=dict(color=node_colors, size=node_sizes, line=dict(width=0)),
            hovertext=hover, hoverinfo="text",
            customdata=node_ids,
      ))
      fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Space Mono", color="#555878", size=10),
            showlegend=False,
            margin=dict(l=8, r=8, t=8, b=8),
            xaxis=dict(visible=False), yaxis=dict(visible=False),
            hovermode="closest",
            clickmode="event",
      )
      return fig, f"{len(G.nodes)} nodes · {len(G.edges)} edges"


@app.callback(
      Output("selected-visit-id", "data"),
      Input("timeline-graph", "clickData"),
      Input("nav-graph",      "clickData"),
)
def store_selected(tl_click, ng_click):
      ctx = callback_context
      if not ctx.triggered:
            return None
      trigger = ctx.triggered[0]["prop_id"]
      click = tl_click if "timeline" in trigger else ng_click
      if not click:
            return None
      pts = click.get("points", [])
      if not pts:
            return None
      cd = pts[0].get("customdata")
      return int(cd) if cd is not None else None


@app.callback(
      Output("drilldown-content", "children"),
      Output("drilldown-stats",   "children"),
      Output("drilldown-badge",   "children"),
      Input("selected-visit-id",  "data"),
)
def update_drilldown(visit_id):
      if visit_id is None:
            empty = html.Div(className="empty-state", children=[
                  html.Div("◎", className="empty-icon"),
                  html.Div("Click any point in the timeline\nor graph to inspect the navigation chain.", className="empty-text"),
            ])
            return empty, [], "click a node"

      row_q = df[df["visit_id"] == visit_id]
      if row_q.empty:
            return html.Div("Visit not found"), [], "—"

      row = row_q.iloc[0]

      # Build ancestor chain (walk back up to 5 levels)
      ancestors = []
      cur = row
      for _ in range(5):
            pid = cur["from_visit_id"] or cur["opener_visit_id"]
            if not pid or pid == 0:
                  break
            par = df[df["visit_id"] == pid]
            if par.empty:
                  break
            ancestors.insert(0, par.iloc[0])
            cur = par.iloc[0]

      # Children (direct)
      children_from   = df[df["from_visit_id"]   == visit_id]
      children_opener = df[df["opener_visit_id"] == visit_id]
      children = pd.concat([children_from, children_opener]).drop_duplicates("visit_id")
      children = children.sort_values("visit_time").head(8)

      content = []

      if ancestors:
            content.append(html.Div("↑ ancestors", className="section-label"))
            for anc in ancestors:
                  content.append(make_visit_card(anc, "ancestor"))
                  content.append(html.Div("↓", className="nav-arrow"))

      content.append(html.Div("● selected", className="section-label"))
      content.append(make_visit_card(row, "active"))

      if not children.empty:
            content.append(html.Div("↓ children", className="section-label"))
            for _, child in children.iterrows():
                  content.append(html.Div("↓", className="nav-arrow"))
                  content.append(make_visit_card(child, "child"))

      # Stats
      score = row["intent_score"]
      dur   = row["duration"]
      sess  = row["session_id"]
      stats = html.Div(className="stats-row", children=[
            html.Div(className="stat-box", children=[
                  html.Div(f"{score:+.1f}", className="stat-val", style={"color": intent_color(score)}),
                  html.Div("INTENT", className="stat-lbl"),
            ]),
            html.Div(className="stat-box", children=[
                  html.Div(f"{dur:.0f}s" if dur < 60 else f"{dur/60:.1f}m", className="stat-val"),
                  html.Div("DURATION", className="stat-lbl"),
            ]),
            html.Div(className="stat-box", children=[
                  html.Div(f"S{sess}", className="stat-val"),
                  html.Div("SESSION", className="stat-lbl"),
            ]),
            html.Div(className="stat-box", children=[
                  html.Div(str(len(children)), className="stat-val"),
                  html.Div("CHILDREN", className="stat-lbl"),
            ]),
      ])

      badge = f"visit {visit_id}"
      return content, stats, badge


if __name__ == "__main__":
      print(f"Dashboard ready → http://127.0.0.1:8050")
      app.run(debug=False, port=8050)