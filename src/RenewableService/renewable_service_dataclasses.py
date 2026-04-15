from dataclasses import dataclass
from typing import List

@dataclass
class DayAheadRenewablesOutput:
    planned_generation_da : str | None = None

@dataclass
class RealTimeRenewablesOutput:
    potential_available_generation_id : float | None = None
    supplied_power_id : float | None = None

