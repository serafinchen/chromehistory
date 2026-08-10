from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from app.cache import CacheEntry, index_by_domain, index_by_url
from app.history import HistoryEntry


class MatchType(str, Enum):
      EXACT_URL = "exact_url"      
      NONE = "none"                

@dataclass
class MatchedVisit:
      history: HistoryEntry
      match_type: MatchType

      response_code: Optional[int] = None
      content_type: Optional[str] = None
      content_language: Optional[str] = None
      is_personalized: bool = False
      is_no_store: bool = False
      age: Optional[int] = None
      last_modified: Optional[str] = None
      content_length: Optional[int] = None
      matched_cache_entries: list[CacheEntry] = field(default_factory=list)

      domain_asset_count: int = 0
      domain_total_bytes: int = 0

      @property
      def is_error(self) -> bool:
            return self.response_code is not None and self.response_code >= 400


def _pick_html(entries: list[CacheEntry]) -> CacheEntry:
      html_entries = [e for e in entries if e.content_type and "text/html" in e.content_type]
      return html_entries[0] if html_entries else entries[0]


def match_history_with_cache(history_entries: list[HistoryEntry], cache_entries: list[CacheEntry],) -> list[MatchedVisit]:

      url_index = index_by_url(cache_entries)
      domain_index = index_by_domain(cache_entries)

      matched: list[MatchedVisit] = []

      for h in history_entries:
            exact_matches = url_index.get(h.url, [])
            domain_matches = domain_index.get(h.domain, [])

            domain_total_bytes = sum(e.content_length or 0 for e in domain_matches)
            domain_asset_count = len(domain_matches)

            if exact_matches:
                  ref = _pick_html(exact_matches)
                  matched.append(
                        MatchedVisit(
                              history=h,
                              match_type=MatchType.EXACT_URL,
                              response_code=ref.response_code,
                              content_type=ref.content_type,
                              content_language=ref.content_language,
                              is_personalized=any(e.is_personalized for e in exact_matches),
                              is_no_store=any(e.is_no_store for e in exact_matches),
                              age=ref.age,
                              last_modified=ref.last_modified,
                              content_length=ref.content_length,
                              matched_cache_entries=exact_matches,
                              domain_asset_count=domain_asset_count,
                              domain_total_bytes=domain_total_bytes,
                        )
                  )
            else:
                  matched.append(MatchedVisit(history=h, match_type=MatchType.NONE))

      return matched
