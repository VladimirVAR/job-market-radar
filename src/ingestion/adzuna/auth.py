"""Authentication helpers for Adzuna API.

Adzuna uses app_id + app_key passed as query parameters.
No OAuth or token caching is needed.
"""

from __future__ import annotations

from dataclasses import dataclass
import os


class AdzunaAuthError(RuntimeError):
    """Raised when Adzuna credentials are missing or invalid."""


@dataclass(frozen=True)
class AdzunaCredentials:
    """Credentials for Adzuna API (app_id + app_key query params)."""

    app_id: str
    app_key: str

    @classmethod
    def from_env(cls) -> "AdzunaCredentials":
        """Build credentials from environment variables.

        Expected variables:
        - ADZUNA_APP_ID
        - ADZUNA_APP_KEY
        """

        app_id = os.getenv("ADZUNA_APP_ID")
        app_key = os.getenv("ADZUNA_APP_KEY")

        missing = [
            name
            for name, value in {
                "ADZUNA_APP_ID": app_id,
                "ADZUNA_APP_KEY": app_key,
            }.items()
            if not value
        ]
        if missing:
            raise AdzunaAuthError(
                "Missing required Adzuna environment variables: " + ", ".join(missing)
            )

        return cls(app_id=app_id or "", app_key=app_key or "")

    def as_query_params(self) -> dict[str, str]:
        """Return auth params to inject into every API request."""

        return {"app_id": self.app_id, "app_key": self.app_key}
