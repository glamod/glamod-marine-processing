.. Marine observations suite documentation master file, created by
   sphinx-quickstart on Thu Jul 23 07:39:51 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Initializing a new data release
===============================

Configuration repository
------------------------

The glamod-marine-config repository
(https://github.com/glamod/glamod-marine-processing) serves as container for the
configuration used to create the different data releases for C3S. The
Observations Suite configuration files are stored in
obs-suite/*release*-*update*/*dataset* directories within this repository.

Currently, the following configuration sets are available:

.. list-table:: Title
   :widths: 20 30 10
   :header-rows: 1

   * - Data release
     - Path in repo/obs-suite
     - Marine code version
   * - r092019
     - r092019-000000/ICOADS_R3.0.0T
     - v1.0
   * - release_2.0
     - release_2.0-000000/ICOADS_R3.0.0T
     - v1.1
   * - Demo release
     - release_demo-000000/ICOADS_R3.0.0T
     - v1.1
   * - Previous release
     - release_7.0/000000/ICOADS_R3.0.2T
     - v7.0.1
   * - Stable release
     - release_8.0/000000/ICOADS_R3.0.0T
     - v8.0.0
   * -
     - release_8.0/000000/ICOADS_R3.0.2T
     - v8.0.0
   * -
     - release_8.0/000000/C-RAID_1.2
     - v8.0.0



Up until v1.1 (release_2.0), the configuration files were not maintained in
the configuration repository, but in the code repository. They have been now
included in the configuration repository for traceability. It is also worth
noting, that some changes have been made to the configuration files after v1.1:
the format in the Demo release files must be applied when running the observations
suite.

Create the configuration files for the release and dataset
----------------------------------------------------------

Every data release is identified in the file system with the following tags:

* release: release name (eg. release_7.0)
* update: update tag (eg. 000000)
* dataset: dataset name (eg. ICOADS_R3.0.2T)

Create a new directory *release*-*update*/*dataset*/ in the obs-suite
configuration directory (*config_directory*) of the configuration repository
(note the hyphen as field separator between *release* and *update*). We will now
refer to this directory as *release_config_dir*.

The files described in the following sections need to be created, with the
:ref:`release_periods_file` and the :ref:`process_list_file` required from the
setup of the new data release. The rest of the files can be generated as the
processing gets to the corresponding level.

The sample files in the following sections can be found in the release_demo
directory of the configuration repository.

.. _release_periods_file:

Release periods file
^^^^^^^^^^^^^^^^^^^^

Create file *release_config_dir*/source_deck_periods.json

This file is a json file with each of the source-deck partitions to be included
in the release, and the associated periods (year resolution) to process.

The figure below shows a sample of this file:

.. literalinclude:: config_files/source_deck_periods.json

.. _process_list_file:

Process list file
^^^^^^^^^^^^^^^^^

Create file *release_config_dir*/source_deck_list.txt

This is a simple ascii file with the list of source-deck partitions to process.
Create the master list with the keys of file source_deck_periods.json. This file
can later be subsetted if a given process is to be run in batches.

The figure below shows a sample of this file:

.. literalinclude:: config_files/source_deck_list.txt

Post process list
^^^^^^^^^^^^^^^^^

Create file *release-config_dir*/source_deck_list_post.json

This is a simple ascii file with a single source-deck partition to process.
Both *source_deck_list* and *source_deck_list_pots* are used in **merge_suite**
or **split_suite** to merge multiple source-deck partitions into a single
source-deck partition or to split a single source-deck partition into multiple
source-deck partitions.

.. literalinclude:: config_files/source_deck_list_post.txt

.. _level1a_config_file:

Level 1a configuration file
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create file *release_config_dir*/level1a.json.

This file includes information on the initial dataset files data model(s),
filters used to select reports and mapping to apply convert the data to the CDM.

The figure below shows a sample of this file:

.. literalinclude:: config_files/level1a.json


This file has its default configuration parameters in the outer keys.
Source-deck specific configuration can be applied by specifying a configuration
parameter under a *sid-dck* key. In the sample given, all the
source and decks will be processed with the default configuration, but using their
source-deck partition specific *data_model* for mapping. Optionally, some specific
reports or observations can be set on a blacklist or on a list of generic IDs.
This is important for quality control in *level1e*.

Configuration parameters job* are only used by the slurm launchers, while the
rest by the corresponding level1a.py script.

.. _level1b_config_file:

Level 1b configuration file
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create file *release_config_dir*/level1b.json.

This file contains information on the *NOC corrections* version to be used
and the correspondences between the CDM tables fields on which the corrections
are applied and the subdirectories where these corrections can be found.
The CDM history stamp for every correction is also configured in this file.
Alternatively, you can use the duplicate checker from the cdm_reader_mapper module.

The figure below shows a sample of this file:

.. literalinclude:: config_files/level1b.json

This file has its default configuration parameters in the outer keys.
Source-deck specific configuration can be applied by specifying a configuration
parameter under a *sid-dck* key. In the sample above, only the default
configuration is applied.

Configuration parameters job* are only used by the slurm launchers, while the
rest by the corresponding level1b.py script.


.. _level1c_config_file:

Level 1c configuration file
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create file *release_config_dir*/level1c.json.

This file contains information on the *NOC corrections* version to be used.

The figure below shows a sample of this file:

.. literalinclude:: config_files/level1c.json

This file has its default configuration parameters in the outer keys.
Source-deck specific configuration can be applied by specifying a configuration
parameter under a *sid-dck* key. In the sample above, only the default
configuration is applied.


.. _level1d_config_file:

Level 1d configuration file
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create file *release_config_dir*/level1d.json.

This file contains information on the metadata sources that are merged into the level1c data.
Currently the only MD source is the *Pub47 files* and the full process is basically tailored
to Pub47 as pre-processed in NOC.

This file contains information of the subdirectory in the release data directory
where the metadata can be found ("md_subdir") and the name of the mapping within the
Common Data Model mapper module used to map Pub47 to the CDM ("md_model").

The level1d process will fail if it doesn't find a metadata file for a month
partition. To account for periods where metadata are not available, the
following optional keys can be used:

* "md_not_avail": true indicates the process that for the full release period,
  there is not metadata available. Defaults to false.
* "md_first_yr_avail": indicates the first year for which metadata files should
  be available in the release period. Defaults to first year in the release
  period.
* "md_last_yr_avail": indicates the last year for which metadata files should be
  available in the release period. Defaults to last year in the release
  period.

By using the above keys, the process is indicated to securely progress data files
to the next processing level without merging any metadata when it is not available.

The figure below shows a sample of this file:

.. literalinclude:: config_files/level1d.json

This file has its default configuration parameters in the outer keys.
Source-deck specific configuration can be applied by specifying a configuration
parameter under a *sid-dck* key. In the sample above, only the default
configuration is applied.

.. _level1e_config_file:

Level 1e configuration file
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create file *release_config_dir*/level1e.json.

The level1e specific quality control parameters included in this file are:

* "history_explain" : text added to the header file history field when flags are
  merged.
* "qc_settings": Settings used by marine_qc.

  * "copies": Skip quality control of the key observations, instead use quality flags
    of the value observation.
  * "individual_reports": Settings applied on individual reports

      * "preprocessing": Define external climtology files and read them as background climatologies
      * "header": QC functions applied on header files
      * "observations": QC functions applied on observations files
      * "combined": Combined QC functions applied on two observation files

  * "sequential_reports": Settings applied on tracks of *primary_station_ids*.

      * "header": QC functions applied on header files
      * "observations": QC functions applied on observations files
      * "combined": Combined QC functions applied on two observation files

  * "grouped_reports": Settings applied on grouped observations.

      * "preprocessing": Define external climtology files and read them as background climatologies
      * "observations": QC functions applied on observations files


The figure below shows a sample of this file:

.. literalinclude:: config_files/level1e.json

This file has its default configuration parameters in the outer keys.
Source-deck specific configuration can be applied by specifying a configuration
parameter under a *sid-dck* key. In the sample above, only the default
configuration is applied.
