"""
=============================================
Quality control Command Line Interface module
=============================================
"""

from __future__ import annotations

import datetime
import os

import click

from .cli import CONTEXT_SETTINGS, add_options
from .utilities import add_to_config, get_base_path, get_configuration, mkdir, save_json


@click.command(context_settings=CONTEXT_SETTINGS)
@add_options()
def QcCli(
    machine,
    release,
    update,
    dataset,
    corrections_version,
    submit_jobs,
):
    """Enry point for theqcmetadata_suite command line interface."""
    release_update = f"{release}-{update}"
    config = get_configuration(machine)

    home_directory = get_base_path()
    data_directory = config["paths"]["data_directory"]
    code_directory = os.path.join(home_directory, "qc_suite")
    config_directory = os.path.join(code_directory, "config")
    obs_code_directory = os.path.join(home_directory, "obs_suite")
    obs_config_directory = os.path.join(
        obs_code_directory, "configuration_files", release_update, dataset
    )
    scripts_directory = os.path.join(code_directory, "scripts")
    lotus_scripts_directory = os.path.join(code_directory, "lotus_scripts")
    work_directory = os.path.abspath(config["paths"]["glamod"])
    scratch_directory = os.path.join(work_directory, os.getlogin())
    release_directory = os.path.join(scratch_directory, "qc_suite")
    qc_log_directory = os.path.join(release_directory, "logs_qc")
    qc_hr_log_directory = os.path.join(release_directory, "logs_qc_hr")

    metoffice_qc_directory = os.path.join(data_directory, release, "metoffice_qc")
    out_dir = os.path.join(metoffice_qc_directory, "base")
    icoads_dir = os.path.join(metoffice_qc_directory, "corrected")
    ids_to_exclude = os.path.join(
        config_directory, "list_of_ids_that_are_not_ships.txt"
    )
    parameter_file = os.path.join(config_directory, "ParametersCCI.json")
    icoads_version = "3.0.2"
    external_files = os.path.join(data_directory, "external_files")
    sst_files = os.path.join(external_files, "SST")
    sst_stdev_climatology = os.path.join(sst_files, "OSTIA_pentad_stdev_climatology.nc")
    old_sst_stdev_climatology = os.path.join(
        sst_files, "HadSST2_pentad_stdev_climatology.nc"
    )
    sst_buddy_one_box_to_buddy_avg = os.path.join(
        sst_files, "OSTIA_compare_1x1x5box_to_buddy_average.nc"
    )
    sst_buddy_one_ob_to_box_avg = os.path.join(
        sst_files, "OSTIA_compare_one_ob_to_1x1x5box.nc"
    )
    sst_buddy_avg_sampling = os.path.join(
        sst_files, "OSTIA_buddy_range_sampling_error.nc"
    )
    ostia_background = os.path.join(external_files, "OSTIA_background")
    djf_ostia_background = os.path.join(ostia_background, "DJF_bckerr_smooth.nc")
    jja_ostia_background = os.path.join(ostia_background, "JJA_bckerr_smooth.nc")
    son_ostia_background = os.path.join(ostia_background, "SON_bckerr_smooth.nc")
    mam_ostia_background = os.path.join(ostia_background, "MAM_bckerr_smooth.nc")
    test_files = os.path.join(external_files, "TestFiles")
    sst_climatology_file = os.path.join(test_files, "HadSST2_pentad_climatology.nc")
    mat_climatology_file = os.path.join(test_files, "HadNMAT2_pentad_climatology.nc")
    stdev_climatology_file = os.path.join(
        test_files, "HadSST2_pentad_stdev_climatology.nc"
    )
    sst_daily_file = os.path.join(test_files, "HadSST2_daily_1x1_climatology.nc")
    ostia_test_file = os.path.join(
        test_files, "20090101-UKMO-L4HRfnd-GLOB-v01-fv02-OSTIA.nc"
    )

    config = add_to_config(
        config,
        home_directory=home_directory,
        code_directory=code_directory,
        config_directory=config_directory,
        scripts_directory=scripts_directory,
        lotus_scripts_directory=lotus_scripts_directory,
        scratch_directory=scratch_directory,
        release_directory=release_directory,
        qc_log_directory=qc_log_directory,
        qc_hr_log_directory=qc_hr_log_directory,
        key="paths",
    )

    config = add_to_config(
        config,
        out_dir=out_dir,
        ICOADS_dir=icoads_dir,
        track_out_dir=out_dir,
        key="Directories",
    )

    config = add_to_config(
        config,
        icoads_version=icoads_version,
        key="Icoads",
    )

    config = add_to_config(
        config,
        parameter_file=parameter_file,
        IDs_to_exclude=ids_to_exclude,
        key="Files",
    )

    config = add_to_config(
        config,
        SST_stdev_climatology=sst_stdev_climatology,
        Old_SST_stdev_climatology=old_sst_stdev_climatology,
        SST_buddy_one_box_to_buddy_avg=sst_buddy_one_box_to_buddy_avg,
        SST_buddy_one_ob_to_box_avg=sst_buddy_one_ob_to_box_avg,
        SST_buddy_avg_sampling=sst_buddy_avg_sampling,
        DJF_ostia_background=djf_ostia_background,
        JJA_ostia_background=jja_ostia_background,
        SON_ostia_background=son_ostia_background,
        MAM_ostia_background=mam_ostia_background,
        key="Climatologies",
    )

    config = add_to_config(
        config,
        sst_climatology_file=sst_climatology_file,
        mat_climatology_file=mat_climatology_file,
        stdev_climatology_file=stdev_climatology_file,
        sst_daily_file=sst_daily_file,
        ostia_test_file=ostia_test_file,
        key="TestFiles",
    )

    config["machine"] = machine
    config["submit_jobs"] = submit_jobs

    current_time = datetime.datetime.now()
    current_time = current_time.strftime("%Y%m%dT%H%M%S")

    qc_config = f"qc_config_{current_time}.json"
    qc_config = os.path.join(release_directory, qc_config)
    save_json(config, qc_config)

    mkdir(qc_log_directory)
    mkdir(qc_hr_log_directory)

    qc_source = os.path.join(data_directory, release, dataset, "level1d")
    dck_list = os.path.join(obs_config_directory, "source_deck_list.txt")
    dck_period = os.path.join(obs_config_directory, "source_deck_periods.json")
    corrections = os.path.join(
        data_directory, release, "NOC_corrections", corrections_version
    )
    qc_destination = os.path.join(data_directory, release, "metoffice_qc", "corrected")

    slurm_script = "preprocess.py"
    slurm_script = os.path.join(scripts_directory, slurm_script)

    os.system(
        "python {} -source={} -dck_list={} -dck_period={} -corrections={} -destination={} -release={} -update={}".format(
            slurm_script,
            qc_source,
            dck_list,
            dck_period,
            corrections,
            qc_destination,
            release,
            update,
        )
    )

    slurm_script = "qc_slurm.py"
    slurm_script = os.path.join(lotus_scripts_directory, slurm_script)
    os.system(f"python {slurm_script} {qc_config}")

    slurm_script = os.path.join(lotus_scripts_directory, slurm_script)
    os.system(f"python {slurm_script} {qc_config} --hr")
