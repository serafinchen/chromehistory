from ccl_chromium_reader import ChromiumProfileFolder
import nx

def build_chrome_history_graph(profile_path):
      G = nx.DiGraph()

      with ChromiumProfileFolder(profile_path) as profile:
            history = list(profile.iterate_history_records())

      lookup = {h.rec_id: h for h in history}

      for h in history:
            G.add_node(
                  h.rec_id,
                  url=h.url,
                  title=h.title,
                  visit_time=str(h.visit_time)
            )

            if h.from_visit_id in lookup:
                  parent = lookup[h.from_visit_id]
                  G.add_edge(
                  parent.rec_id,
                  h.rec_id,
                  type="from_visit",
                  transition=str(h.transition)
                  )

            if h.opener_visit_id in lookup:
                  opener = lookup[h.opener_visit_id]
                  G.add_edge(
                  opener.rec_id,
                  h.rec_id,
                  type="opener"
                  )

      return G