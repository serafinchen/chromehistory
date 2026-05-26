import shutil
from ccl_chromium_reader import ChromiumProfileFolder
import pathlib
from helpers import decode_core, decode_qualifier, chrome_time_to_datetime, normalize_url
from intent import compute_intent_score

PROFILE_PATH = (
      pathlib.Path.home()
      / "AppData"
      / "Local"
      / "Google"
      / "Chrome"
      / "User Data"
      / "Default"
)

HISTORY_FILE = PROFILE_PATH / "History"
TEMP_DB = "history_copy.db"

      
def copy_history_db():
      shutil.copy2(HISTORY_FILE, TEMP_DB)   

def load_history(profile_path):
      with ChromiumProfileFolder(profile_path) as profile:
            history = list(profile.iterate_history_records())

      return history

def normalize(history):
      data = []

      for h in history:
            visit_time = chrome_time_to_datetime(h.visit_time)

            data.append({
                  "visit_id": h.rec_id,
                  "url": normalize_url(h.url),
                  "title": h.title,
                  "visit_time": visit_time.isoformat(),
                  "visit_duration_seconds": h.visit_duration.total_seconds() if h.visit_duration else 0,

                  "from_visit_id": h.from_visit_id,
                  "opener_visit_id": h.opener_visit_id,

                  "transition_core": decode_core(h.transition.core),
                  "transition_qualifier": "|".join(decode_qualifier(h.transition.qualifier)),

                  "intent_score": compute_intent_score(h)
            })
      return data
