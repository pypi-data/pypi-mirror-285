"""Utility functions for QuClo."""

import os
from datetime import datetime, timedelta
from pyqir import Module, Context

CONFIG_FILE = os.path.expanduser("~/.quclo_config")
QUCLO_API_URL = "https://quclo.com/api/"


def duration_to_expires_at(duration: int | None) -> str | None:
    """Convert a duration to an expiration date."""
    if duration is None:
        return None
    return (datetime.now() + timedelta(days=duration)).isoformat()


def check_qir(qir: str | bytes) -> bool:
    """Check if the QIR is valid."""
    try:
        Module.from_ir(Context(), qir)
        return True
    except:
        try:
            Module.from_bitcode(Context(), qir)
            return True
        except:
            return False
