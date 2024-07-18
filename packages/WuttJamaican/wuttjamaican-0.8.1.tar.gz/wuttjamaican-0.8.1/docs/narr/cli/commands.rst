
Commands
========

WuttJamaican in fact does not directly provide a way to define a
command line interface for your app.

The reason is that several good frameworks exist already.  You are
encouraged to use one of the following to define
:term:`commands<command>` and :term:`subcommands<subcommand>` as
needed:

* `Typer <https://typer.tiangolo.com/>`_
* `Click <https://click.palletsprojects.com/en/latest/>`_
* :mod:`python:argparse`

For even more options see:

* `awesome-cli-framework <https://github.com/shadawck/awesome-cli-frameworks/blob/master/README.md#python>`_
* `Hitchhiker’s Guide to Python <https://docs.python-guide.org/scenarios/cli/>`_
* `Python Wiki <https://wiki.python.org/moin/CommandlineTools>`_

Or if that is overkill you can always just use :doc:`scripts`.
