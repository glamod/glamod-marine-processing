.. Marine observations suite documentation master file, created by
   sphinx-quickstart on Thu Jul 23 07:39:51 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Level 1e
========

The level1e does quality control and adds quality control flags to the level1d data.
For quality control, the MetOffice QC (https://github.com/glamod/marine_qc)
is used.

For more information to the quality control package see: https://marine-qc.readthedocs.io/en/latest/

This script executes an array of monthly subjobs per source and deck included in
the process_list. The configuration for the process is directly accessed from
the release configuration directory: the data period processed is as configured
per source and deck in the release periods file ( :ref:`release_periods_file`)
and the level1e configuration is retrieved from :ref:`level1e_config_file`.

For more details run:

.. code-block:: bash

  obs_suite -h

This script logs to *data_dir*/release/dataset/level1e/log/sid-dck/. Log files
are yyyy-mm-<release>-<update>.ext with ext either ok or failed depending on the
subjob termination status.

List  \*.failed in the sid-dck level1e log directories to find if any went wrong.
