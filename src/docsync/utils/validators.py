"""Small validation helpers used across DocSync."""

from typing import Any, Dict


def validate_esg_data(data: Dict[str, Any]) -> bool:
    """Validate ESG data structure minimally.

    Ensures the input is a dictionary. Additional validation can be added later.
    """

    if not isinstance(data, dict):
        raise ValueError("ESG data must be a dictionary")
    return True

__all__ = ["validate_esg_data"]

