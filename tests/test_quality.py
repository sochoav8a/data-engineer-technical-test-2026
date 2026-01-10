from pipeline.models import ExtractionResult, MineralReserve
from pipeline.quality import apply_quality_checks


def test_filter_invalid_reserve_categories():
    result = ExtractionResult(reserves=[MineralReserve(category="Measured")])
    checked, metrics, warnings = apply_quality_checks(result, sections={"reserves"})

    assert checked.reserves == []
    assert metrics["reserves_count"] == 0
    assert any("reserve category filtered" in warning for warning in warnings)
