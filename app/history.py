import pathlib
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

from ccl_chromium_reader import ccl_chromium_history
from app.analytics import decode_core, decode_qualifier
from app.helpers import chrome_time_to_datetime, normalize_url

@dataclass
class HistoryEntry:
      rec_id: int
      url: str
      title: str
      visit_time: str
      visit_duration: float
      from_visit_id: Optional[int]
      opener_visit_id: Optional[int]
      transition_core: str
      transition_qualifier: str

      @property
      def domain(self) -> str:
            return urlparse(self.url).netloc


def load_history_entries(profile_path: pathlib.Path) -> list[HistoryEntry]:
      db_path = pathlib.Path(profile_path) / "History"

      with ccl_chromium_history.HistoryDatabase(db_path) as history_db:
            raw_records = list(history_db.iter_history_records(None))

      entries: list[HistoryEntry] = []
      for h in raw_records:
            visit_time = chrome_time_to_datetime(h.visit_time)
            entries.append(
                  HistoryEntry(
                        rec_id=h.rec_id,
                        url=normalize_url(h.url),
                        title=h.title or "Untitled",
                        visit_time=visit_time.isoformat(),
                        visit_duration=h.visit_duration.total_seconds() if h.visit_duration else 0,
                        from_visit_id=h.from_visit_id,
                        opener_visit_id=h.opener_visit_id,
                        transition_core=decode_core(h.transition.core),
                        transition_qualifier=decode_qualifier(h.transition.qualifier),
                  )
            )

      return entries
