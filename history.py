import datetime
import shutil
import pathlib
from typing import Optional
from ccl_chromium_reader import ChromiumProfileFolder
from ccl_chromium_reader import ccl_chromium_cache
from helpers import decode_core, decode_qualifier, chrome_time_to_datetime, normalize_url
from intent import compute_intent_score
from dataclasses import dataclass, field


PROFILE_PATH = (
      pathlib.Path.home()
      / "AppData"
      / "Local"
      / "Google"
      / "Chrome"
      / "User Data"
      / "Default"
)

CACHE_PATH = PROFILE_PATH / "Cache" / "Cache_Data"

HISTORY_FILE = PROFILE_PATH / "History"
TEMP_DB = "history_copy.db"


@dataclass
class HistoryVisit:
      visit_id: int
      url: str
      title: str
      visit_time: str
      visit_duration_seconds: float
      from_visit_id: Optional[int]
      opener_visit_id: Optional[int]
      transition_core: str
      transition_qualifier: str
      intent_score: float

      # Cache
      cached: bool = False
      content_type: Optional[str] = None
      cache_creation_time: Optional[str] = None
      cache_last_used_time: Optional[str] = None
      response_code: Optional[int] = None
      server: Optional[str] = None
      etag: Optional[str] = None
      cache_control: Optional[str] = None
      content_encoding: Optional[str] = None
      content_length: Optional[int] = None


def copy_history_db():
      shutil.copy2(HISTORY_FILE, TEMP_DB)


def load_history(profile_path):
      with ChromiumProfileFolder(profile_path) as profile:
            history = list(profile.iterate_history_records())
      return history


def load_cache(cache_path: pathlib.Path) -> dict[str, dict]:
      cache_data: dict[str, dict] = {}

      if not cache_path.exists():
            return cache_data

      try:
            cache_type = ccl_chromium_cache.guess_cache_class(cache_path)
            cache = cache_type(cache_path)
      except Exception:
            return cache_data

      for key in cache.keys():
            try:
                  record = cache[key]
                  url = normalize_url(record.key)

                  headers_raw: dict[str, str] = {}
                  response_code: Optional[int] = None

                  try:
                        http_headers = record.get_response_headers()
                        if http_headers:
                              for line in http_headers.splitlines():
                                    if line.startswith("HTTP/"):
                                          parts = line.split(" ", 2)
                                          if len(parts) >= 2:
                                                try:
                                                      response_code = int(parts[1])
                                                except ValueError:
                                                      pass
                                    elif ":" in line:
                                          k, _, v = line.partition(":")
                                          headers_raw[k.strip().lower()] = v.strip()
                  except Exception:
                        pass

                  def h(name: str) -> Optional[str]:
                        return headers_raw.get(name)

                  content_length: Optional[int] = None
                  if h("content-length"):
                        try:
                              content_length = int(h("content-length"))
                        except ValueError:
                              pass

                  cache_data[url] = {
                        "content_type":      h("content-type"),
                        "creation_time":     record.creation_time.isoformat() if record.creation_time else None,
                        "last_used_time":    record.last_used_time.isoformat() if record.last_used_time else None,
                        "response_code":     response_code,
                        "server":            h("server"),
                        "etag":              h("etag"),
                        "cache_control":     h("cache-control"),
                        "content_encoding":  h("content-encoding"),
                        "content_length":    content_length,
                  }

            except Exception:
                  continue

      return cache_data


def normalize(history, cache_data: dict[str, dict] | None = None) -> list[HistoryVisit]:
      if cache_data is None:
            cache_data = {}

      data = []

      for h in history:
            visit_time = chrome_time_to_datetime(h.visit_time)
            url = normalize_url(h.url)
            cached_entry = cache_data.get(url)

            normalized_visit = HistoryVisit(
                  visit_id=h.rec_id,
                  url=url,
                  title=h.title or "Untitled",
                  visit_time=visit_time.isoformat(),
                  visit_duration_seconds=h.visit_duration.total_seconds() if h.visit_duration else 0,
                  from_visit_id=h.from_visit_id,
                  opener_visit_id=h.opener_visit_id,
                  transition_core=decode_core(h.transition.core),
                  transition_qualifier="|".join(decode_qualifier(h.transition.qualifier)),
                  intent_score=compute_intent_score(h),

                  cached=cached_entry is not None,
                  content_type=cached_entry.get("content_type") if cached_entry else None,
                  cache_creation_time=cached_entry.get("creation_time") if cached_entry else None,
                  cache_last_used_time=cached_entry.get("last_used_time") if cached_entry else None,
                  response_code=cached_entry.get("response_code") if cached_entry else None,
                  server=cached_entry.get("server") if cached_entry else None,
                  etag=cached_entry.get("etag") if cached_entry else None,
                  cache_control=cached_entry.get("cache_control") if cached_entry else None,
                  content_encoding=cached_entry.get("content_encoding") if cached_entry else None,
                  content_length=cached_entry.get("content_length") if cached_entry else None,
            )
            data.append(normalized_visit)

      return data