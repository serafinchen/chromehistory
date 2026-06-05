import datetime
import shutil
import pathlib
from typing import Optional
from ccl_chromium_reader import ChromiumProfileFolder
from ccl_chromium_reader import ccl_chromium_cache
from helpers import decode_core, decode_qualifier, chrome_time_to_datetime, normalize_url
from intent import compute_intent_score
from dataclasses import dataclass, field
from urllib.parse import urlparse


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

      # Cache — nur was für Intent relevant ist
      cached: bool = False
      response_code: Optional[int] = None        # wurde Seite geladen? Fehler?
      content_type: Optional[str] = None         # html? json? was war es?
      content_language: Optional[str] = None     # welche Sprache
      is_personalized: bool = False              # Vary: Cookie/Authorization
      is_no_store: bool = False                  # bewusst nicht gecacht → sensitiv?
      cache_age_seconds: Optional[int] = None    # wie alt war gecachter Inhalt
      last_modified: Optional[str] = None        # wann geändert
      asset_count: int = 0                       # wie viele Assets von dieser Domain
      total_bytes: int = 0                       # wie viel wurde geladen


def copy_history_db():
      shutil.copy2(HISTORY_FILE, TEMP_DB)


def load_history(profile_path):
      with ChromiumProfileFolder(profile_path) as profile:
            history = list(profile.iterate_history_records())
      return history

def build_cache_domain_index(cache_data: dict[str, dict]) -> dict[str, list[dict]]:
      """Gruppiert Cache-Einträge nach Domain für Domain-Level-Matching."""
      domain_index: dict[str, list[dict]] = {}

      for url, entry in cache_data.items():
            try:
                  domain = urlparse(url).netloc
                  if domain not in domain_index:
                        domain_index[domain] = []
                  domain_index[domain].append(entry)
            except Exception:
                  continue



def load_cache(cache_path: pathlib.Path) -> dict[str, dict]:
      domain_index: dict[str, dict] = {}

      if not cache_path.exists():
            return domain_index

      try:
            cache_type = ccl_chromium_cache.guess_cache_class(cache_path)
            cache = cache_type(cache_path)
      except Exception:
            return domain_index

      for key in cache.keys():
            try:
                  record = cache[key]
                  url = normalize_url(record.key)
                  domain = urlparse(url).netloc

                  if not domain:
                        continue

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

                  age: Optional[int] = None
                  if h("age"):
                        try:
                              age = int(h("age"))
                        except ValueError:
                              pass

                  vary = h("vary") or ""
                  is_personalized = any(
                        v.strip().lower() in ("cookie", "authorization")
                        for v in vary.split(",")
                  )

                  cc = h("cache-control") or ""
                  is_no_store = "no-store" in cc.lower()

                  entry = {
                        "response_code":     response_code,
                        "content_type":      h("content-type"),
                        "content_language":  h("content-language"),
                        "is_personalized":   is_personalized,
                        "is_no_store":       is_no_store,
                        "age":               age,
                        "last_modified":     h("last-modified"),
                        "content_length":    content_length,
                  }

                  if domain not in domain_index:
                        domain_index[domain] = {
                              "entries": [],
                              "asset_count": 0,
                              "total_bytes": 0,
                        }

                  domain_index[domain]["entries"].append(entry)
                  domain_index[domain]["asset_count"] += 1
                  if content_length:
                        domain_index[domain]["total_bytes"] += content_length

            except Exception:
                  continue

      return domain_index


def normalize(history, cache_data: dict[str, dict] | None = None) -> list[HistoryVisit]:
      if cache_data is None:
            cache_data = {}

      data = []

      for h in history:
            visit_time = chrome_time_to_datetime(h.visit_time)
            url = normalize_url(h.url)
            domain = urlparse(url).netloc
            domain_data = cache_data.get(domain)
            entries = domain_data["entries"] if domain_data else []

            html_entries = [
                  e for e in entries
                  if e["content_type"] and "text/html" in e["content_type"]
            ]
            ref = html_entries[0] if html_entries else (entries[0] if entries else None)

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

                  cached=domain_data is not None,
                  response_code=ref["response_code"] if ref else None,
                  content_type=ref["content_type"] if ref else None,
                  content_language=ref["content_language"] if ref else None,
                  is_personalized=any(e["is_personalized"] for e in entries),
                  is_no_store=any(e["is_no_store"] for e in entries),
                  cache_age_seconds=ref["age"] if ref else None,
                  last_modified=ref["last_modified"] if ref else None,
                  asset_count=domain_data["asset_count"] if domain_data else 0,
                  total_bytes=domain_data["total_bytes"] if domain_data else 0,
            )
            data.append(normalized_visit)

      return data