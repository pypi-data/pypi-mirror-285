"""Module for login to the server."""

import json
import os
from datetime import datetime, timedelta

import requests
import rich
import rich_click as click
from requests import codes

from oxpecker import API_ENDPOINTS, API_URL, WORK_DIR
from oxpecker.utils import retry_if_network_error


@click.command()
@click.option("--username", "-u", required=True, help="""Username of the service.""")
@click.option(
    "--password",
    "-p",
    required=True,
    prompt=True,
    prompt_required=False,
    hide_input=True,
    help="""Password of the service. If not provided, it will ask for input.""",
)
@click.pass_context
@retry_if_network_error()
def login(ctx, username, password):
    """Login to Oxpecker service."""
    if ctx.find_root().params["debug"]:
        click.echo(username)
    r = requests.post(
        f"{API_URL}{API_ENDPOINTS['login']}",
        json={"userName": username, "password": password},
        verify=not ctx.find_root().params["insecure_skip_tls_verify"],
        timeout=30,
    )
    if r.status_code == codes.ok:  # pylint: disable=no-member
        expires_in = r.json().get("expiresIn", 0)
        refresh_expires_in = r.json().get("refreshExpiresIn", 0)
        current_time = datetime.now()

        # Convert expiresIn and refreshExpiresIn to local datetime
        token_data = r.json()
        token_data["expiresIn"] = (
            current_time + timedelta(seconds=expires_in)
        ).strftime("%Y-%m-%d %H:%M:%S")
        token_data["refreshExpiresIn"] = (
            current_time + timedelta(seconds=refresh_expires_in)
        ).strftime("%Y-%m-%d %H:%M:%S")

        with open(
            token_file_path := WORK_DIR / "token", mode="w", encoding="utf-8"
        ) as cf:
            rich.print_json(json.dumps(token_data))
            json.dump(token_data, cf, indent=4)
        os.chmod(token_file_path, 0o600)
    else:
        click.secho(f"{r.status_code}: {r.request.method} {r.url}", fg="red", bold=True)
        ctx.abort()
