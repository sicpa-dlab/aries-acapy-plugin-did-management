from dataclasses import dataclass


@dataclass(frozen=True)
class PreviousKey:
    index: int
    key: bytes
