
=========
Changelog
=========

v7.0.1 (unpublished)
--------------------
Contributors to this version: Ludwig Lierhammer (:user:`ludwiglierhammer`)

New features and enhancements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* add quality checks for both Wind speed and wind direction in level1e script (:issue:`20`, :pull:`22`)

Breaking changes
^^^^^^^^^^^^^^^^
* delete metadata suite, config suite and not-used scripts/modules (:issue:`14`, :pull:`16`)
* adjust ``obs_suite`` to ``cdm_reader_mapper`` version ``v0.4.0`` (yet unpublished) (:pull:`21`)

Bug fixes
^^^^^^^^^
* fixing observation suite level1e tests (:pull:`17`)
* level1e: change QC mapping from ``v7.0.0`` is now running by setting values of ``location_quality`` and ``report_time_quality`` to ``str`` (:pull:`18`)

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
* delete emtpy and not used files, functions and folders (:pull:`3`)
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
