import threading
from datetime import datetime

from app.store import LinkStore


def test_new_link_has_no_clicks():
    link = LinkStore().add("https://glassflow.ai")
    assert link.clicks == 0
    assert link.last_clicked_at is None


def test_record_click_counts_and_stamps_the_link():
    store = LinkStore()
    link = store.add("https://glassflow.ai")

    first = store.record_click(link.code)
    assert first is link
    assert first.clicks == 1
    assert isinstance(first.last_clicked_at, datetime)
    assert first.last_clicked_at.tzinfo is not None
    first_at = first.last_clicked_at

    second = store.record_click(link.code)
    assert second.clicks == 2
    assert second.last_clicked_at >= first_at


def test_record_click_on_unknown_code_returns_none():
    assert LinkStore().record_click("nope00") is None


def test_snapshot_is_an_independent_copy():
    store = LinkStore()
    link = store.add("https://glassflow.ai")
    store.record_click(link.code)

    copy = store.snapshot(link.code)
    assert copy == link
    assert copy is not link

    store.record_click(link.code)
    assert copy.clicks == 1
    assert link.clicks == 2


def test_snapshot_of_unknown_code_returns_none():
    assert LinkStore().snapshot("nope00") is None


def test_concurrent_clicks_are_all_counted():
    # Smoke test: it may pass even without the lock; the lock stays in the store regardless.
    store = LinkStore()
    link = store.add("https://glassflow.ai")

    def click() -> None:
        for _ in range(1000):
            store.record_click(link.code)

    threads = [threading.Thread(target=click) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert store.snapshot(link.code).clicks == 8000
