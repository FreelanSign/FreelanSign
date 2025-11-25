# apps/user/adapters/system_clock.py
"""
SystemClock implementation of Clock port.

@author: @Bertrand2808
@since: 2025-11-25
@version: 1.0
"""
from datetime import datetime

from django.utils import timezone

from apps.user.application.ports.clock import Clock


class SystemClock:
    """Production clock using Django timezone."""

    def now(self) -> datetime:
        """Return current datetime."""
        return timezone.now()
