import datetime
from urllib.parse import urlparse

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

def score_to_color(score):

      if score >= 10:
            return "#1abc9c"
      elif score >= 5:
            return "#2ecc71"
      elif score >= 2:
            return "#f1c40f"
      elif score >= 0:
            return "#95a5a6"
      elif score >= -5:
            return "#e67e22"
      else:
            return "#e74c3c"
      
def chrome_time_to_datetime(chrome_time):
      if isinstance(chrome_time, datetime.datetime):
            return chrome_time
      return datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=chrome_time)


def normalize_url(url):
      try:
            parsed = urlparse(url)
            return (
                  f"{parsed.scheme}://{parsed.netloc}"
                  f"{parsed.path}"
                  f"?{parsed.query}"
            ).rstrip("/")
      except Exception:
            return url
      