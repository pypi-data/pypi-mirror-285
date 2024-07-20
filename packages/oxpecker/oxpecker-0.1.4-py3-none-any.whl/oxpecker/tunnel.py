"""
This module provides functionality for creating a tunnel that's accessible from the server.
"""

import subprocess
from pathlib import Path

import rich_click as click

from oxpecker import WS_TUNNEL_URL, auth
from oxpecker.utils import run_command


@click.command(hidden=True)
@click.pass_context
@click.option("--local-host", default="localhost", show_default=True)
@click.option("--local-port", default=22, show_default=True)
@click.option(
    "--remote-proto", default="tcp", help="Remote protocol.", show_default=True
)
@click.option(
    "--remote-host", default="127.0.0.1", help="Remote host.", show_default=True
)
@click.option(
    "--remote-port",
    help="Remote port. Default is local_port + 8000.",
    show_default=True,
)
def tunnel(
    ctx: click.Context,
    local_host: str,
    local_port: int,
    remote_proto: str,
    remote_host: str,
    remote_port: int,
) -> None:
    """Create a tunnel that's accessible from the server."""
    if not remote_port:
        remote_port = min(local_port + 8000, 65535)
    wstunnel_vendor_exec = Path(__file__).parent / "vendor" / "wstunnel"
    try:
        subprocess.run([wstunnel_vendor_exec, "-V"], check=True)
    except OSError as e:
        click.echo(f"Error: {e}")
        wstunnel_exec = "wstunnel"
    else:
        wstunnel_exec = wstunnel_vendor_exec.as_posix()
    args = [
        wstunnel_exec,
        "client",
        "--http-upgrade-path-prefix",
        "proxy",
        "--http-headers",
        f"Authorization: {auth['Authorization']}",
        "--remote-to-local",
        f"{remote_proto}://{remote_host}:{remote_port}:{local_host}:{local_port}",
        WS_TUNNEL_URL,
    ]
    if ctx.find_root().params["debug"]:
        click.echo(f"Running command: {' '.join(args)}")
    run_command(args)
