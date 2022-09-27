from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from catalog.catalog import Column


@dataclass
class Statistic:
    upper_bound: float
    lower_bound: float
    frequency: float
    domain: Tuple[float, float]


class LogicalProfile:
    def __init__(self) -> None:
        self.profile: Dict[Column, Statistic] = {}
        self.frequency: Optional[float] = None

    def set_stats(self, col: Column, frequency: float) -> None:
        # Right now, we only support frequency
        self.profile[col] = Statistic(0, 0, frequency, (0, 0))
        if self.frequency != None:
            assert self.frequency == frequency
        self.frequency = frequency

    def get_stats(self, col: Column) -> Statistic:
        return self.profile[col]

    def get_frequency(self) -> float:
        assert self.frequency is not None
        return self.frequency
