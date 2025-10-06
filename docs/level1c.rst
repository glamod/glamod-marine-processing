.. Marine observations suite documentation master file, created by
   sphinx-quickstart on Thu Jul 23 07:39:51 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Level 1c
========

Level1c files contain reports from level1b that have been further validated
following corrections to the date/time, location and station ID using *NOC ancillaries*.
Those failing validation are rejected and archived for future analysis. Additionally,
datetime corrections applied previously in level1b, can potentially result in reports
being relocated to a different month. These reports are moved to their correct
monthly file in this level.

For more details run:

.. code-block:: bash

  obs_suite -h

This script executes an array of monthly subjobs per source and deck included in
the process_list. The configuration for the process is directly accessed from
the release configuration directory: the data period processed is as configured
per source and deck in the release periods file ( :ref:`release_periods_file`)
and the level1c configuration is retrieved from :ref:`level1c_config_file`.

This script logs to *data_dir*/release/dataset/level1c/log/sid-dck/. Log files
are yyyy-mm-<release>-<update>.ext with ext either ok or failed depending on the
subjob termination status.

List  \*.failed in the sid-dck level1e log directories to find if any went wrong.
