"""Module about CodeQL databases."""

import os
import subprocess
from pathlib import Path

import rich_click as click

from oxpecker import CODEQL_EXE, LANGUAGES
from oxpecker.utils import run_command


@click.command(
    help="Create a CodeQL database for a source tree that can be analyzed using one of the CodeQL "
    "products.",
    hidden=True,
)
@click.option(
    "--source-root",
    default=".",
    type=click.Path(),
    help="""See `scan` help.""",
)
@click.option(
    "--database",
    required=True,
    type=click.Path(),
    help="""
        Path to the CodeQL database to create.
        This directory will be created, and must not
        already exist (but its parent must).

        If the --db-cluster option is given, this will not
        be a database itself, but a directory that will
        contain databases for several languages built
        from the same source root.

        It is important that this directory is not in a
        location that the build process will interfere
        with. For instance, the target directory of a
        Maven project would not be a suitable choice.
        """,
)
@click.option(
    "--db-cluster/--no-db-cluster",
    help="""
        Instead of creating a single database, create a
        "cluster" of databases for different languages,
        each of which is a subdirectory of the directory
        given on the command line.""",
)
@click.option(
    "--language",
    required=True,
    type=click.Choice(LANGUAGES, case_sensitive=False),
    help="""See `scan` help.""",
)
@click.option(
    "-c",
    "--command",
    help="""See `scan` help.""",
)
@click.option(
    "--overwrite/--no-overwrite",
    help="""
        If the database already exists, delete
        it and proceed with this command instead of
        failing. This option should be used with caution
        as it may recursively delete the entire database
        directory.
        """,
    default=True,
)
@click.option(
    "--codeql-options",
    multiple=True,
    help="""
    Other CodeQL options.
""",
)
@click.option(
    "--precompile-jsp/--no-precompile-jsp",
    is_flag=True,
    show_default=True,
    default=False,
    help="""See `scan` help.""",
)
@click.pass_context
def createdb(
    ctx,
    database,
    source_root,
    language,
    db_cluster,
    command,
    overwrite,
    codeql_options,
    precompile_jsp,
):  # pylint: disable=too-many-arguments
    """Create a CodeQL database for a source tree that can be analyzed using one of
    the CodeQL products.
    """
    if not CODEQL_EXE:
        ctx.fail("FATAL: Codeql executable not found!")

    if precompile_jsp:
        compiler_jar = (
            Path(__file__).parent
            / "jsp-compiler/target/jsp-compiler-0.0.1-SNAPSHOT.jar"
        )
        process = subprocess.run(
            f"java -jar {compiler_jar}",
            shell=True,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if process.returncode != 0:
            click.secho(
                f"Command {' '.join(process.args)} failed with exit code {process.returncode}.",
                fg="red",
                bold=True,
            )
            ctx.abort()

    popen_args = (
        [
            CODEQL_EXE,
            "database",
            "create",
            "--language",
            language,
            "--db-cluster" if db_cluster else "--no-db-cluster",
            "--overwrite" if overwrite else "--no-overwrite",
        ]
        + ([f"--command={command}"] if command else [])
        + ["--no-run-unnecessary-builds", "-j0"]
        + ["--source-root", source_root]
        + ([" ".join(codeql_options)] if codeql_options else [])
        + ["--", os.path.expanduser(database)]
    )
    try:
        run_command(
            popen_args, env=os.environ | {"SEMMLE_JAVA_EXTRACTOR_JVM_ARGS": "-Xmx4g"}
        )
    except click.Abort:
        ctx.abort()
