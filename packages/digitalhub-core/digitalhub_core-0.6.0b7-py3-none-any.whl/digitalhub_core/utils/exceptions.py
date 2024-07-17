from __future__ import annotations


class StoreError(Exception):
    """
    Raised when incontered errors on stores.
    """


class BackendError(Exception):
    """
    Raised when incontered errors from backend.
    """


class EntityError(Exception):
    """
    Raised when incontered errors on entities.
    """
