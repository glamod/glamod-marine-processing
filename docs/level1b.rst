.. Marine observations suite documentation master file, created by
   sphinx-quickstart on Thu Jul 23 07:39:51 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Level 1b
========

Level 1b integrates *NOC corrections* containing enhanced information on the
duplicate status of the observations, corrected date/time and locations, and
linked station IDs with the level1a data. As part of the integration a weather
report may move between months if an error in the date had previously been
identified and the correct data is for a different month. A description of the
processing used to generate these external files is described in the marine
duplication identification document (available upon request,
to be published shortly). It should be noted that this processing is currently
external to C3S311a_lot2 but will be integrated in a future release.
Optionally, the cdm_reader_mapper.duplicate_check can be used to detect and
flag duplicates.

For more details run:

.. code-block:: bash

  obs_suite -h

This script executes an array of monthly subjobs per source and deck included in
the process_list. The configuration for the process is directly accessed from
the release configuration directory: the data period processed is as configured
per source and deck in the release periods file ( :ref:`release_periods_file`)
and the level1b configuration is retrieved from :ref:`level1b_config_file`.

This script logs to *data_dir*/release/dataset/level1b/log/sid-dck/. Log files
are yyyy-mm-<release>-<update>.ext with ext either ok or failed depending on the
subjob termination status.

List  \*.failed in the sid-dck level1e log directories to find if any went wrong.
