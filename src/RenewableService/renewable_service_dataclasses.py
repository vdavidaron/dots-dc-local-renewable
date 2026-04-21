from dataclasses import dataclass
from typing import List

@dataclass
class DayAheadRenewablesOutput:
    planned_generation_DA : str | None = None

@dataclass
class RealTimeRenewablesOutput:
    potential_available_generation_ID : float | None = None
    supplied_power_ID : float | None = None

