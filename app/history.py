import datetime
import shutil
import pathlib
from typing import Optional
from ccl_chromium_reader import ChromiumProfileFolder
from ccl_chromium_reader import ccl_chromium_cache
from app.helpers import decode_core, decode_qualifier, chrome_time_to_datetime, normalize_url
from app.intent import compute_intent_score
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

CACHE_PATHS = {
      "chrome": pathlib.Path.home() / "AppData/Local/Google/Chrome/User Data/Default/Cache/Cache_Data",
      "edge":   pathlib.Path.home() / "AppData/Local/Microsoft/Edge/User Data/Default/Cache/Cache_Data",
      "brave":  pathlib.Path.home() / "AppData/Local/BraveSoftware/Brave-Browser/User Data/Default/Cache/Cache_Data",
      "opera":  pathlib.Path.home() / "AppData/Roaming/Opera Software/Opera Stable/Cache/Cache_Data",
}


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

      cached: bool = False
      response_code: Optional[int] = None       
      content_type: Optional[str] = None        
      content_language: Optional[str] = None     
      is_personalized: bool = False              
      is_no_store: bool = False                  
      cache_age_seconds: Optional[int] = None   
      last_modified: Optional[str] = None        
      asset_count: int = 0                      
      total_bytes: int = 0 

      @property
      def domain(self):
            return urlparse(self.url).netloc

      @property
      def is_error(self):
            return self.response_code is not None and self.response_code >= 400                      



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
