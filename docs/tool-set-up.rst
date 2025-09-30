.. Marine observations suite documentation master file, created by
   sphinx-quickstart on Thu Jul 23 07:39:51 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Tool set-up
===========

Code repository
---------------

The full set of suites that make up the marine code are integrated in the
glamod-marine-processing repository. Thus, to install the observations suite,
the repository needs to be cloned:

.. code-block:: bash

  git clone https://github.com/glamod/glamod-marine-processing

Installation
------------

Once you have a copy of the source, you can install it with pip_:

.. code-block:: console

   pip install -e .

If you're interested in participating in the development of the **glamod-marine-processing**, you can install the package in development mode after cloning the repository from source:

.. code-block:: console

    pip install -e .[dev]      # Install optional development dependencies in addition
    pip install -e .[docs]     # Install optional dependencies for the documentation in addition
    pip install -e .[all]      # Install all the above for complete dependency version


Setting paths and environments
------------------------------

The paths for the processing software and data files, including both a data directory and a release directory
for the user running the software has to be set in a configuration file.

* **glamod**: full path to user-specific release directory
* **data_directory**: full path to marine data file system.

These paths are pre-defined for KAY, MeluXina and BASTION. The default machine is BASTION.
If you want to work on another marine, please create a new configuration file with the name of your machine in it:

``glamod_marine_processing/configuration_files/config_<your_machine>.json``

Other directories that will be needed for processing the data will be created
automatically while calling the software the first time.
