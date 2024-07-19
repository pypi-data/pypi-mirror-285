from pathlib import Path

import typer

from tdms_cli.__about__ import __version__
from tdms_cli.count_tdms_content import count_groups
from tdms_cli.extract_group_as_csv import extract_group
from tdms_cli.tdms_metadata_extraction import (
    display_groups,
    print_channel_meta,
    print_file_metadata,
    print_group_metadata,
)

app = typer.Typer()
meta_app = typer.Typer()
app.add_typer(meta_app, name="meta")


@app.command("version")
def print_version():
    """Prints version and exits"""
    print(__version__)


@app.command("extract")
def extract_group_cli(tdms_file_path: str, group_idx: int):
    """Extracts single group and saves it as CSV into CWD"""
    extract_group(Path(tdms_file_path).resolve(), group_idx)


@app.command("count")
def count_groups_cli(tdms_file_path: str):
    """Counts the number of groups and channels"""
    count_groups(tdms_file_path)


@app.command("groups")
def groups_cli(tdms_file_path: str):
    """Shows the contained groups"""
    display_groups(tdms_file_path)


@meta_app.command("file")
def file_meta_cli(tdms_file_path: str):
    """Prints the file metadata"""
    print_file_metadata(tdms_file_path)


@meta_app.command("group")
def group_meta_cli(tdms_file_path: str, idx: int = 0):
    """Prints the group metadata"""
    print_group_metadata(tdms_file_path, idx)


@meta_app.command("ch")
def channel_meta_cli(tdms_file_path: str, group_path: str = ""):
    """Prints the metadata of all channels of a group

    If the group path is not specified, it defaults to first group
    """
    print_channel_meta(tdms_file_path, group_path)


def main():
    app()


if __name__ == "__main__":
    main()
