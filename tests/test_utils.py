from pipeline.utils import (
    NO_ECONOMICS_PATTERNS,
    NO_RESERVES_PATTERNS,
    clamp_text,
    extract_relevant_page_snippets,
    find_pages_with_patterns,
    is_toc_page,
    normalize_whitespace,
)


def test_is_toc_page_detection():
    toc = "Table of Contents\n....\n1. Intro\n2. Summary\n3. More"
    assert is_toc_page(toc)
    non_toc = "Executive Summary\nProject overview and objectives"
    assert not is_toc_page(non_toc)


def test_normalize_whitespace_and_clamp():
    text = "a\n\n  b\t c"
    assert normalize_whitespace(text) == "a b c"
    assert clamp_text("abcdef", 3) == "abc"


def test_extract_relevant_page_snippets():
    context = (
        "Page 1:\nintro text\nmore intro\n\n"
        "Page 2:\nmineral reserves table 5-1\n100 1.2\n\n"
        "Page 3:\nother content\n"
    )
    focused = extract_relevant_page_snippets(context, ["mineral reserves"])
    assert "Page 2:" in focused
    assert "mineral reserves" in focused.lower()
    assert "Page 1:" not in focused


def test_find_pages_with_patterns():
    pages = [
        "General discussion of the project.",
        "No reserves conforming to CIM standards have been estimated.",
        "Capital and operating costs are not determined at this time.",
    ]
    reserves = find_pages_with_patterns(pages, NO_RESERVES_PATTERNS)
    economics = find_pages_with_patterns(pages, NO_ECONOMICS_PATTERNS)
    assert reserves == [2]
    assert economics == [3]
