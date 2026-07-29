import datetime
from urllib.parse import urlparse
import math


SESSION_GAP = 30 * 60

#HOW DID THE VISIT TOOK PLACE
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

#UNDER WHICH CIRCUMSTANCES
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
      
def decode_core(value: int) -> list[str]:
      if value == 0:
            return []

      result = []

      for flag, name in TRANSITIONS.items():
            if value & flag:
                  result.append(name)

      return result

def decode_qualifier(value: int) -> list[str]:
      if value == 0:
            return []

      result = []

      for flag, name in QUALIFIERS.items():
            if value & flag:
                  result.append(name)

      return result 

CORE_WEIGHTS = {
      "LINK": 3.0,
      "TYPED": 8.0,
      "AUTO_BOOKMARK": 6.0,
      "FORM_SUBMIT": 7.0,
      "GENERATED": 2.0,

      "MANUAL_SUBFRAME": -2.0,

      "AUTO_SUBFRAME": -8.0,
      "AUTO_TOPLEVEL": -6.0,
      "RELOAD": -2.0,
}


QUALIFIER_WEIGHTS = {
      "FORWARD_BACK": -3.0,

      "CLIENT_REDIRECT": -6.0,
      "SERVER_REDIRECT": -4.0,

      "FROM_ADDRESS_BAR": 5.0,

      "FROM_API": -7.0,

      "FROM_START_PAGE": -2.0,

      "IS_MAIN_FRAME": 2.0,
      "IS_SUBFRAME": -7.0,

      "BLOCKED": -5.0,
      "SAFE_BROWSING": -4.0,

      "ALLOW_POPUP": -5.0,

      "RELOAD": -2.0,
      "RELOAD_BYPASSING_CACHE": -1.0,
}

def compute_intent_score(h):
      score = 0.0

      core = decode_core(h.transition.core)
      qualifiers = decode_qualifier(h.transition.qualifier)

      score = 0.0

      #Core
      for c in core:
            score = CORE_WEIGHTS.get(c, 0)

      for q in qualifiers:
            score = QUALIFIER_WEIGHTS.get(q, 0)

      duration = h.visit_duration.total_seconds() if h.visit_duration else 0
      duration_score = math.log1p(duration)
      duration_score = (duration_score-1.0)*2.2

      if duration < 2:
            duration_score -= 6

      elif duration < 5:
            duration_score -= 2

      score += duration_score

      if h.from_visit_id is not None:
            score += 1

      score = max(-15, min(score, 15))      

      return score


def add_sessions(df):
      session_ids = [0]

      for i in range(1, len(df)):
            gap = (
                  df.loc[i, "visit_time_dt"]
                  - df.loc[i-1, "visit_time_dt"]
            ).total_seconds()

            session_ids.append(
                  session_ids[-1] + (1 if gap > SESSION_GAP else 0)
            )

      df["session_id"] = session_ids
      return df

def intent_color(score):
      if score >= 10:  return "#00ff9d"
      if score >= 5:   return "#7fff7f"
      if score >= 2:   return "#ffd700"
      if score >= 0:   return "#888ea8"
      if score >= -5:  return "#ff8c42"
      return "#ff3d5a"


def intent_color_vec(scores):
      return [intent_color(s) for s in scores]

def visit_type_color(tags):
    if "TYPED" in tags:
        return "#ffcc00"
    if "LINK" in tags:
        return "#55aaff"
    if "RELOAD" in tags:
        return "#999999"
    return "#777777"

