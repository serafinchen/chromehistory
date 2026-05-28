from helpers import decode_core, decode_qualifier
import math


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
