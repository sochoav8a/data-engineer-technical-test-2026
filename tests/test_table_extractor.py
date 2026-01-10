from pipeline.table_extractor import build_table_context, filter_tables_for_section


def test_filter_tables_prefers_section_keywords():
    tables = [
        {"page": 1, "method": "camelot", "text": "Noise table\\nA,B,C\\nfoo,bar,baz"},
        {
            "page": 2,
            "method": "camelot",
            "text": "Mineral Resource Estimate\\nMeasured,Indicated,Inferred\\n100,1.2,3.4",
        },
        {
            "page": 3,
            "method": "pdfplumber",
            "text": "Capital Cost\\nCapex,US$\\n1000,2000",
        },
    ]

    resources = filter_tables_for_section(tables, "resources", max_tables=1)
    assert resources
    assert resources[0]["page"] == 2

    economics = filter_tables_for_section(tables, "economics", max_tables=1)
    assert economics
    assert economics[0]["page"] == 3


def test_build_table_context_labels_page_and_method():
    tables = [{"page": 5, "method": "pdfplumber", "text": "A,B\\n1,2"}]
    context = build_table_context(tables, max_rows=2, max_chars=100)
    assert "Page 5 (pdfplumber):" in context
    assert "A,B" in context
