from pipeline.storage import _normalize_pages


def test_normalize_pages():
    raw = "Page 1; Page 2|Page 3/4"
    assert _normalize_pages(raw) == "1, 2, 3, 4"
    assert _normalize_pages(None) is None
