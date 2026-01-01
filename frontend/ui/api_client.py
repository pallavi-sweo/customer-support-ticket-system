from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()


@dataclass
class ApiError(Exception):
    status_code: int
    message: str
    code: str | None = None
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

    def request(
        self,
        method: str,
        path: str,
        *,
        json: Any | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        url = f"{self.base_url}{path}"
        resp = requests.request(
            method=method,
            url=url,
            json=json,
            params=params,
            headers=self._headers(),
            timeout=self.timeout,
        )
        return self._handle(resp)

    def _handle(self, resp: requests.Response) -> Any:
        try:
            data = resp.json()
        except Exception:  # noqa: BLE001
            data = resp.text

        if resp.status_code >= 400:
            code = None
            message = None

            if isinstance(data, dict):
                # New domain error format: {"error": {"code": "...", "message": "..."}}
                if "error" in data and isinstance(data["error"], dict):
                    code = data["error"].get("code")
                    message = data["error"].get("message")
                # FastAPI default: {"detail": "..."}
                message = message or data.get("detail") or data.get("message")

            raise ApiError(
                status_code=resp.status_code,
                message=message or str(data),
                code=code,
                details=data,
            )

        return data

    # -------- Auth --------
    def signup(self, email: str, password: str) -> dict[str, Any]:
        return self.request(
            "POST", "/auth/signup", json={"email": email, "password": password}
        )

    def login(self, email: str, password: str) -> dict[str, Any]:
        return self.request(
            "POST", "/auth/login", json={"email": email, "password": password}
        )

    # -------- Tickets --------
    def create_ticket(
        self, subject: str, description: str, priority: str
    ) -> dict[str, Any]:
        return self.request(
            "POST",
            "/tickets",
            json={"subject": subject, "description": description, "priority": priority},
        )

    def list_tickets(
        self,
        page: int,
        page_size: int,
        status: str | None = None,
        priority: str | None = None,
        created_from: str | None = None,
        created_to: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        if status:
            params["status"] = status
        if priority:
            params["priority"] = priority
        if created_from:
            params["created_from"] = created_from
        if created_to:
            params["created_to"] = created_to
        return self.request("GET", "/tickets", params=params)

    def get_ticket(self, ticket_id: int) -> dict[str, Any]:
        return self.request("GET", f"/tickets/{ticket_id}")

    # -------- Replies --------
    def list_replies(
        self, ticket_id: int, page: int = 1, page_size: int = 20
    ) -> dict[str, Any]:
        return self.request(
            "GET",
            f"/tickets/{ticket_id}/replies",
            params={"page": page, "page_size": page_size},
        )

    def create_reply(self, ticket_id: int, message: str) -> dict[str, Any]:
        return self.request(
            "POST", f"/tickets/{ticket_id}/replies", json={"message": message}
        )

    # -------- Admin --------
    def update_status(self, ticket_id: int, status: str) -> dict[str, Any]:
        return self.request(
            "PUT", f"/admin/tickets/{ticket_id}/status", json={"status": status}
        )


def get_api_base_url() -> str:
    return os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
