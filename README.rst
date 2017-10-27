========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - |
        |
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|

.. |docs| image:: https://readthedocs.org/projects/git-doccommit/badge/?style=flat
    :target: https://readthedocs.org/projects/git-doccommit
    :alt: Documentation Status

.. |version| image:: https://img.shields.io/pypi/v/git-doccommit.svg
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/git-doccommit

.. |commits-since| image:: https://img.shields.io/github/commits-since/svenseeberg/git-doccommit/v1.0.3.svg
    :alt: Commits since latest release
    :target: https://github.com/svenseeberg/git-doccommit/compare/v1.0.3...master

.. |wheel| image:: https://img.shields.io/pypi/wheel/git-doccommit.svg
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/git-doccommit

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/git-doccommit.svg
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/git-doccommit

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/git-doccommit.svg
    :alt: Supported implementations
    :target: https://pypi.python.org/pypi/git-doccommit


.. end-badges

Helps to write well formatted git commit messages that can be used for SUSE documentation doc u

* Free software: MIT license

Installation
============

::

    pip install git-doccommit

Documentation
=============

https://git-doccommit.readthedocs.io/

Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
