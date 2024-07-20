"""Module for managing Oxpecker tasks."""

import os
import webbrowser
from datetime import datetime

import pytz
import rich_click as click
from requests import codes
from rich.console import Console
from rich.markdown import Markdown

from oxpecker import API_ENDPOINTS, API_URL, LANGUAGES, session
from oxpecker.utils import print_resp, retry_if_network_error


@click.command(hidden=True)
@click.option(
    "-l",
    "--language",
    type=click.Choice(LANGUAGES, case_sensitive=False),
    required=True,
    help="""The identifier for the language to create a task for.""",
)
@click.option(
    "-s", "--source-code", required=True, help="SHA256 checksum of the source code."
)
@click.option(
    "-c", "--codeql-db", required=True, help="SHA256 checksum of the CodeQL database."
)
@click.option(
    "-t",
    "--build-target",
    required=True,
    help="SHA256 checksum of the build target file.",
)
@click.option("--include-package", multiple=True, help="For pathfinder.")
@click.option("--sandbox-url", required=True, help="See `scan` help.")
@click.option("--sandbox-headers", help="See `scan` help.")
@click.option(
    "--poc-start-index",
    type=click.INT,
    default=0,
    help="See `scan` help.",
)
@click.option(
    "--poc-max-count",
    type=click.INT,
    default=1,
    help="See `scan` help.",
)
@click.option(
    "--poc-use-local-python",
    type=click.BOOL,
    default=False,
    help="Use local Python to generate POC.",
)
@click.option("--include-rules", help="See `scan` help.")
@click.option("--exclude-rules", help="See `scan` help.")
@click.option(
    "--use-openai-model-as-primary",
    is_flag=True,
    default=False,
    help="See `scan` help.",
)
@click.pass_context
@retry_if_network_error()
def create(
    ctx,
    language,
    source_code,
    codeql_db,
    build_target,
    include_package,
    sandbox_url,
    sandbox_headers,
    poc_start_index,
    poc_max_count,
    poc_use_local_python,
    include_rules,
    exclude_rules,
    use_openai_model_as_primary,
):  # pylint: disable=too-many-arguments
    """Create a new task."""
    if ctx.find_root().params["debug"]:
        click.echo(language)
        click.echo(source_code)
        click.echo(codeql_db)
        click.echo(build_target)
        click.echo(include_package)
    r = session.post(
        f"{API_URL}{API_ENDPOINTS['task_create']}",
        json={
            "lang": language,
            "params": {
                "pf": {
                    "buildTargetFile": build_target,
                    "includePackages": include_package,
                },
                "poc": {
                    "sandboxUrl": sandbox_url,
                    "sandboxAuthHeaders": sandbox_headers,
                    "startIndex": poc_start_index,
                    "maxCount": poc_max_count,
                    "includeRules": include_rules.split(",") if include_rules else [],
                    "excludeRules": exclude_rules.split(",") if exclude_rules else [],
                    "useLocalPython": poc_use_local_python,
                    "testModeOnly": False if use_openai_model_as_primary else True,
                },
            } | ({"sast": {"codeqldb": codeql_db}} if codeql_db else {}),
        } | ({"sourceCode": source_code} if source_code else {}),
        verify=not ctx.find_root().params["insecure_skip_tls_verify"],
    )
    print_resp(ctx, r)
    # pylint: disable=no-member
    return r.json()["taskId"] if r.status_code == codes.ok else None


@click.command(name="list", hidden=True)
@click.pass_context
@retry_if_network_error()
def list_command(ctx):
    """List tasks."""
    r = session.post(
        f"{API_URL}{API_ENDPOINTS['task_list']}",
        json={},
        verify=not ctx.find_root().params["insecure_skip_tls_verify"],
    )
    print_resp(ctx, r)


@click.command(hidden=True)
@click.argument("task_id")
@click.pass_context
@retry_if_network_error()
def inspect(ctx, task_id):
    """Return detailed information of a task."""
    r = session.get(
        f"{API_URL}{API_ENDPOINTS['task_inspect']}/{task_id}",
        verify=not ctx.find_root().params["insecure_skip_tls_verify"],
    )
    ctx.ensure_object(dict)
    ctx.obj["response"] = r
    print_resp(ctx, r)


@click.command(hidden=True)
def cancel():
    """Cancel a task."""
    raise NotImplementedError


@click.command(hidden=True)
@click.argument("task_id")
@click.option(
    "--render/--no-render",
    help="Render markdown report in terminal.",
    is_flag=True,
    default=True,
)
@click.option(
    "--format",
    "format_",
    type=click.Choice(["markdown", "pdf", "html"], case_sensitive=False),
    default="markdown",
    help="Format of report.",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    help="Output file path.",
)
@click.option(
    "--web",
    is_flag=True,
    help="Open HTML report in web browser.",
)
@click.pass_context
@retry_if_network_error()
# pylint: disable=too-many-arguments
def report(ctx, format_, render, task_id, output, web):
    """Get vulnerability report about a task."""
    url = f"{API_URL}{API_ENDPOINTS['task_inspect']}/{task_id}/result"
    if format_ == "pdf":
        url += "?type=pdf"
    r = session.get(
        url,
        verify=not ctx.find_root().params["insecure_skip_tls_verify"],
    )
    if r.status_code == codes.ok:  # pylint: disable=no-member
        if format_ == "pdf":
            if output is None:
                output = os.path.join(os.getcwd(), f"Oxpecker_report_{task_id}.pdf")
            with open(output, "wb") as f:
                f.write(r.content)
            click.secho(f"📙 PDF report saved to {output}")
        elif format_ == "html":
            url1 = f"{API_URL}{API_ENDPOINTS['task_inspect']}/{task_id}/create-report-share-link"
            r1 = session.get(
                url1,
                verify=not ctx.find_root().params["insecure_skip_tls_verify"],
            )
            if r1.status_code == codes.ok:  # pylint: disable=no-member
                share_link = r1.json()["shareLink"]
                expired_at = r1.json()["expiredAt"]
                # Parse the datetime string and convert it to local time
                dt = datetime.strptime(expired_at, "%Y-%m-%d %H:%M:%S")
                dt = dt.replace(tzinfo=pytz.utc).astimezone(tz=None)
                expired_at = dt.strftime("%Y-%m-%d %H:%M:%S")
                if web:
                    if not webbrowser.open(share_link):
                        click.secho("⚠️ No browser available.")
                        click.secho(f"🌍 HTML report link: {share_link}")
                        click.secho(f"The link expires at {expired_at}.")
                else:
                    click.secho(f"🌍 HTML report link: {share_link}")
                    click.secho(f"The link expires at {expired_at}.")
            else:
                click.secho(
                    f"{r1.status_code}: {r1.request.method} {r1.url}",
                    fg="red",
                    bold=True,
                )
                ctx.abort()
        elif render:
            console = Console()
            md = Markdown(r.text)
            console.print(md)
        else:
            print(r.text)
    else:
        click.secho(f"{r.status_code}: {r.request.method} {r.url}", fg="red", bold=True)
        ctx.abort()
