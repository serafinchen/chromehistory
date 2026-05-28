from history import load_history, normalize, copy_history_db, PROFILE_PATH
from graph import build_chrome_history_graph, plot_history_pyvis

if __name__ == "__main__":
      copy_history_db()
      history = load_history(PROFILE_PATH)
      data = normalize(history)

      G = build_chrome_history_graph(PROFILE_PATH)
      plot_history_pyvis(G)
      