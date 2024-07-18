
WuttJamaican
============

This package provides a "base layer" for custom apps, regardless of
environment/platform:

* console
* web
* GUI

It mostly is a distillation of certain patterns developed within the
`Rattail Project`_, which are deemed generally useful.  (At least,
according to the author.)  It roughly corresponds to the "base layer"
as described in the Rattail Manual (see
:doc:`rattail-manual:base/index`).

.. _Rattail Project: https://rattailproject.org/

Good documentation and 100% `test coverage`_ are priorities for this
project.

.. _test coverage: https://buildbot.rattailproject.org/coverage/wuttjamaican/

Rattail is still the main use case so far, and will be refactored
along the way to incorporate what this package has to offer.


Features
--------

* flexible configuration, using config files and/or DB settings table
* flexible architecture, abstracting various portions of the overall app
* flexible database support, using `SQLAlchemy`_

.. _SQLAlchemy: https://www.sqlalchemy.org


Contents
--------

.. toctree::
   :maxdepth: 3

   glossary
   narr/index
   api/index


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
