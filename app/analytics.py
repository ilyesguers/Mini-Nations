from dataclasses import dataclass
from statistics import mean, median
from typing import Iterable


@dataclass(frozen=True)
class RoundSummary:
    total: int
    wins: int
    losses: int
    win_rate: float
    average_multiplier: float | None
    median_multiplier: float | None
    highest_multiplier: float | None


def summarize_rounds(rows: Iterable[object]) -> RoundSummary:
    items = list(rows)
    wins = sum(1 for row in items if row.outcome == "win")
    losses = sum(1 for row in items if row.outcome == "loss")
    multipliers = [float(row.multiplier) for row in items if row.multiplier is not None and float(row.multiplier) > 0]
    total = len(items)
    return RoundSummary(
        total=total, wins=wins, losses=losses,
        win_rate=(wins / total * 100) if total else 0.0,
        average_multiplier=mean(multipliers) if multipliers else None,
        median_multiplier=median(multipliers) if multipliers else None,
        highest_multiplier=max(multipliers) if multipliers else None,
    )
