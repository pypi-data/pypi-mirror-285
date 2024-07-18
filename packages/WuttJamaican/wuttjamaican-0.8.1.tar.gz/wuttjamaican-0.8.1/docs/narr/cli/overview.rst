
Overview
========

Many apps will need some sort of command line usage, via cron or
otherwise.  There are two main aspects to it:

First there is the :term:`ad hoc script` which is a single file and
can be placed anywhere, but is not installed as part of a
:term:`package`.  See :doc:`scripts`.

But a "true" command line interface may define
:term:`commands<command>` and :term:`subcommands<subcommand>`, which
are then installed as part of a package.  See :doc:`commands` for more
about that.
