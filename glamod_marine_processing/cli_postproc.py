"""
=============================================
Post-Processing Command Line Interface module
=============================================
"""

from __future__ import annotations

import os
from types import SimpleNamespace

import click

from .cli import CONTEXT_SETTINGS, Cli, add_options
from .post_processing import post_processing
from .utilities import load_json, mkdir, read_txt


def open_deck_list_file(config_files_path, level_config_file):
    """Open Deck list file from config file."""
    level_config_file = os.path.join(config_files_path, level_config_file)
    level_config = load_json(level_config_file)
    deck_list_file = level_config["process_list_file"]
    deck_list_file = os.path.join(config_files_path, deck_list_file)
    return read_txt(deck_list_file)


@click.command(context_settings=CONTEXT_SETTINGS)
@add_options()
def post_proc_cli(
    machine,
    release,
    update,
    dataset,
    data_directory,
    additional_directories,
    available_date_information,
    overwrite,
):
    """Entry point for the pre-processing command line interface."""
    level = "level1b"
    prev_level = "level1a"
    config = Cli(
        machine=machine,
        level=level,
        release=release,
        update=update,
        dataset=dataset,
        data_directory=data_directory,
        suite="obs_suite",
    ).initialize()
    p = SimpleNamespace(**config["paths"])

    future_deck = open_deck_list_file(p.config_files_path, f"{level}.json")
    prev_deck_list = open_deck_list_file(p.config_files_path, f"{prev_level}.json")
    input_dir = os.path.join(p.data_directory, release, dataset, "level1a")
    output_dir = os.path.join(input_dir, future_deck[0])
    mkdir(output_dir)
    post_processing(
        idir=input_dir,
        odir=output_dir,
        release=release,
        update=update,
        prev_deck_list=prev_deck_list,
        date_avail=available_date_information,
        overwrite=overwrite,
    )

    if isinstance(additional_directories, str):
        additional_directories = [additional_directories]
    for additional_directory in additional_directories:
        input_dir = os.path.join(
            p.data_directory, release, dataset, "level1a", additional_directory
        )
        output_dir = os.path.join(input_dir, future_deck[0])
        mkdir(output_dir)
        post_processing(
            idir=input_dir,
            odir=output_dir,
            release=release,
            update=update,
            prev_deck_list=prev_deck_list,
            date_avail=available_date_information,
            cdm_tables=False,
            overwrite=overwrite,
        )
