from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class ApiError(Exception):
    status_code: int
    message: str
    details: Any | None = None


class ApiClient:
    def __init__(self, base_url: str, token: str | None = None, timeout: int = 20):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout

    def with_token(self, token: str | None) -> "ApiClient":
        return ApiClient(self.base_url, token=token, timeout=self.timeout)

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _handle(self, resp: requests.Response) -> Any:
        # Try JSON first
        try:
            data = resp.json()
        except Exception:  # noqa: BLE001
            data = resp.text

        if resp.status_code >= 400:
            message = None
            if isinstance(data, dict):
                message = data.get("detail") or data.get("message")
            raise ApiError(
                status_code=resp.status_code, message=message or str(data), details=data
            )

        return data

    # -------- Auth --------
    def signup(self, email: str, password: str) -> dict[str, Any]:
        url = f"{self.base_url}/auth/signup"
        resp = requests.post(
            url,
            json={"email": email, "password": password},
            headers=self._headers(),
            timeout=self.timeout,
        )
        return self._handle(resp)

    def login(self, email: str, password: str) -> dict[str, Any]:
        url = f"{self.base_url}/auth/login"
        resp = requests.post(
            url,
            json={"email": email, "password": password},
            headers=self._headers(),
            timeout=self.timeout,
        )
        return self._handle(resp)

    # -------- Tickets --------
    def create_ticket(
        self, subject: str, description: str, priority: str
    ) -> dict[str, Any]:
        url = f"{self.base_url}/tickets"
        resp = requests.post(
            url,
            json={"subject": subject, "description": description, "priority": priority},
            headers=self._headers(),
            timeout=self.timeout,
        )
        return self._handle(resp)

    def list_tickets(
        self,
        page: int,
        page_size: int,
        status: str | None = None,
        priority: str | None = None,
        created_from: str | None = None,
        created_to: str | None = None,
    ) -> dict[str, Any]:
        url = f"{self.base_url}/tickets"
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        if status:
            params["status"] = status
        if priority:
            params["priority"] = priority
        if created_from:
            params["created_from"] = created_from
        if created_to:
            params["created_to"] = created_to

        resp = requests.get(
            url, params=params, headers=self._headers(), timeout=self.timeout
        )
        return self._handle(resp)

    def get_ticket(self, ticket_id: int) -> dict[str, Any]:
        url = f"{self.base_url}/tickets/{ticket_id}"
        resp = requests.get(url, headers=self._headers(), timeout=self.timeout)
        return self._handle(resp)

    # -------- Replies --------
    def list_replies(self, ticket_id: int) -> list[dict[str, Any]]:
        url = f"{self.base_url}/tickets/{ticket_id}/replies"
        resp = requests.get(url, headers=self._headers(), timeout=self.timeout)
        return self._handle(resp)

    def create_reply(self, ticket_id: int, message: str) -> dict[str, Any]:
        url = f"{self.base_url}/tickets/{ticket_id}/replies"
        resp = requests.post(
            url,
            json={"message": message},
            headers=self._headers(),
            timeout=self.timeout,
        )
        return self._handle(resp)

    # -------- Admin --------
    def update_status(self, ticket_id: int, status: str) -> dict[str, Any]:
        url = f"{self.base_url}/admin/tickets/{ticket_id}/status"
        resp = requests.put(
            url, json={"status": status}, headers=self._headers(), timeout=self.timeout
        )
        return self._handle(resp)


def get_api_base_url() -> str:
    return os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
