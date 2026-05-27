from helpers import decode_core, decode_qualifier

def compute_intent_score(h):
      score = 0.0

      core = decode_core(h.transition.core)
      qualifier = decode_qualifier(h.transition.qualifier)

      #Core
      if "LINK" in core: #intended link
            score += 3.5

      elif "TYPED" in core: #typed URL
            score += 4.0

      elif "AUTO_BOOKMARK" in core: #clicked from bookmark
            score += 3.5 

      elif "AUTO_SUBFRAME" in core: #autoload/ads
            score += 0.5    

      elif "MANUAL_SUBFRAME" in core: #manual iframe
            score += 2.0    

      elif "GENERATED" in core: #generated navigation
            score += 2.5

      elif "AUTO_TOPLEVEL" in core: #session restore
            score += 0.5

      elif "FORM_SUBMIT" in core: #login/search
            score += 3.5

      elif "RELOAD" in core:
            score += 0.5

      #Qualifier
      if "FORWARD_BACK" in qualifier: #user navigated via browser back/forward history
            score -= 1.0

      if "FORWARD_BACK_MASK" in qualifier: #technical history-navigation mask flag
            score -= 1.5

      if "CLIENT_REDIRECT" in qualifier: #redirect triggered by JavaScript/meta refresh
            score -= 1.5

      if "SERVER_REDIRECT" in qualifier: #HTTP redirect from server (301/302/etc.)
            score -= 1.0

      if "IS_REDIRECT_MASK" in qualifier: #technical redirect-related mask flag
            score -= 1.5

      if "FROM_ADDRESS_BAR" in qualifier:  #navigation initiated from browser address bar
            score += 1.5

      if "FROM_API" in qualifier: #page opened by external app/API/browser automation
            score -= 2.0

      if "FROM_START_PAGE" in qualifier: #navigation originated from browser start/new-tab page
            score -= 0.5

      if "IS_MAIN_FRAME" in qualifier: #primary/top-level page visited by the user
            score += 1.0

      if "IS_SUBFRAME" in qualifier: #iframe or embedded resource, usually passive loading
            score -= 2.5

      if "BLOCKED" in qualifier: #navigation/resource blocked by browser or policy
            score -= 2.0

      if "SAFE_BROWSING" in qualifier: #triggered Safe Browsing/security protection
            score -= 1.5

      if "ALLOW_POPUP" in qualifier: #popup window/tab triggered or allowed
            score -= 1.0

      if "RELOAD" in qualifier: #page reload, not a fresh navigation
            score -= 1.0

      if "RELOAD_BYPASSING_CACHE" in qualifier: #hard refresh bypassing browser cache
            score -= 0.5

      duration = h.visit_duration.total_seconds() if h.visit_duration else 0

      if duration > 8:
            score += 1.0
      elif duration < 3:
            score -= 1.0
      elif duration < 1:
            score -= 3.0

      if h.from_visit_id:
            score += 1

      return score
