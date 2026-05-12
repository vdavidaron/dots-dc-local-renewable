from dataclasses import dataclass
from typing import List

@dataclass
class DayAheadRenewablesOutput:
    planned_generation_DA : list[float] | None = None

@dataclass
class RenewableStateOutput:
    potential_available_generation_ID : float | None = None
    supplied_power_ID : float | None = None

