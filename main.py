from history import load_history, load_cache, normalize, PROFILE_PATH, CACHE_PATH
from graph import build_chrome_history_graph, plot_history_pyvis

if __name__ == "__main__":
      history = load_history(PROFILE_PATH)
      cache_data = load_cache(CACHE_PATH)
      data = normalize(history, cache_data)
      print(data)

      #G = build_chrome_history_graph(data, 200)
      #plot_history_pyvis(G)