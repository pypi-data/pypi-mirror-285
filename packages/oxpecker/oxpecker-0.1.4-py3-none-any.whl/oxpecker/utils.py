"""Misc utilities."""

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Sequence, Union
from zipfile import ZIP_DEFLATED, ZipFile

import click
import pathspec
import rich
from click import Context
from requests import ConnectionError as ConnectionError_r
from requests import Response, codes
from tenacity import retry, stop_after_attempt
from tenacity.retry import retry_if_exception_type


def calculate_sha256(filename):
    """Calculate file sha256sum."""
    with open(filename, "rb") as f:
        bytes_ = f.read()
        readable_hash = hashlib.sha256(bytes_).hexdigest()
    return readable_hash


def print_resp(ctx: Context, r: Response) -> None:
    """Print requests response info and abort script for bad response."""
    try:
        parsed = json.loads(r.text)
    except json.JSONDecodeError:
        print(r.text)
    else:
        rich.print_json(json.dumps(parsed), indent=4)

    if r.status_code != codes.ok:  # pylint: disable=no-member
        click.secho(f"{r.status_code}: {r.request.method} {r.url}", fg="red", bold=True)
        ctx.abort()


def create_zip(
    source_root: Union[str, Path],
    output_path: Union[str, Path],
    ignore_gitignore: bool = True,
    exclude: Union[None, Sequence[str]] = None,
):
    """Create a ZIP archive from a path.
    :param source_root: file(s) or directory to create ZIP
    :param output_path: ZIP archive path
    :param ignore_gitignore: flag to ignore .gitignore patterns
    :param List of string glob patterns to exclude.
    """
    with ZipFile(output_path, "w", ZIP_DEFLATED) as zipf:
        source_root_path = Path(source_root)
        if source_root_path.is_file():
            zipf.write(source_root_path, source_root_path.name)
        elif source_root_path.is_dir():
            patterns = []
            if ignore_gitignore:
                gitignore_path = source_root_path / ".gitignore"
                if gitignore_path.exists():
                    with open(gitignore_path, "r", encoding="utf-8") as f:
                        patterns += f.readlines()
            if exclude:
                patterns += exclude
            path_spec = (
                pathspec.PathSpec.from_lines("gitwildmatch", patterns)
                if patterns
                else None
            )

            for root, dirs, files in os.walk(source_root):
                root_path = Path(root)
                if path_spec:
                    dirs[:] = [
                        d for d in dirs if not path_spec.match_file(str(root_path / d))
                    ]
                    files = [
                        f for f in files if not path_spec.match_file(str(root_path / f))
                    ]

                for file in files:
                    file_path = root_path / file
                    zipf.write(
                        str(file_path), str(file_path.relative_to(source_root_path))
                    )


def retry_if_network_error():
    """Return a decorator to retry for netwwork errors."""
    return retry(
        retry=retry_if_exception_type(ConnectionError_r),
        stop=stop_after_attempt(3),
        reraise=True,
    )


def run_command(popen_args, **kwargs):
    """Run a command with the given arguments and print its output."""
    with subprocess.Popen(
        popen_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        **kwargs,
    ) as process:
        for c in iter(
            process.stdout.readline,  # type: ignore
            b"",
        ):
            sys.stdout.write(c)
            if process.poll() is not None:
                break
        if process.returncode != 0:
            click.secho(
                f"Command {' '.join(process.args)} failed with exit code {process.returncode}.",  # type: ignore
                fg="red",
                bold=True,
            )
            raise click.Abort()
