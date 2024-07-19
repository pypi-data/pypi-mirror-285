=============================
Django Cashier
=============================

.. image:: https://circleci.com/gh/kaleemibnanwar/dj-cashier.svg?style=svg
    :target: https://circleci.com/gh/kaleemibnanwar/dj-cashier

.. image:: https://codecov.io/gh/kaleemibnanwar/dj-cashier/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/kaleemibnanwar/dj-cashier

.. image:: https://readthedocs.org/projects/dj-cashier/badge/?version=latest
    :target: https://dj-cashier.readthedocs.io/en/latest/?badge=latest

.. image:: https://img.shields.io/pypi/pyversions/envision.svg

.. image:: https://img.shields.io/pypi/pyversions/dj-cashier.svg

.. image:: https://img.shields.io/pypi/v/dj-cashier.svg

.. image:: https://img.shields.io/pypi/wheel/dj-cashier.svg

Your project description goes here

Documentation
-------------

The full documentation is at https://dj-cashier.readthedocs.io.

Quickstart
----------

Install Django Cashier::

    pip install dj-cashier

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'dj_cashier',
        ...
    )

Add Django Cashier's URL patterns:

.. code-block:: python

    import dj_cashier

    urlpatterns = [
        ...
        url(r'^', include(dj_cashier.urls)),
        ...
    ]

Features
--------

* TODO

Running Tests
-------------

Does the code actually work?::

    $ cd dj-cashier
    $ poetry install
    $ poetry run runtests.py

Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
