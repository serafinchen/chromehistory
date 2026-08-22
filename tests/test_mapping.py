from datetime import datetime
import pytest
from app.cache import CacheEntry
from app.history import HistoryEntry
from app.mapping import MatchType, MatchedVisit, _pick_html, match_history_with_cache

@pytest.fixture
def history_entry() -> HistoryEntry:
    return HistoryEntry(
        rec_id=1,
        url="https://example.com/article",
        title="Article",
        visit_time=datetime(2026, 1, 1, 12, 0),
        visit_duration=3.5,
        from_visit_id=None,
        opener_visit_id=None,
        transition_core="LINK",
        transition_qualifier="",
    )


def test_pick_html_prefers_html_entry_over_other_asset() -> None:
    image = CacheEntry(
        url="https://example.com/article",
        domain="example.com",
        raw_key="image",
        content_type="image/png",
    )
    page = CacheEntry(
        url="https://example.com/article",
        domain="example.com",
        raw_key="page",
        content_type="text/html; charset=utf-8",
    )

    assert _pick_html([image, page]) is page


def test_match_exact_url_uses_html_metadata_and_aggregates_cache_flags(
    history_entry: HistoryEntry,
) -> None:
    asset = CacheEntry(
        url=history_entry.url,
        domain=history_entry.domain,
        raw_key="asset",
        response_code=200,
        content_type="image/png",
        content_length=20,
        is_probably_personalized=True,
    )
    page = CacheEntry(
        url=history_entry.url,
        domain=history_entry.domain,
        raw_key="page",
        response_code=404,
        content_type="text/html; charset=utf-8",
        content_language="de",
        content_length=100,
        is_no_store=True,
        age=30,
        last_modified="Wed, 01 Jan 2026 10:00:00 GMT",
    )
    other_domain_asset = CacheEntry(
        url="https://example.com/site.css",
        domain=history_entry.domain,
        raw_key="css",
        content_length=50,
    )

    visit = match_history_with_cache(
        [history_entry], [asset, page, other_domain_asset]
    )[0]

    assert visit.match_type is MatchType.EXACT_URL
    assert visit.matched_cache_entries == [asset, page]
    assert visit.raw_key == "page"
    assert visit.response_code == 404
    assert visit.content_type == "text/html; charset=utf-8"
    assert visit.is_html is True
    assert visit.is_error is True
    assert visit.is_probably_personalized is True
    assert visit.is_no_store is True
    assert visit.domain_asset_count == 3
    assert visit.domain_total_bytes == 170


def test_match_without_exact_url_returns_unmatched_visit(history_entry: HistoryEntry) -> None:
    same_domain_asset = CacheEntry(
        url="https://example.com/other",
        domain=history_entry.domain,
        raw_key="other",
        content_length=10,
    )

    visit = match_history_with_cache([history_entry], [same_domain_asset])[0]

    assert visit.match_type is MatchType.NONE
    assert visit.matched_cache_entries == []
    assert visit.response_code is None
    assert visit.domain_asset_count == 0
    assert visit.domain_total_bytes == 0
    assert visit.is_error is False


@pytest.mark.parametrize("response_code, expected", [(None, False), (399, False), (400, True)])
def test_is_error_only_for_http_error_statuses(
    history_entry: HistoryEntry, response_code: int | None, expected: bool
) -> None:
    visit = MatchedVisit(
        history=history_entry,
        match_type=MatchType.EXACT_URL,
        response_code=response_code,
    )

    assert visit.is_error is expected
