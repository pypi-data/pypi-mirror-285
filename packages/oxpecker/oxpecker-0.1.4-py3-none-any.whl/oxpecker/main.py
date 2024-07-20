"""Entrypoint for the CLI."""

import rich_click as click
import urllib3

import oxpecker.build
import oxpecker.database
import oxpecker.file
import oxpecker.login
import oxpecker.scan
import oxpecker.serve
import oxpecker.task
import oxpecker.tunnel

click.rich_click.MAX_WIDTH = 128
CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option("--debug/--no-debug", help="Debug mode.", is_flag=True, default=False)
@click.option(
    "--insecure-skip-tls-verify",
    is_flag=True,
    default=False,
    help="If true, the server's certificate will not be checked for validity. This will make your "
    "HTTPS connections insecure.",
)
def cli(debug, insecure_skip_tls_verify):  # pylint: disable=unused-argument
    """Oxpecker CLI."""
    if insecure_skip_tls_verify:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@cli.group(hidden=True)
def file():
    """Manage files."""


@cli.group(hidden=True)
def task():
    """Manage tasks."""


cli.add_command(oxpecker.build.build)
cli.add_command(oxpecker.database.createdb)
cli.add_command(oxpecker.login.login)
cli.add_command(oxpecker.scan.scan)
cli.add_command(oxpecker.serve.serve)
cli.add_command(oxpecker.tunnel.tunnel)

task.add_command(oxpecker.task.create)
task.add_command(oxpecker.task.list_command)
task.add_command(oxpecker.task.inspect)
task.add_command(oxpecker.task.cancel)
task.add_command(oxpecker.task.report)

file.add_command(oxpecker.file.upload)


def main():
    """Entrypoint script."""
    cli(auto_envvar_prefix="OXPECKER")  # pylint: disable=no-value-for-parameter


if __name__ == "__main__":
    main()
