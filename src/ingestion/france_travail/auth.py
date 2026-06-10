"""Authentication helpers for France Travail API.

This module is intentionally source-specific and contains no database-loading
logic. It reads credentials from environment variables, requests an OAuth2
access token, and caches it in memory until shortly before expiration.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import os
from typing import Any

import requests


DEFAULT_TOKEN_URL = (
    "https://entreprise.francetravail.fr/connexion/oauth2/access_token"
    "?realm=/partenaire"
)
DEFAULT_SCOPE = "api_offresdemploiv2 o2dsoffre"


class FranceTravailAuthError(RuntimeError):
    """Raised when France Travail authentication fails."""


@dataclass(frozen=True)
class FranceTravailCredentials:
    """Credentials required for France Travail OAuth2 client-credentials flow."""

    client_id: str
    client_secret: str
    token_url: str = DEFAULT_TOKEN_URL
    scope: str = DEFAULT_SCOPE

    @classmethod
    def from_env(cls) -> "FranceTravailCredentials":
        """Build credentials from environment variables.

        Expected variables:
        - FRANCE_TRAVAIL_CLIENT_ID
        - FRANCE_TRAVAIL_CLIENT_SECRET

        Optional variables:
        - FRANCE_TRAVAIL_TOKEN_URL
        - FRANCE_TRAVAIL_SCOPE
        """

        client_id = os.getenv("FRANCE_TRAVAIL_CLIENT_ID")
        client_secret = os.getenv("FRANCE_TRAVAIL_CLIENT_SECRET")

        missing = [
            name
            for name, value in {
                "FRANCE_TRAVAIL_CLIENT_ID": client_id,
                "FRANCE_TRAVAIL_CLIENT_SECRET": client_secret,
            }.items()
            if not value
        ]
        if missing:
            raise FranceTravailAuthError(
                "Missing required France Travail environment variables: "
                + ", ".join(missing)
            )

        return cls(
            client_id=client_id or "",
            client_secret=client_secret or "",
            token_url=os.getenv("FRANCE_TRAVAIL_TOKEN_URL", DEFAULT_TOKEN_URL),
            scope=os.getenv("FRANCE_TRAVAIL_SCOPE", DEFAULT_SCOPE),
        )


@dataclass(frozen=True)
class AccessToken:
    """Access token value with expiration metadata."""

    token: str
    token_type: str
    expires_at: datetime

    def is_valid(self, safety_window_seconds: int = 60) -> bool:
        """Return true if token is not close to expiration."""

        return datetime.now(timezone.utc) + timedelta(seconds=safety_window_seconds) < self.expires_at


class FranceTravailAuthenticator:
    """OAuth2 authenticator for France Travail API."""

    def __init__(
        self,
        credentials: FranceTravailCredentials | None = None,
        timeout_seconds: int = 30,
    ) -> None:
        self.credentials = credentials or FranceTravailCredentials.from_env()
        self.timeout_seconds = timeout_seconds
        self._cached_token: AccessToken | None = None

    def get_access_token(self) -> AccessToken:
        """Return a cached valid token or request a new one."""

        if self._cached_token and self._cached_token.is_valid():
            return self._cached_token

        payload: dict[str, str] = {
            "grant_type": "client_credentials",
            "client_id": self.credentials.client_id,
            "client_secret": self.credentials.client_secret,
        }
        if self.credentials.scope:
            payload["scope"] = self.credentials.scope

        try:
            response = requests.post(
                self.credentials.token_url,
                data=payload,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                },
                timeout=self.timeout_seconds,
            )
        except requests.RequestException as exc:
            raise FranceTravailAuthError(f"France Travail token request failed: {exc}") from exc

        if response.status_code >= 400:
            raise FranceTravailAuthError(
                "France Travail token request returned "
                f"HTTP {response.status_code}: {response.text[:500]}"
            )

        try:
            payload_json: dict[str, Any] = response.json()
        except ValueError as exc:
            raise FranceTravailAuthError("France Travail token response is not valid JSON") from exc

        token = payload_json.get("access_token")
        if not token:
            raise FranceTravailAuthError("France Travail token response does not contain access_token")

        expires_in = int(payload_json.get("expires_in", 3600))
        token_type = str(payload_json.get("token_type", "Bearer"))
        self._cached_token = AccessToken(
            token=str(token),
            token_type=token_type,
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=expires_in),
        )
        return self._cached_token

    def get_authorization_header(self) -> dict[str, str]:
        """Return a safe Authorization header for API requests.

        Do not persist this header in raw.api_requests.
        """

        access_token = self.get_access_token()
        return {"Authorization": f"{access_token.token_type} {access_token.token}"}
