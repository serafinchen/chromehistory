import datetime
from urllib.parse import urlparse


      
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
      