from datetime import datetime, timedelta
import pandas as pd
from app.cache import CacheEntry
from app.data import _visit_to_row, dashboard_summary, filter_visits
from app.history import HistoryEntry
from app.mapping import MatchType, MatchedVisit
import app.data as data


def make_history_entry(*, rec_id: int = 1, url: str = "https://example.com/page") -> HistoryEntry:
    return HistoryEntry(
        rec_id=rec_id,
        url=url,
        title="Example",
        visit_time=datetime(2026, 1, 1, 9, 0),
        visit_duration=12.0,
        from_visit_id=None,
        opener_visit_id=None,
        transition_core="LINK",
        transition_qualifier="",
    )


def test_visit_to_row_flattens_history_and_match_information() -> None:
    history = make_history_entry()
    visit = MatchedVisit(
        history=history,
        match_type=MatchType.EXACT_URL,
        response_code=500,
        content_type="text/html",
        is_html=True,
        raw_key="cache-key",
        domain_asset_count=2,
        domain_total_bytes=256,
    )

    row = _visit_to_row(visit)

    assert row["rec_id"] == 1
    assert row["url"] == history.url
    assert row["match_type"] == "exact_url"
    assert row["raw_key"] == "cache-key"
    assert row["is_error"] is True
    assert row["domain_asset_count"] == 2
    assert row["domain_total_bytes"] == 256
    assert "matched_cache_entries" not in row


def test_filter_visits_returns_all_or_only_the_requested_session() -> None:
    df = pd.DataFrame({"session_id": [0, 1, 1], "url": ["a", "b", "c"]})

    assert filter_visits(df, -1).equals(df)
    assert filter_visits(df, 1)["url"].tolist() == ["b", "c"]


def test_dashboard_summary_counts_visits_and_distinct_sessions() -> None:
    df = pd.DataFrame({"session_id": [3, 3, 7]})

    assert dashboard_summary(df) == {"total_visits": 3, "total_sessions": 2}


def test_load_df_builds_sorted_dataframe_from_the_data_sources(monkeypatch) -> None:

    early = make_history_entry(rec_id=1, url="https://example.com/early")
    late = make_history_entry(rec_id=2, url="https://example.com/late")
    early = HistoryEntry(**{**early.__dict__, "visit_time": early.visit_time})
    late = HistoryEntry(**{**late.__dict__, "visit_time": late.visit_time + timedelta(minutes=5)})
    cache_entries = [
        CacheEntry(
            url=early.url,
            domain=early.domain,
            raw_key="early-cache",
            response_code=200,
            content_type="text/html",
            content_length=40,
        )
    ]
    profile = object()

    #dummy data instead of real data
    monkeypatch.setattr(data, "get_profile", lambda: profile)
    monkeypatch.setattr(data, "load_history_entries", lambda path: [early, late])
    monkeypatch.setattr(data, "load_cache_entries", lambda received_profile: cache_entries)

    df = data.load_df()

    assert df["rec_id"].tolist() == [1, 2]
    assert df["domain"].tolist() == ["example.com", "example.com"]
    assert df["duration"].tolist() == [12.0, 12.0]
    assert df["match_type"].tolist() == ["exact_url", "none"]
    assert df["session_id"].tolist() == [0, 0]
