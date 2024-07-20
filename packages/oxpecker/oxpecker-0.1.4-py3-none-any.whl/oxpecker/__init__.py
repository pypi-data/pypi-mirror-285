"""Basic setup for oxpecker package."""

import datetime
import json
import logging
import os
import shutil
from pathlib import Path

import requests
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(usecwd=True))

host = os.environ.get("OXPECKER_HOST", "oxpecker.entropass.com")
port = os.environ.get("OXPECKER_PORT", 443)
API_URL = f"https://{host}:{port}/oxpecker/api/v1/"
WS_URL = f"wss://{host}:{port}/oxpecker-client-connect"

wstunnel_host = os.environ.get("OXPECKER_WSTUNNEL_HOST", default=host)
wstunnel_port = os.environ.get("OXPECKER_WSTUNNEL_PORT", default=443)
WS_TUNNEL_URL = f"wss://{wstunnel_host}:{wstunnel_port}"

API_ENDPOINTS = {
    "login": "auth/login",
    "upload": "files/upload",
    "task_create": "tasks",
    "task_list": "tasks/search",
    "file_check": "files/check-exist",
    "task_inspect": "tasks",
}

LANGUAGES = [
    "c",
    "cpp",
    "csharp",
    "go",
    "java",
    "kotlin",
    "javascript",
    "typescript",
    "python",
    "ruby",
    "swift",
]

WORK_DIR = Path("~/.oxpecker").expanduser()
WORK_DIR.mkdir(parents=True, exist_ok=True)

if not (CODEQL_EXE := shutil.which("codeql")):
    logging.warning("`codeql` is not found; many commands would not work.")

try:
    auth = {"Authorization": (token := os.environ.get("OXPECKER_TOKEN", ""))}
    if not token:
        with open(WORK_DIR / "token", encoding="utf-8") as tf:
            auth = {"Authorization": f"Bearer {json.load(tf)['accessToken']}"}
except (OSError, FileNotFoundError, json.JSONDecodeError):
    logging.warning(
        "Oxpecker token not found; many commands would not work.\n"
        "Use `oxpecker login` to get the token.\n"
    )
    auth = {"Authorization": "INVALID TOKEN"}


class OxpeckerAuthSession(requests.Session):
    """Session class for Oxpecker that handles automatic token refresh."""

    def request(self, *args, **kwargs):
        response = super().request(*args, **kwargs)
        if response.status_code == 401:
            self.refresh_access_token()
            # Retry the original request with the new token
            response = super().request(*args, **kwargs)
        return response

    def refresh_token_if_needed(self):
        """Refresh the session token if it is close to expiring."""
        with open(WORK_DIR / "token", encoding="utf-8") as token_file:
            token_data = json.load(token_file)
        token_expiry_str = token_data.get("expiresIn")
        if token_expiry_str:
            token_expiry = datetime.datetime.strptime(
                token_expiry_str, "%Y-%m-%d %H:%M:%S"
            )
            if (token_expiry - datetime.datetime.now()).total_seconds() < 30:
                self.refresh_access_token(token_data["refreshToken"])

    def refresh_access_token(self, refresh_token=None):
        """Refresh the access token using the provided refresh token."""
        if not refresh_token:
            with open(WORK_DIR / "token", encoding="utf-8") as token_file:
                token_data = json.load(token_file)
                refresh_token = token_data["refreshToken"]

        refresh_url = f"{API_URL}auth/exchange-token"
        r = requests.post(refresh_url, json={"refreshToken": refresh_token}, timeout=30)
        if r.status_code == requests.codes.ok:  # pylint: disable=no-member
            new_token_data = r.json()
            current_time = datetime.datetime.now()
            # Convert expiresIn and refreshExpiresIn to local datetime
            expires_in = new_token_data.get("expiresIn", 0)
            refresh_expires_in = new_token_data.get("refreshExpiresIn", 0)
            new_token_data["expiresIn"] = (
                current_time + datetime.timedelta(seconds=expires_in)
            ).strftime("%Y-%m-%d %H:%M:%S")
            new_token_data["refreshExpiresIn"] = (
                current_time + datetime.timedelta(seconds=refresh_expires_in)
            ).strftime("%Y-%m-%d %H:%M:%S")
            with open(WORK_DIR / "token", mode="w", encoding="utf-8") as cf:
                json.dump(new_token_data, cf, indent=4)
            self.headers.update(
                {"Authorization": f"Bearer {new_token_data['accessToken']}"}
            )


session = OxpeckerAuthSession()
session.headers.update(auth)
