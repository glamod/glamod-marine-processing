.. Marine observations suite documentation master file, created by
   sphinx-quickstart on Thu Jul 23 07:39:51 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Split a single source-deck partiton
===================================

Optionally, you can split a singel source-deck partition into multiple new source-deck_partitions. See:

.. code-block:: bash

  split_suite

Optionally, if date information is given in the file names, please run the command with option --date_avail.

Old deck list:

.. literalinclude:: config_files/source_deck_list.txt

New deck list:

.. literalinclude:: config_files/source_deck_list_post.txt

For more details run:

.. code-block:: bash

  split_suite -h
