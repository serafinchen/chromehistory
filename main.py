from history import load_history, normalize, copy_history_db, PROFILE_PATH
from graph import build_chrome_history_graph, plot_history_pyvis

if __name__ == "__main__":
      history = load_history(PROFILE_PATH)
      data = normalize(history)

      G = build_chrome_history_graph(data, 200)
      plot_history_pyvis(G)
