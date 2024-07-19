from dataclasses import dataclass


@dataclass(slots=True)
class ContactRate:
    startRate: float
    contact120: float
    contact117: float
    contact112: float
    sumRate: float
