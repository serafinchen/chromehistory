import sys
from pathlib import Path

import dash
from dash import Dash

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
      sys.path.insert(0, str(ROOT))

app = Dash(
      __name__,
      use_pages=True,
      suppress_callback_exceptions=True,
      title="History Analyser"
      )

server = app.server

app.layout = dash.page_container

if __name__ == "__main__":
      app.run(debug=False, port=8050)
      
