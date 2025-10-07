
=========
Changelog
=========

v8.0.0 (unreleased)
-------------------
Contributors to this version: Ludwig Lierhammer (:user:`ludwiglierhammer`)

Announcements
^^^^^^^^^^^^^
* This release drops support for Python 3.9 and adds support for Python 3.13 (:pull:`76`).
* ``qc_suite`` is now in https://github.com/glamod/marine_qc (:pull:`117`).

New features and enhancements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* ``obs_suite``: add new level3 for extracting pressure data and merging ``header`` and ``observations-slp`` tables into one single CDM-OBS-CORE table (:pull:`75`)
* ``obs_suite``: add ICOADS_R3.0.0T configuration files for release_7.0 (:pull:`75`)
* ``obs_suite``: mark QC flags of observations as `9` if they are on a blacklistd (:pull:`137`)
* add environment.yml file (:pull:`76`)
* add dummy observation configuration files for release_8.0 (:issue:`113`, :pull:`102`)
* make this tool running with `cdm_reader_mapper` >= 2.1.0 (:issue:`113`, :pull:`102`)
* new module `split` to split decks from single deck into new multiple deck list (:pull:`140`)
* new CLI `split_suite` to split decks from single deck into new multiple deck list (:pull:`140`)
* ``obs_suite``: run jobs in parallel using nohup (:pull:`140`)
* ``merge_suite``: not only running for level1a data (:pull:`140`)
* ``obs_suite``: new release 8.0 config files for : ICOADS_R3.0.0T, ICOADS_R3.0.2T, C-RAID_1.1 and C-RAID_1.2 (:issue:`113`, :pull:`140`)
* new decorator `auto_cast` to automatically convert input data type to desired data type (:pull:`140`)
* ``obs_suite``: level1a now flags data on blacklist (6) and data with generic IDs (88) (:issue:`147`, :pull:`140`)
* ``obs_suite``: level1e now uses `marine_qc` to calculate quality control flags (:issue:`113`, :pull:`140`)

CI changes
^^^^^^^^^^
* rename GitHub workflow ``ci`` to ``testing_suite`` (:pull:`76`)
* GitHub workflow for ``testing_suite`` now uses ``uv`` for environment management, replacing ``micromamba`` (:pull:`76`)
* Update GitHub workflow for ``testing_suite`` for ``astral-sh/uv-setup`` >= ``6.0.0`` (:pull:`124`)

Internal changes
^^^^^^^^^^^^^^^^
* ``obs_suite``: update ICOADS_R3.0.0T release_4.0 time period list (:pull:`73`)
* ``obs_suite``: combine loops over decks in ``level_slurm.py`` and ``config_array.py`` to one single loop (:issue:`74`, :pull:`79`)
* ``obs_suie``: name log files according to the date of the source files instead of simply numbering them consecutively (:issue:`74`, :pull:`79`)
* ``obs_suite``: standardize level scripts (:pull:`79`)
* rename ci/requirements to CI, tidy up requirements and add dependencies to pyproject.toml file (:pull:`76`)
* ``merge_suite``: use joblib for parallelization (:pull:`140`)
* ``obs_suite``: restructure level1b, level1c, level1d and level_slurm scripts (:issue:`113`, :pull:`140`)

