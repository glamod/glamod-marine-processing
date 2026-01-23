"""
========================================
Marine processing Command Line Interface
========================================
"""

from __future__ import annotations

import os

import click

from .utilities import (
    add_to_config,
    get_abs_path,
    get_base_path,
    get_configuration,
    load_json,
    make_release_source_tree,
    mkdir,
)

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"], show_default=True)


def add_options():
    """Add decorator click options."""

    def _get_parameters(func):
        argcount = func.__code__.co_argcount
        return func.__code__.co_varnames[:argcount]

    def _add_options(func):
        options = _get_parameters(func)
        for option in reversed(options):
            if not hasattr(Options, option):
                continue
            option = getattr(Options, option)
            func = option(func)
        return func

    return _add_options


class Cli:
    """Skeleton command line interface class."""

    def __init__(
        self,
        machine="",
        level="",
        level_source="",
        level_destination="",
        release="",
        release_source="",
        release_destination="",
        update="",
        dataset="",
        dataset_source="",
        dataset_destination="",
        cdm_tables=None,
        data_directory=None,
        work_directory=None,
        config_file=None,
        suite="",
        deck_list=None,
        overwrite=False,
    ):
        if not release_source:
            release_source = release
        if not release_destination:
            release_destination = release
        if not level_destination:
            level_destination = level
        if not dataset_source:
            dataset_source = dataset
        if not dataset_destination:
            dataset_destination = dataset
        self.machine = machine.lower()
        self.level = level
        self.level_source = level_source
        self.level_destination = level_destination
        self.release = release
        self.release_source = release_source
        self.release_destination = release_destination
        self.update = update
        self.dataset = dataset
        self.dataset_source = dataset_source
        self.dataset_destination = dataset_destination
        self.cdm_tables = cdm_tables
        self.data_directory = data_directory
        self.work_directory = work_directory
        self.config_file = config_file
        self.suite = suite
        self.release_update = f"{release}-{update}"
        self.release_update_source = f"{release_source}-{update}"
        self.release_update_destination = f"{release_destination}-{update}"
        self.deck_list = deck_list
        self.overwrite = overwrite

    def initialize(self):
        """Initialize command line interface settings."""
        if not self.config_file:
            config = self.build_configuration()
        elif not os.path.isfile(self.config_file):
            raise FileNotFoundError(config)
        else:
            config = load_json(self.config_file)

        make_release_source_tree(
            data_path=config["paths"]["data_directory"],
            config_path=config["paths"]["config_directory"],
            release_source=self.release,
            release_destination=self.release_destination,
            update=self.update,
            dataset_source=self.dataset,
            dataset_destination=self.dataset_destination,
            level=self.level,
            level_destination=self.level_destination,
            deck_list=self.deck_list,
        )
        mkdir(config["paths"]["release_directory"])
        return config

    def build_configuration(self):
        """Build configuration."""
        config = get_configuration(self.machine)
        config["machine"] = self.machine
        config["overwrite"] = self.overwrite
        config["abbreviations"] = {
            "release": self.release,
            "update": self.update,
            "dataset": self.dataset,
            "release_tag": self.release_update,
        }
        config["abbreviations_source"] = {
            "release": self.release_source,
            "update": self.update,
            "dataset": self.dataset_source,
            "release_tag": self.release_update_source,
        }
        config["abbreviations_destination"] = {
            "release": self.release_destination,
            "update": self.update,
            "dataset": self.dataset_destination,
            "release_tag": self.release_update_destination,
        }
        config["level_source"] = self.level_source
        config["level_destination"] = self.level_destination
        config["release_source"] = self.release_source
        config["release_destination"] = self.release_destination
        config["dataset_source"] = self.dataset_source
        config["dataset_destination"] = self.dataset_destination
        config["cdm_tables"] = self.cdm_tables

        if self.data_directory is not None:
            config["paths"]["data_directory"] = self.data_directory
        if self.work_directory is not None:
            config["paths"]["glamod"] = self.work_directory

        try:
            user = os.getlogin()
        except OSError:
            user = "testuser"

        config["paths"]["data_directory"] = get_abs_path(
            config["paths"]["data_directory"]
        )
        config["paths"]["glamod"] = get_abs_path(config["paths"]["glamod"])

        home_directory = get_base_path()
        code_directory = os.path.join(home_directory, self.suite)
        config_directory = os.path.join(code_directory, "configuration_files")
        config_files_path = os.path.join(
            config_directory, self.release, self.update, self.dataset
        )
        scripts_directory = os.path.join(code_directory, "scripts")
        lotus_scripts_directory = os.path.join(code_directory, "lotus_scripts")
        work_directory = os.path.abspath(config["paths"]["glamod"])
        scratch_directory = os.path.join(work_directory, user)
        release_directory = os.path.join(
            scratch_directory, self.release, self.dataset, self.level
        )

        config = add_to_config(
            config,
            home_directory=home_directory,
            code_directory=code_directory,
            config_directory=config_directory,
            config_files_path=config_files_path,
            scripts_directory=scripts_directory,
            lotus_scripts_directory=lotus_scripts_directory,
            scratch_directory=scratch_directory,
            release_directory=release_directory,
            key="paths",
        )
        return config


