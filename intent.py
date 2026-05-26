from helpers import decode_core, decode_qualifier

def compute_intent_score(h):
      score = 0.0

      core = decode_core(h.transition.core)
      qualifier = decode_qualifier(h.transition.qualifier)

      #Core
      if "LINK" in core:
            score += 2.0

      elif "TYPED" in core:
            score += 2.5

      elif "FORM_SUBMIT" in core:
            score += 2.0

      elif "AUTO_SUBFRAME" in core:
            score -= 0.5

      elif "RELOAD" in core:
            score += 0.2

      #Qualifier
      if "CLIENT_REDIRECT" in qualifier:
            score -= 1.5

      if "SERVER_REDIRECT" in qualifier:
            score -= 1.5

      duration = h.visit_duration.total_seconds() if h.visit_duration else 0

      if duration > 10:
            score += 1.0
      elif duration < 3:
            score -= 1.0
      elif duration < 1:
            score -= 3.0

      if h.from_visit_id:
            score += 1

      return score
