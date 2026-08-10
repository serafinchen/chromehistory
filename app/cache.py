import pathlib
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse
import gzip
import zlib

try:
    import brotli
except ImportError:
    brotli = None

import pathlib
import shutil

from ccl_chromium_reader import ChromiumProfileFolder

from app.helpers import normalize_url

TEMP_CACHE_DIR = pathlib.Path("cache_copy")
@dataclass
class CacheEntry:
    url: str
    domain: str
    raw_key: str
    response_code: Optional[int] = None
    content_type: Optional[str] = None
    content_language: Optional[str] = None
    content_encoding: Optional[str] = None
    is_personalized: bool = False
    is_no_store: bool = False
    age: Optional[int] = None
    last_modified: Optional[str] = None
    content_length: Optional[int] = None


def _attr(meta, name: str) -> Optional[str]:
      if meta is None:
            return None
      values = meta.get_attribute(name)
      return values[0] if values else None


def _parse_status_code(meta) -> Optional[int]:
      if meta is None:
            return None
      for line in meta.http_header_declarations:
            if line.upper().startswith("HTTP/"):
                  parts = line.split(" ", 2)
                  if len(parts) >= 2:
                        try:
                              return int(parts[1])
                        except ValueError:
                              return None
      return None


def _build_cache_entry(record, url: str) -> CacheEntry:
      meta = record.metadata

      content_length_raw = _attr(meta, "content-length")
      try:
            content_length = int(content_length_raw) if content_length_raw else None
      except ValueError:
            content_length = None

      age_raw = _attr(meta, "age")
      try:
            age = int(age_raw) if age_raw else None
      except ValueError:
            age = None

      vary = _attr(meta, "vary") or ""
      is_personalized = any(
            v.strip().lower() in ("cookie", "authorization") for v in vary.split(",")
      )

      cc = _attr(meta, "cache-control") or ""
      is_no_store = "no-store" in cc.lower()

      return CacheEntry(
            url=url,
            domain=urlparse(url).netloc,
            raw_key=record.key.raw_key,
            response_code=_parse_status_code(meta),
            content_type=_attr(meta, "content-type"),
            content_language=_attr(meta, "content-language"),
            content_encoding=_attr(meta, "content-encoding"),
            is_personalized=is_personalized,
            is_no_store=is_no_store,
            age=age,
            last_modified=_attr(meta, "last-modified"),
            content_length=content_length,
      )


def load_cache_entries(profile: ChromiumProfileFolder) -> list[CacheEntry]:
      entries: list[CacheEntry] = []
      for record in profile.iterate_cache(None, omit_cached_data=True):
            try:
                  if record.metadata is None:
                        continue
                  url = normalize_url(record.key.url)
                  domain = urlparse(url).netloc
                  if not domain:
                        continue
                  entries.append(_build_cache_entry(record, url))
            except Exception as exc:
                  print(f"[cache] Skipping record: {exc}")
                  continue
      return entries


def get_cached_body(profile: ChromiumProfileFolder, raw_key: str) -> Optional[bytes]:
      data_hits = profile.cache.get_cachefile(raw_key)
      meta_hits = profile.cache.get_metadata(raw_key)

      if not data_hits or not meta_hits:
            return None

      data = data_hits[0]
      meta = meta_hits[0]
      if data is None:
            return None

      encoding = (_attr(meta, "content-encoding") or "").strip().lower()
      try:
            if encoding == "gzip":
                  data = gzip.decompress(data)
            elif encoding == "br":
                  if brotli is None:
                        raise RuntimeError("Paket 'brotli' fehlt (pip install Brotli)")
                  data = brotli.decompress(data)
            elif encoding == "deflate":
                  data = zlib.decompress(data, -zlib.MAX_WBITS)
      except Exception as exc:
            print(f"[cache] Dekompression fehlgeschlagen ({encoding}): {exc}")
            return None

      return data


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
