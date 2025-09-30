.. Marine observations suite documentation master file, created by
   sphinx-quickstart on Thu Jul 23 07:39:51 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Marine file system
==================

The Observations Suite code is integrated in the file system designed for the
C3S data deliveries. The general directory structure that holds this file system
is shown in the figure.

.. figure:: figures/marine_file_system.png
    :width: 600px
    :align: center
    :alt: alternate text
    :figclass: align-center

    General marine directory structure

The following abbreviations are used throughout this manual:

* **NOC corrections**: ``<data_directory>/datasets/<dataset>/NOC_correction/<correction_version>``
* **NOC ancillaries**: ``<data_directory>/datasets/<dataset>/NOC_ANC_INFO/<noc_version>``
* **Pub47 files**: ``<data_directory>/datasets/<dataset>Pub47/<md_version>``
* **background climatologies**: ``<data_directory>/datasets/<dataset>/external_files``
* **level0 data**: ``<data_directory>/datasets/<dataset>/level0``
* **level1a data**: ``<data_directory>/datasets/<dataset>/level1a``
* **level1b data**: ``<data_directory>/datasets/<dataset>/level1b``
* **level1c data**: ``<data_directory>/datasets/<dataset>/level1c``
* **level1d data**: ``<data_directory>/datasets/<dataset>/level1d``
* **level1e data**: ``<data_directory>/datasets/<dataset>/level1e``
* **level2 data**: ``<data_directory>/datasets/<dataset>/level2``
* **level3 data**: ``<data_directory>/datasets/<dataset>/level3``
