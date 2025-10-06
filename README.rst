==================================================================
GLAMOD marine processing: ``glamod-marine-processing`` toolbox
==================================================================

+----------------------------+-----------------------------------------------------+
| Versions                   | |tag| |release|                                     |
+----------------------------+-----------------------------------------------------+
| Documentation and Support  | |docs|                                              |
+----------------------------+-----------------------------------------------------+
| Open Source                | |license| |zenodo| |fair-software|                  |
+----------------------------+-----------------------------------------------------+
| Coding Standards           | |black| |ruff| |pre-commit| |fossa| |codefactor|    |
+----------------------------+-----------------------------------------------------+
| Development Status         | |status| |build| |coveralls|                        |
+----------------------------+-----------------------------------------------------+
| Funding                    | |funding| |noc|                                     |
+----------------------------+-----------------------------------------------------+

``glamod-marine-processing`` is a python tool for creating SLURM scripts for several GLAMOD marine processing workflows.
Once installed you can use it as an command-line interface. For more information, please call the help functions:

.. code-block:: console

    pre_proc --help        # Preprocessing steps to create level0 data
    obs_suite --help       # Observations workflow help page
    merge_suite  --help    # Step to merge multiple available decks into one single deck
    split_suite --help     # Step to split one single available deck into multiple decks

Installation
------------
Before you install ``glamod-marine-processing`` please clone the GitHub repository.

.. code-block:: console

    git clone https://github.com/glamod/glamod-marine-processing
    cd glamod-marine-processing

Now you can install several dependency versions:

.. code-block:: console

    pip install -e .           # Install minimum dependency version

This will install the package but you can still edit it and you don't need the package in your :code:`PYTHONPATH`.

Documentation
-------------

The official documentation is at https://glamod-marine-processing.readthedocs.io/

Contributing to glamod-marine-processing
----------------------------------------

If you're interested in participating in the development of `glamod-marine-processing` by suggesting new features, new indices or report bugs, please leave us a message on the `issue tracker`_.

If you would like to contribute code or documentation (which is greatly appreciated!), check out the `Contributing Guidelines`_ before you begin!

How to cite this library
------------------------

If you wish to cite `glamod-marine-processing` in a research publication, we kindly ask that you refer to Zenodo: https://doi.org/10.5281/zenodo.14215566.

License
-------

This is free software: you can redistribute it and/or modify it under the terms of the `Apache License 2.0`_. A copy of this license is provided in the code repository (`LICENSE`_).

Credits
-------

``glamod-marine-processing`` development is funded through Copernicus Climate Change Service (C3S_).

Furthermore, acknowledgments go to National Oceanography Centre (NOC_).

We want to thank `GNU parallel`_ for optionally using the ``glamod-marine-processing`` suite cases in parallel.

This package was created with Cookiecutter_ and the `audreyfeldroy/cookiecutter-pypackage`_ project template.

.. _Apache License 2.0: https://opensource.org/license/apache-2-0/

.. _audreyfeldroy/cookiecutter-pypackage: https://github.com/audreyfeldroy/cookiecutter-pypackage/

.. _C3S: https://climate.copernicus.eu/

.. _Contributing Guidelines: https://github.com/glamod/glamod-marine-processing/blob/master/CONTRIBUTING.rst

.. _Cookiecutter: https://github.com/cookiecutter/cookiecutter/

.. _issue tracker: https://github.com/glamod/glamod-marine-processing/issues

.. _LICENSE: https://github.com/glamod/glamod-marine-processing/blob/master/LICENSE

.. _NOC: https://noc.ac.uk/

.. _GNU parallel: https://doi.org/10.5281/zenodo.12789352

.. |build| image:: https://github.com/glamod/glamod-marine-processing/actions/workflows/testing_suite.yml/badge.svg
        :target: https://github.com/glamod/glamod-marine-processing/actions/workflows/testing_suite.yml
        :alt: Build Status

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
        :target: https://github.com/psf/black
        :alt: Python Black

.. |codefactor| image:: https://www.codefactor.io/repository/github/glamod/glamod-marine-processing/badge
		:target: https://www.codefactor.io/repository/github/glamod/glamod-marine-processing
		:alt: CodeFactor

.. |coveralls| image:: https://codecov.io/gh/glamod/glamod-marine-processing/graph/badge.svg
	      :target: https://codecov.io/gh/glamod/glamod-marine-processing
	      :alt: Coveralls

.. |docs| image:: https://readthedocs.org/projects/glamod_marine_processing/badge/?version=latest
        :target: https://glamod-marine-processing.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status

.. |fair-software| image:: https://img.shields.io/badge/fair--software.eu-%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8B%20%20%E2%97%8F%20%20%E2%97%8B-orange
   	    :target: https://fair-software.eu
	      :alt: FAIR-software

.. |fossa| image:: https://app.fossa.com/api/projects/git%2Bgithub.com%2Fglamod%2Fglamod-marine-processing.svg?type=shield
        :target: https://app.fossa.com/projects/git%2Bgithub.com%2Fglamod%2Fglamod-marine-processing?ref=badge_shield
        :alt: FOSSA

.. |funding| image:: https://img.shields.io/badge/Powered%20by-Copernicus-blue.svg
        :target: https://climate.copernicus.eu/
        :alt: Funding

.. |license| image:: https://img.shields.io/github/license/glamod/glamod-marine-processing.svg
        :target: https://github.com/glamod/glamod-marine-processing/blob/main/LICENSE
        :alt: License

.. |noc| image:: https://img.shields.io/badge/Thanks%20to-NOC-blue.svg
        :target: https://noc.ac.uk/
        :alt: NOC

.. |pre-commit| image:: https://results.pre-commit.ci/badge/github/glamod/glamod-marine-processing/master.svg
   :target: https://results.pre-commit.ci/latest/github/glamod/glamod-marine-processing/master
   :alt: pre-commit.ci status

.. |ruff| image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
        :target: https://github.com/astral-sh/ruff
        :alt: Ruff

.. |status| image:: https://www.repostatus.org/badges/latest/active.svg
        :target: https://www.repostatus.org/#active
        :alt: Project Status: Active – The project has reached a stable, usable state and is being actively developed.

.. |release| image:: https://img.shields.io/github/v/release/glamod/glamod-marine-processing.svg
        :target: https://github.com/glamod/glamod-marine-processing/releases
        :alt: Release

.. |tag| image:: https://img.shields.io/github/v/tag/glamod/glamod-marine-processing.svg
        :target: https://github.com/glamod/glamod-marine-processing/tags
        :alt: Tag

.. |zenodo| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.14215566.svg
  	:target: https://doi.org/10.5281/zenodo.14215566
 	:alt: DOI

.. |noc| image:: https://img.shields.io/badge/Thanks%20to-NOC-blue.svg
        :target: https://noc.ac.uk/
        :alt: NOC
