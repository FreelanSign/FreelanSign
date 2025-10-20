# apps/quote/application/ports/clock.py
from __future__ import annotations
from typing import Protocol
from datetime import datetime

class Clock(Protocol):
    def now(self) -> datetime: ...
