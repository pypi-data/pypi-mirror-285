
Quick Start
===========

Install with:

.. code-block:: sh

   pip install wuttjamaican

Create a config file, e.g. ``my.conf``:

.. code-block:: ini

   [foo]
   bar = A
   baz = 2
   feature = true
   words = the quick brown fox

In your app, load the config and reference its values as needed::

   from wuttjamaican.conf import make_config

   config = make_config('/path/to/my.conf')

   # this call..                        ..returns this value

   config.get('foo.bar')                # 'A'

   config.get('foo.baz')                # '2'
   config.get_int('foo.baz')            # 2

   config.get('foo.feature')            # 'true'
   config.get_bool('foo.feature')       # True

   config.get('foo.words')              # 'the quick brown fox'
   config.get_list('foo.words')         # ['the', 'quick', 'brown', 'fox']

For more info see:

* :func:`~wuttjamaican.conf.make_config()`
* :class:`~wuttjamaican.conf.WuttaConfig` and especially
  :meth:`~wuttjamaican.conf.WuttaConfig.get()`

You can also define your own command line interface; see
:doc:`/narr/cli/index`.
