.. image:: https://github.com/GalKepler/neuroflow/blob/main/assets/neuroflow.png?raw=true
    :align: center

========
Overview
========
.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests, CI & coverage
      - |github-actions| |codecov| |codacy|
    * - version
      - |pypi| |python|
    * - styling
      - |black| |isort| |flake8| |pre-commit|
    * - license
      - |license|

.. |codacy| image:: https://app.codacy.com/project/badge/Grade/6acd65a8fd4741509422510d7a023386
    :target: https://app.codacy.com/gh/GalKepler/neuroflow/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade
    :alt: Code Quality

.. |docs| image:: https://readthedocs.org/projects/neuroflow/badge/?style=flat
    :target: https://readthedocs.org/projects/neuroflow/
    :alt: Documentation Status

.. |github-actions| image:: https://github.com/GalKepler/neuroflow/actions/workflows/github-actions.yml/badge.svg
    :alt: GitHub Actions Build Status
    :target: https://github.com/GalKepler/neuroflow/actions

.. |codecov| image:: https://codecov.io/github/GalKepler/neuroflow/graph/badge.svg?token=LO5CH471O4
    :alt: Coverage Status
    :target: https://app.codecov.io/github/GalKepler/neuroflow

.. |license| image:: https://img.shields.io/github/license/GalKepler/neuroflow.svg
        :target: https://opensource.org/license/mit
        :alt: License

.. |pypi| image:: https://img.shields.io/pypi/v/neuroflow-yalab.svg
        :target: https://pypi.python.org/pypi/neuroflow-yalab

.. |python| image:: https://img.shields.io/pypi/pyversions/neuroflow-yalab
        :target: https://www.python.org

.. |black| image:: https://img.shields.io/badge/formatter-black-000000.svg
        :target: https://github.com/psf/black

.. |isort| image:: https://img.shields.io/badge/imports-isort-%231674b1.svg
        :target: https://pycqa.github.io/isort/

.. |flake8| image:: https://img.shields.io/badge/style-flake8-000000.svg
        :target: https://flake8.pycqa.org/en/latest/

.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
        :target: https://github.com/pre-commit/pre-commit


NeuroFlow: A streamlined toolkit for DWI post-processing, offering advanced analysis and visualization for neuroimaging research.


* Free software: MIT license
* Documentation: https://neuroflow.readthedocs.io.


Features
--------

* Estimation of tensor derivatives (FA, MD, AD, RD, etc.) using either `MRtrix3 <https://www.mrtrix.org/>`_ or `DIPY <https://dipy.org/>`_.
* Registration of numerous volumetric parcellation atlases to subjects' native T1w and DWI images.
* Estimation of numerous distribution metrices (e.g. mean, median, IQR-mean, etc.) of diffusion metrics within each parcellation unit.
* Automatic extraction of available covariates originating from different sources (demographics, temporal, environmental).
* Quality control of the preprocessing of the diffusion MRI data.


Usage
-----

Basic Usage
~~~~~~~~~~~

.. code-block:: bash

    $ neuroflow process <input_dir> <output_dir> <google_credentials>


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