Breaking changes
^^^^^^^^^^^^^^^^
* ``obs_suite``: rename level3 output from <YYYY>-<MM>-<RELEASE>-<UPDATE>-pressure_data.psv to pressure-data-<YYYY>-<MM>-<RELEASE>-<UPDATE>.psv (:pull:`79`)
* command-line interface: set default release from "release_7.0" to "release_8.0" (:issue:`113`, :pull:`102`)
* extract blacklisting and some ICOADS specific functions from ``qc_suite```to ``obs_suite`` (:issue:`131`, :pull:`137`)
* refactor ``qc_suite`` and move to https://github.com/glamod/marine_qc (:issue:`108`, :pull:`117`)
* rename module ``post_processing`` to ``merge`` and CLI ``post_proc`` to ``merge_suite`` (:pull:`140`)

v7.1.0 (2024-11-25)
-------------------
Contributors to this version: Ludwig Lierhammer (:user:`ludwiglierhammer`)

Announcements
^^^^^^^^^^^^^
* make preparations for zenodo DOI assignment (:issue:`4`, :pull:`42`: pull:`54`)
* adding readthedocs documentation (:pull:`42`)
* Now under Apache v2.0 license (:pull:`42`)
* Thanks to NOC, Cookiecutter and GNU parallel (:issue:`53`, :pull:`54`)
* glamod-marine-processing has migrated its development branch name from master to main.
* final GLAMOD marine processing data release 7.0 version (:pull:`63`)

New features and enhancements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* ``obs_suite``: add quality checks for both Wind speed and wind direction in level1e script (:issue:`20`, :pull:`22`)
* ``pre_proc``: add pre-processing for ICOADS data (:pull:`24`)
* ``post_proc``: add post processing for C-RAID level1a data (:pull:`26`)
* ``obs_suite``: optionally, set list of decks to process (:pull:`25`)
* ``obs_suite``: optionally, set both release period init and end year (:pull:`25`)
* ``obs_suite``: running with C-RAID data (:pull:`25`)
* ``obs_suite``: optionally, set both source and destination level, release and dataset (:pull:`67`)
* ``obs_suite``: optionally, set both path to NOC correction data and NOC version in level1b (:pull:`67`)
* ``obs_suite``: optionally, set path to Pub47 data in level1d (:pull:`67`)
* ``obs_suite`` and ``qc_suite``: optionally, run jobs in parallel with gnu_parallel (:pull:`41`)´
* ``post_proc``: optionally, post-processing for ICOADS data (:pull:`46`)
* ``post_proc``: optionally, merge data from additional directories (invalid, excluded) to a new deck dataset (:pull:`52`)

Internal changes
^^^^^^^^^^^^^^^^
* ``obs_suite``: take data paths from already created configuration files (:pull:`67`)
* ``obs_suite``: configuration files for C-RAID (:pull:`25`)
* ``obs_suite``: adjust  to ``cdm_reader_mapper`` version ``v0.4.0`` and further versions (:pull:`21`, :pull:`28`)

Breaking changes
^^^^^^^^^^^^^^^^
* delete metadata suite, config suite and not-used scripts/modules (:issue:`14`, :pull:`16`)
* ``obs_suite``: date information is NOT mandatory in filenames anymore (:pull:`25`)
* ``obs_suite``: pass tables if no correction or quality control file are available (:pull:`25`)
* ``obs_suite``: adjust both process deck lists and processing init/end years to release7.0 requirements (:pull:`27`)
* ``obs_suite``: new ICOADS_R3.0.2T deck list after level 1a (:pull:`40`)
* ``obs_suite``: starting with year 2014 (:pull:`40`)
* set BASTION do default machine (bastion01.core.ichec.ie) (:pull:`37`)
* ``obs_suite``: use duplicate checker from ``cdm_reader_mapper`` instead of NOc correction files in level1b (:pull:`37`)
* ``obs_suite``: create only one task for level2 (:pull:`45`)
* ``obs_suite``: rename Pub47 data from {year}-{month}-01.csv to pub47-{year}-{month}.csv in level1d script (:pull:`48`)
* ``obs_suite``: set release period to 2015 to 2023 (:pull:`49`)
* ``obs_suite``: if no qc files available: set report_quality from 2 (not checked) to 0 (passed) in level1e script (:pull:`50`)
* ``obs_suite``: if report_id is not available in any observations: remove report_id from header (and vice versa) in level1e script (:pull:`50`)
* ``obs_suite``: update configuration file structure of previous GLAMOD data releases (:pull:`67`)
* ``qc_suite``: no need for NOC correction files (:pull:`39`)
* ``qc_suite``: set minimum QC end year from 2022 to 1948 (:pull:`52`)
* ``qc_suite``: update job list for release 7.0 (:pull:`52`)


Bug fixes
^^^^^^^^^
* ``obs_suite``: fixing observation suite level1e tests (:pull:`17`)
* ``obs_suite``: QC mapping from ``v7.0.0`` is now running by setting values of ``location_quality`` and ``report_time_quality`` to ``str`` (:pull:`18`)
* ``obs_suite``: use only observation reports that are also available in the header file (:pull:`44`, :pull:`45`)
* ``qc_suite``: take qc source data from level1d files instead of level1a (:pull:`47`)
* ``qc_suite``: update deck list for quality control (:pull:`47`)
* ``qc_suite``: ignore reports with invalid date time information (:pull:`52`, :pull:`58`)
* ``obs_suite``: allow mixed date time formats in level1c (:pull:`62`)

v7.0.0 (2024-06-13)
-------------------
Contributors to this version: Ludwig Lierhammer (:user:`ludwiglierhammer`)

Announcements
^^^^^^^^^^^^^^
renaming release name to vX.Y.Z

release_7.0.0 (2024-06-13)
--------------------------
Contributors to this version: Ludwig Lierhammer (:user:`ludwiglierhammer`)

Breaking changes
^^^^^^^^^^^^^^^^
* delete empty and not used files, functions and folders (:pull:`3`)
* create requirements for each suite (:pull:`3`)
* rebuild to a installable python package (:pull:`3`)
* install package and requirements via a pyproject.toml file (:pul::`3`)
* change QC mapping in obs_suite level1e (:issue:`7`, :pull:`8`):

  * if ``location_quality`` is equal ``2`` set both ``report_quality`` and ``quality_flag`` to ``1``
  * if ``report_time_quality`` is equal ``4`` or ``5`` set both ``report_quality`` and ``quality_flag`` to ``1``

New features and enhancements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* add some information files: ``AUTHORS.rst``, ``CHANGES.rst``, ``CONTRIBUTING.rst`` and ``LICENSE`` (:pull:`3`)
* make us of pre-commit (:pull:`3`)
* make use of an command-line interface to create suite PYTHON and SLURM scripts (:pull:`3`, :pull:`5`)
* add new release 7.0 configuration files (:pull:`3`)
* set some default directories and SLURM settings for both HPC systems KAY and MeluXina (:pull:`3`)

Internal changes
^^^^^^^^^^^^^^^^
* reduce complexity of some functions (:pull:`3`)
* adding observational testing suite (:issue:`5`, :pull:`5`)
* load data from ``cdm-testdata`` (:pull:`11`)
