.. Marine observations suite documentation master file, created by
   sphinx-quickstart on Thu Jul 23 07:39:51 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Level 1a
========

Level 1a contains the initial data converted from the input data sources
(*level0 data*) to files compatible with the CDM.

Every monthly file of the individual source-deck dataset partitions is
converted with the following command:

Command to create level1a observation suite scripts:

.. code-block:: bash

  obs_suite -l level1a

Command to run level1a observation suite scripts:

.. code-block:: bash

  obs_suite -l level1a -run

Command to run level1a observation suite scripts in parallel:

.. code-block:: bash

  obs_suite -l level1a -parallel

For more details run:

.. code-block:: bash

  obs_suite -h

This script executes an array of monthly subjobs per source and deck included in
the process_list. The configuration for the process is directly accessed from
the release configuration directory: the data period processed is as configured
per source and deck in the release periods file ( :ref:`release_periods_file`)
and the level1a configuration is retrieved from :ref:`level1a_config_file`.

This script logs to *data_dir*/release/dataset/level1b/log/sid-dck/. Log files
are yyyy-mm-<release>-<update>.ext with ext either ok or failed depending on the
subjob termination status.

List  \*.failed in the sid-dck level1e log directories to find if any went wrong.
