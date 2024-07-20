"""Modules for processing files with the server."""

import rich_click as click
from requests import codes

from oxpecker import API_ENDPOINTS, API_URL, session
from oxpecker.utils import calculate_sha256, print_resp, retry_if_network_error


@click.command(hidden=True)
@click.argument("filename", type=click.Path())
@click.pass_context
@click.option(
    "-f",
    "--force-upload",
    is_flag=True,
    default=False,
    show_default=True,
    help="Upload file even if it already exists in the remote database.",
)
@retry_if_network_error()
def upload(ctx, filename, force_upload):
    """Upload file to server."""
    if ctx.find_root().params["debug"]:
        click.echo(filename)
        click.echo(f"{force_upload = }")

    sha256sum = calculate_sha256(filename)

    if not force_upload:
        # Check if file is on the server.
        r = session.post(
            f"{API_URL}{API_ENDPOINTS['file_check']}/{sha256sum}",
            verify=not ctx.find_root().params["insecure_skip_tls_verify"],
        )
        if r.status_code == codes["✓"]:
            click.echo(
                f"File already exists with sha256: {sha256sum}. Use --force-upload to override."
            )
        elif r.status_code == codes.not_found:  # pylint: disable=no-member
            _upload_file(filename, ctx)
        else:
            print_resp(ctx, r)
    else:
        _upload_file(filename, ctx)


@retry_if_network_error()
def _upload_file(filename: str, ctx: click.Context) -> None:
    with open(filename, "rb") as f:
        r = session.post(
            f"{API_URL}{API_ENDPOINTS['upload']}",
            files={"file": f},
            verify=not ctx.find_root().params["insecure_skip_tls_verify"],
        )
    print_resp(ctx, r)
