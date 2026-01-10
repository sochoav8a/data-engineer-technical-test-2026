from pipeline.embeddings import EmbeddingSettings, EmbeddingStore
from pipeline.selector import SECTION_CONFIGS, select_pages


def test_select_pages_skips_toc(tmp_path):
    pages = [
        "Table of Contents\n....\n1. Intro\n2. Summary",
        "Mineral Reserves Table 5-1\nProven Probable 100 0.5",
        "Background text without signals",
    ]
    config = SECTION_CONFIGS["reserves"]
    embed_settings = EmbeddingSettings(
        enabled=False,
        api_key=None,
        model_name="test",
        max_chars=500,
        max_pages=10,
    )
    embed_store = EmbeddingStore(tmp_path, embed_settings)

    selected = select_pages(pages, config, embed_store, embed_settings)
    assert 0 not in selected
    assert 1 in selected
