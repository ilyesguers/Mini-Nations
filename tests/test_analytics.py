from types import SimpleNamespace

from app.analytics import summarize_rounds


def row(outcome, multiplier=None):
    return SimpleNamespace(outcome=outcome, multiplier=multiplier)


def test_summary_calculates_historical_statistics():
    result = summarize_rounds([
        row("win", 2.0),
        row("loss", 1.5),
        row("win", 3.0),
    ])
    assert result.total == 3
    assert result.wins == 2
    assert result.losses == 1
    assert round(result.win_rate, 2) == 66.67
    assert round(result.average_multiplier, 2) == 2.17
    assert result.median_multiplier == 2.0
    assert result.highest_multiplier == 3.0


def test_empty_history_is_safe():
    result = summarize_rounds([])
    assert result.total == 0
    assert result.win_rate == 0
    assert result.average_multiplier is None
    assert result.median_multiplier is None
    assert result.highest_multiplier is None


def test_invalid_and_non_finite_multipliers_are_ignored():
    result = summarize_rounds([
        row("win", 2.0),
        row("loss", float("inf")),
        row("win", float("nan")),
        row("loss", -1),
        row("win", None),
    ])
    assert result.total == 5
    assert result.wins == 3
    assert result.losses == 2
    assert result.average_multiplier == 2.0
    assert result.highest_multiplier == 2.0
