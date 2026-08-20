import datetime
from urllib.parse import urlparse
import os
from pathlib import Path

def get_browser_profile(browser: str) -> Path:
      local_app_data = Path(os.environ["LOCALAPPDATA"])
      roaming_app_data = Path(os.environ["APPDATA"])

      profiles = {
            "chrome": local_app_data / "Google/Chrome/User Data/Default",
            "edge": local_app_data / "Microsoft/Edge/User Data/Default",
            "brave": local_app_data / "BraveSoftware/Brave-Browser/User Data/Default",
            "opera": roaming_app_data / "Opera Software/Opera Stable",
      }

      return profiles[browser]


PROFILE_PATH = get_browser_profile("chrome")

CACHE_PATHS = {
      "chrome": Path.home() / "AppData/Local/Google/Chrome/User Data/Default",
      "edge":   Path.home() / "AppData/Local/Microsoft/Edge/User Data/Default/Cache/Cache_Data",
      "brave":  Path.home() / "AppData/Local/BraveSoftware/Brave-Browser/User Data/Default/Cache/Cache_Data",
      "opera":  Path.home() / "AppData/Roaming/Opera Software/Opera Stable/Cache/Cache_Data",
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
      