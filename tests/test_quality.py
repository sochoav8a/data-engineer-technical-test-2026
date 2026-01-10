from pipeline.models import ExtractionResult, MineralReserve
from pipeline.quality import apply_quality_checks


def test_filter_invalid_reserve_categories():
    result = ExtractionResult(reserves=[MineralReserve(category="Measured")])
    checked, metrics, warnings = apply_quality_checks(result, sections={"reserves"})

    assert checked.reserves == []
    assert metrics["reserves_count"] == 0
    assert any("reserve category filtered" in warning for warning in warnings)


def test_keeps_valid_reserves_and_filters_invalid():
    result = ExtractionResult(
        reserves=[
            MineralReserve(category="Proven + Probable"),
            MineralReserve(category="Indicated"),
        ]
    )
    checked, metrics, warnings = apply_quality_checks(result, sections={"reserves"})

    assert len(checked.reserves) == 1
    assert checked.reserves[0].category == "Proven + Probable"
    assert metrics["reserves_count"] == 1
    assert any("reserve category filtered" in warning for warning in warnings)


def test_flags_missing_economics_values():
    result = ExtractionResult()
    checked, metrics, warnings = apply_quality_checks(result, sections={"economics"})

    assert checked.economics is not None
    assert metrics["economics_has_values"] is False
    assert any("economics missing numeric values" in warning for warning in warnings)
