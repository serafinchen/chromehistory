import shutil
from ccl_chromium_reader import ChromiumProfileFolder
import pathlib
from urllib.parse import urlparse
import datetime

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

TRANSITIONS = {
      1: "LINK",
      2: "TYPED",
      4: "AUTO_BOOKMARK",
      8: "AUTO_SUBFRAME",
      16: "MANUAL_SUBFRAME",
      32: "GENERATED",
      64: "AUTO_TOPLEVEL",
      128: "FORM_SUBMIT",
      256: "RELOAD"
}

QUALIFIERS = {
      0x00000001: "FORWARD_BACK",
      0x00000002: "FORWARD_BACK_MASK",

      0x00000004: "CLIENT_REDIRECT",
      0x00000008: "SERVER_REDIRECT",
      0x00000010: "IS_REDIRECT_MASK",

      0x00000020: "FROM_ADDRESS_BAR",
      0x00000040: "FROM_API",
      0x00000080: "FROM_START_PAGE",

      0x00000100: "IS_MAIN_FRAME",
      0x00000200: "IS_SUBFRAME",

      0x00000400: "BLOCKED",
      0x00000800: "SAFE_BROWSING",
      0x00001000: "ALLOW_POPUP",

      0x00002000: "RELOAD",
      0x00004000: "RELOAD_BYPASSING_CACHE",
      }

def decode_transition(value):
      if value == 0:
            return "UNKNOWN"

      result = []
      for flag, name in TRANSITIONS.items():
            if value & flag:
                  result.append(name)

      return "|".join(result) if result else "UNKNOWN"

def decode_qualifier(value: int) -> str:
      if value == 0:
            return "NONE"

      result = []
      for flag, name in QUALIFIERS.items():
            if value & flag:
                  result.append(name)

      return "|".join(result) if result else "UNKNOWN"            

def chrome_time_to_datetime(chrome_time):
      if isinstance(chrome_time, datetime.datetime):
            return chrome_time
      return datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=chrome_time)

def normalize_url(url):
      try:
            parsed = urlparse(url)
            return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

      except Exception:
            return url
      
def copy_history_db():
      shutil.copy2(HISTORY_FILE, TEMP_DB)   

def load_history(profile_path):
      with ChromiumProfileFolder(profile_path) as profile:
            history = list(profile.iterate_history_records())

      return history





def compute_intent_score(h):
      score = 0.0

      core = str(h.transition.core)

      if core == "LINK":
            score += 2.0
      elif core in ["AUTO_SUBFRAME", "CLIENT_REDIRECT"]:
            score -= 2.0
      elif core == "TYPED":
            score += 1

      duration = h.visit_duration.total_seconds() if h.visit_duration else 0

      if duration > 10:
            score += 1.0
      elif duration < 3:
            score -= 1.0
      elif duration < 1:
            score -= 3.0

      if h.from_visit_id:
            score += 1

      return round(score)

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

                  "transition_core": decode_transition(h.transition.core),
                  "transition_qualifier": decode_qualifier(h.transition.qualifier),

                  "intent_score": compute_intent_score(h)
            })
      return data


if __name__ == "__main__":
      history = load_history(PROFILE_PATH)
      data = normalize(history)
      print(data)