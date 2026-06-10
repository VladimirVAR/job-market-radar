"""Shared exception classes for Job Market Radar pipelines."""


class JobMarketRadarError(RuntimeError):
    """Base project exception."""


class ConfigurationError(JobMarketRadarError):
    """Raised when required configuration is missing or invalid."""


class DatabaseError(JobMarketRadarError):
    """Raised when database operations fail."""


class RawLoadingError(JobMarketRadarError):
    """Raised when raw loading fails."""
