import pathlib
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

from ccl_chromium_reader import ccl_chromium_cache
from app.helpers import normalize_url


@dataclass
class CacheEntry:
      url: str
      domain: str
      response_code: Optional[int] = None
      content_type: Optional[str] = None
      content_language: Optional[str] = None
      is_personalized: bool = False
      is_no_store: bool = False
      age: Optional[int] = None
      last_modified: Optional[str] = None
      content_length: Optional[int] = None


def _parse_headers(raw_headers: Optional[str]) -> tuple[Optional[int], dict[str, str]]:
      response_code: Optional[int] = None
      headers: dict[str, str] = {}

      if not raw_headers:
            return response_code, headers

      for line in raw_headers.splitlines():
            if line.startswith("HTTP/"):
                  parts = line.split(" ", 2)
                  if len(parts) >= 2:
                        try:
                              response_code = int(parts[1])
                        except ValueError:
                              pass
            elif ":" in line:
                  k, _, v = line.partition(":")
                  headers[k.strip().lower()] = v.strip()

      return response_code, headers


def _build_cache_entry(url: str, headers: dict[str, str], response_code: Optional[int]) -> CacheEntry:
      def h(name: str) -> Optional[str]:
            return headers.get(name)

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

      return CacheEntry(
            url=url,
            domain=urlparse(url).netloc,
            response_code=response_code,
            content_type=h("content-type"),
            content_language=h("content-language"),
            is_personalized=is_personalized,
            is_no_store=is_no_store,
            age=age,
            last_modified=h("last-modified"),
            content_length=content_length,
      )


def load_cache_entries(cache_path: pathlib.Path) -> list[CacheEntry]:
      entries: list[CacheEntry] = []

      if not cache_path.exists():
            return entries

      try:
            cache_type = ccl_chromium_cache.guess_cache_class(cache_path)
            cache = cache_type(cache_path)
      except Exception:
            return entries

      for key in cache.keys():
            try:
                  record = cache[key]
                  url = normalize_url(record.key)
                  domain = urlparse(url).netloc

                  if not domain:
                        continue

                  try:
                        raw_headers = record.get_response_headers()
                  except Exception:
                        raw_headers = None

                  response_code, headers = _parse_headers(raw_headers)
                  entries.append(_build_cache_entry(url, headers, response_code))

            except Exception:
                  continue

      return entries


def index_by_url(entries: list[CacheEntry]) -> dict[str, list[CacheEntry]]:
      index: dict[str, list[CacheEntry]] = {}
      for entry in entries:
            index.setdefault(entry.url, []).append(entry)
      return index


def index_by_domain(entries: list[CacheEntry]) -> dict[str, list[CacheEntry]]:
      index: dict[str, list[CacheEntry]] = {}
      for entry in entries:
            index.setdefault(entry.domain, []).append(entry)
      return index
