from dataclasses import dataclass


@dataclass(slots=True)
class AntiAirCutIn:
    id: int = 0
    rateCorr: float = 1
    fixCorrA: int = 1
    fixCorrB: int = 0
    rate: float = 1
