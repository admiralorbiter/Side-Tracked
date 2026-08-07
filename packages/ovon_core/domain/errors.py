"""Typed domain exceptions for OVON Core."""


class DomainError(Exception):
    """Base exception for all OVON domain errors."""

    pass


class InvalidCoordinateError(DomainError):
    """Raised when latitude/longitude values are invalid or zero."""

    pass


class MissingAttributionError(DomainError):
    """Raised when a media asset is instantiated without mandatory licensing/attribution metadata."""

    pass


class InvalidTimeBudgetError(DomainError):
    """Raised when a loop request specifies an unsupported walking duration."""

    pass


class TaxonNotFoundError(DomainError):
    """Raised when a species identifier cannot be resolved to a canonical TaxonRef."""

    pass


class NoFeasibleLoopError(DomainError):
    """Raised when candidate generator finds no budget-compliant loops for a request."""

    pass