class Options:
    """Class for click options."""

    def __init__(self):
        self.machine = click.option(
            "-m",
            "--machine",
            default="BASTION",
            help="""HPC cluster where to create and run the scripts, \n
            * KAY: kay.ichec.ie \n
            * MELUXINA: login.lxp.lu \n
            * BASTION: bastion01.core.ichec.ie
            """,
        )
        self.submit_jobs = click.option(
            "-submit", "--submit_jobs", is_flag=True, help="Submit job scripts."
        )
        self.run_jobs = click.option(
            "-run", "--run_jobs", is_flag=True, help="Run job scripts interactively."
        )
        self.parallel_jobs = click.option(
            "-parallel",
            "--parallel_jobs",
            is_flag=True,
            help="Run job scripts interactively in parallel. This is mainly for BASTION machine.",
        )
        self.parallel_tasks = click.option(
            "-parallel_task",
            "--parallel_tasks",
            is_flag=True,
            help="Run tasks per job script interactively in parallel. This is mainly for BASTION machine.",
        )
        self.n_max_jobs = click.option(
            "-n_max",
            "--n_max_jobs",
            default="12",
            help="Maximum number of jobs running in parallel. Use only with parallel_jobs.",
        )
        self.nohup = click.option(
            "-nohup",
            "--nohup",
            is_flag=True,
            help="Use nohup to run job scripts in the background",
        )
        self.level = click.option(
            "-l",
            "--level",
            required=True,
            help="""Step of observation suite process:

            * level1a: Mapping dataset to CDM. \n
            * level1b: Improve data with corrections and/or additional information. \n
            * level1c: Perform data validation and apply data with metadata.\n
            * level1d: Enrich data with external metadata. \n
            * level1e: Add quality control flags to data. \n
            * level2: Make data ready to ingest in the database.
            """,
        )
        self.level_source = click.option(
            "-ls",
            "--level_source",
            help="Name of the source data level.",
        )
        self.level_destination = click.option(
            "-ld",
            "--level_destination",
            help="Name of the destination data level.",
        )
        self.release = click.option(
            "-r", "--release", default="release_8.0", help="Name of the data release."
        )
        self.release_source = click.option(
            "-rs",
            "--release_source",
            help="Name of the source data release",
        )
        self.release_destination = click.option(
            "-rd",
            "--release_destination",
            help="Name of the destination data release.",
        )
        self.update = click.option(
            "-u", "--update", default="000000", help="Name of the data release update."
        )
        self.dataset = click.option(
            "-d",
            "--dataset",
            default="ICOADS_R3.0.2T",
            help="Name of the data release dataset.",
        )
        self.dataset_source = click.option(
            "-ds", "--dataset_source", help="Name of the source data release dataset"
        )
        self.dataset_destination = click.option(
            "-dd",
            "--dataset_destination",
            help="Name of the destination data release dataset",
        )
        self.data_directory = click.option(
            "-data_dir",
            "--data_directory",
            help="Directory path of the input and output datasets. By default, take directory path from machine-depending configuration file.",
        )
        self.work_directory = click.option(
            "-work_dir",
            "--work_directory",
            help="Directory path of the log and template files. By default, take directory path from machine-depending configuration file.",
        )
        self.cdm_tables = click.option(
            "-tables",
            "--cdm_tables",
            multiple=True,
            help="CDM tables to process (obs_suite).",
        )
        self.noc_version = click.option(
            "-noc_v",
            "--noc_version",
            help="Name of the NOC corrections version (obs_suite: level1b).",
        )
        self.noc_path = click.option(
            "-noc_p",
            "--noc_path",
            help="Path to the NOC correction files (obs_suite: level1b).",
        )
        self.pub47_path = click.option(
            "-pub47_p",
            "--pub47_path",
            help="Path to the Pub47 files (obs_suite: level1d).",
        )
        self.config_file = click.option(
            "-cfg",
            "--config_file",
            default=False,
            help="Use already existing configuration file.",
        )
        self.available_date_information = click.option(
            "-date_avail",
            "--available_date_information",
            is_flag=True,
            help="Set if date information is available in input file names (post_proc).",
        )
        self.additional_directories = click.option(
            "-add_dirs",
            "--additional_directories",
            multiple=True,
            default=["excluded", "invalid"],
            help="Merge data in additional directories too (post_proc).",
        )
        self.overwrite = click.option(
            "-o",
            "--overwrite",
            is_flag=True,
            help="Overwrite already existing data.",
        )
        self.source_pattern = click.option(
            "-sp",
            "--source_pattern",
            help="User-defined input source pattern (obs_suite).",
        )
        self.prev_file_id = click.option(
            "-p_id",
            "--prev_file_id",
            help="fileID of input file names. Default <YYYY><MM><RELEASE>",
        )
        self.process_list = click.option(
            "-p_list",
            "--process_list",
            multiple=True,
            help="List of decks to process. Take default from level configuration file (obs_suite).",
        )
        self.year_init = click.option(
            "-year_i", "--year_init", help="Initial release period year (obs_suite)."
        )
        self.year_end = click.option(
            "-year_e", "--year_end", help="End release period year (obs_suite)."
        )


Options = Options()
