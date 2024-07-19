# -*- coding: utf-8; -*-
################################################################################
#
#  WuttJamaican -- Base package for Wutta Framework
#  Copyright © 2023-2024 Lance Edgar
#
#  This file is part of Wutta Framework.
#
#  Wutta Framework is free software: you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option) any
#  later version.
#
#  Wutta Framework is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
#
#  You should have received a copy of the GNU General Public License along with
#  Wutta Framework.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
WuttJamaican - utilities
"""

import importlib
import logging
import shlex
from uuid import uuid1


log = logging.getLogger(__name__)


# nb. this is used as default kwarg value in some places, to
# distinguish passing a ``None`` value, vs. *no* value at all
UNSPECIFIED = object()


def load_entry_points(group, ignore_errors=False):
    """
    Load a set of ``setuptools``-style entry points.

    This is used to locate "plugins" and similar things, e.g. the set
    of subcommands which belong to a main command.

    :param group: The group (string name) of entry points to be
       loaded, e.g. ``'wutta.commands'``.

    :param ignore_errors: If false (the default), any errors will be
       raised normally.  If true, errors will be logged but not
       raised.

    :returns: A dictionary whose keys are the entry point names, and
       values are the loaded entry points.
    """
    entry_points = {}

    try:
        # nb. this package was added in python 3.8
        import importlib.metadata as importlib_metadata
    except ImportError:
        import importlib_metadata

    eps = importlib_metadata.entry_points()
    if not hasattr(eps, 'select'):
        # python < 3.10
        eps = eps.get(group, [])
    else:
        # python >= 3.10
        eps = eps.select(group=group)
    for entry_point in eps:
        try:
            ep = entry_point.load()
        except:
            if not ignore_errors:
                raise
            log.warning("failed to load entry point: %s", entry_point,
                        exc_info=True)
        else:
            entry_points[entry_point.name] = ep

    return entry_points


def load_object(spec):
    """
    Load an arbitrary object from a module, according to the spec.

    The spec string should contain a dotted path to an importable module,
    followed by a colon (``':'``), followed by the name of the object to be
    loaded.  For example:

    .. code-block:: none

       wuttjamaican.util:parse_bool

    You'll notice from this example that "object" in this context refers to any
    valid Python object, i.e. not necessarily a class instance.  The name may
    refer to a class, function, variable etc.  Once the module is imported, the
    ``getattr()`` function is used to obtain a reference to the named object;
    therefore anything supported by that approach should work.

    :param spec: Spec string.

    :returns: The specified object.
    """
    if not spec:
        raise ValueError("no object spec provided")

    module_path, name = spec.split(':')
    module = importlib.import_module(module_path)
    return getattr(module, name)


def make_uuid():
    """
    Generate a universally-unique identifier.

    :returns: A 32-character hex string.
    """
    return uuid1().hex


def parse_bool(value):
    """
    Derive a boolean from the given string value.
    """
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if str(value).lower() in ('true', 'yes', 'y', 'on', '1'):
        return True
    return False


def parse_list(value):
    """
    Parse a configuration value, splitting by whitespace and/or commas
    and taking quoting into account etc., yielding a list of strings.
    """
    if value is None:
        return []
    if isinstance(value, list):
        return value
    parser = shlex.shlex(value)
    parser.whitespace += ','
    parser.whitespace_split = True
    values = list(parser)
    for i, value in enumerate(values):
        if value.startswith('"') and value.endswith('"'):
            values[i] = value[1:-1]
        elif value.startswith("'") and value.endswith("'"):
            values[i] = value[1:-1]
    return values
