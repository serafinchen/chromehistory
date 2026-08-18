import datetime
from urllib.parse import urlparse

import pathlib

PROFILE_PATH = pathlib.Path(r"C:\Users\seraf\AppData\Local\Google\Chrome\User Data\Default")

CACHE_PATHS = {
      "chrome": pathlib.Path.home() / "AppData/Local/Google/Chrome/User Data/Default",
      "edge":   pathlib.Path.home() / "AppData/Local/Microsoft/Edge/User Data/Default/Cache/Cache_Data",
      "brave":  pathlib.Path.home() / "AppData/Local/BraveSoftware/Brave-Browser/User Data/Default/Cache/Cache_Data",
      "opera":  pathlib.Path.home() / "AppData/Roaming/Opera Software/Opera Stable/Cache/Cache_Data",
}
      
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
      