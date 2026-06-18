from ccl_chromium_reader import ChromiumProfileFolder, ccl_chromium_cache, ccl_chromium_history
from urllib.parse import urlparse
from app.helpers import normalize_url
import pathlib
from typing import Optional
from app.history import PROFILE_PATH
import shutil

HISTORY_FILE = PROFILE_PATH / "History"
TEMP_DB = "history_copy.db"


def load_history(profile_path):
      history_file = pathlib.Path(profile_path) / "History"
      temp_db = pathlib.Path(TEMP_DB)

      try:
            shutil.copy2(history_file, temp_db)
            db_path = temp_db
      except OSError:
            db_path = temp_db if temp_db.exists() else history_file

      with ccl_chromium_history.HistoryDatabase(db_path) as history_db:
            history = list(history_db.iter_history_records(None))
      return history

def copy_history_db():
      shutil.copy2(HISTORY_FILE, TEMP_DB)


def build_cache_domain_index(cache_data: dict[str, dict]) -> dict[str, list[dict]]:
      domain_index: dict[str, list[dict]] = {}

      for url, entry in cache_data.items():
            try:
                  domain = urlparse(url).netloc
                  if domain not in domain_index:
                        domain_index[domain] = []
                  domain_index[domain].append(entry)
            except Exception:
                  continue

      return domain_index


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

