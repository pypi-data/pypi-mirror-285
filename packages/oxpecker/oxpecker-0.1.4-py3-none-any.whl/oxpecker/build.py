"""Module for building the project using a specified command."""

import shlex

import click

from oxpecker.utils import run_command


@click.command(hidden=True)
@click.option(
    "-s",
    "--source-root",
    default=".",
    show_default=True,
    type=click.Path(),
    help="""
        The root source code directory.
        """,
)
@click.option(
    "-b", "--build-command", required=True, help="Command to compile the project."
)
@click.pass_context
def build(ctx, source_root, build_command):
    """Builds the project using the specified command."""
    click.echo(
        f"Executing build command {build_command} in source root {source_root}..."
    )
    popen_args = shlex.split(build_command)
    try:
        run_command(popen_args, cwd=source_root)
    except click.Abort:
        ctx.abort()
