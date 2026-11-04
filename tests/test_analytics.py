from math import inf, nan
from types import SimpleNamespace

from app.analytics import summarize_rounds


def test_summary_calculates_historical_statistics():
    rows = [
        SimpleNamespace(outcome="win", multiplier=2.0),
        SimpleNamespace(outcome="loss", multiplier=1.5),
        SimpleNamespace(outcome="win", multiplier=3.0),
    ]
    result = summarize_rounds(rows)
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
    rows = [
        SimpleNamespace(outcome="win", multiplier=2.0),
        SimpleNamespace(outcome="loss", multiplier=nan),
        SimpleNamespace(outcome="loss", multiplier=inf),
        SimpleNamespace(outcome="loss", multiplier=-inf),
        SimpleNamespace(outcome="win", multiplier=0),
        SimpleNamespace(outcome="loss", multiplier=-1),
        SimpleNamespace(outcome="loss", multiplier="not-a-number"),
        SimpleNamespace(outcome="win", multiplier=None),
    ]
    result = summarize_rounds(rows)
    assert result.total == 8
    assert result.average_multiplier == 2.0
    assert result.median_multiplier == 2.0
    assert result.highest_multiplier == 2.0
