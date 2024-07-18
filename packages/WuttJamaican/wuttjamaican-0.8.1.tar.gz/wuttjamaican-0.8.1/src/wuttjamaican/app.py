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
WuttJamaican - app handler
"""

import importlib
import os
import warnings

from wuttjamaican.util import load_entry_points, load_object, make_uuid, parse_bool


class AppHandler:
    """
    Base class and default implementation for top-level :term:`app
    handler`.

    aka. "the handler to handle all handlers"

    aka. "one handler to bind them all"

    For more info see :doc:`/narr/handlers/app`.

    There is normally no need to create one of these yourself; rather
    you should call :meth:`~wuttjamaican.conf.WuttaConfig.get_app()`
    on the :term:`config object` if you need the app handler.

    :param config: Config object for the app.  This should be an
       instance of :class:`~wuttjamaican.conf.WuttaConfig`.

    .. attribute:: model

       Reference to the :term:`app model` module.

       Note that :meth:`get_model()` is responsible for determining
       which module this will point to.  However you can always get
       the model using this attribute (e.g. ``app.model``) and do not
       need to call :meth:`get_model()` yourself - that part will
       happen automatically.

    .. attribute:: providers

       Dictionary of :class:`AppProvider` instances, as returned by
       :meth:`get_all_providers()`.
    """
    default_app_title = "WuttJamaican"
    default_model_spec = 'wuttjamaican.db.model'
    default_auth_handler_spec = 'wuttjamaican.auth:AuthHandler'
    default_people_handler_spec = 'wuttjamaican.people:PeopleHandler'

    def __init__(self, config):
        self.config = config
        self.handlers = {}

    @property
    def appname(self):
        """
        The :term:`app name` for the current app.  This is just an
        alias for :attr:`wuttjamaican.conf.WuttaConfig.appname`.

        Note that this ``appname`` does not necessariy reflect what
        you think of as the name of your (e.g. custom) app.  It is
        more fundamental than that; your Python package naming and the
        :term:`app title` are free to use a different name as their
        basis.
        """
        return self.config.appname

    def __getattr__(self, name):
        """
        Custom attribute getter, called when the app handler does not
        already have an attribute with the given ``name``.

        This will delegate to the set of :term:`app providers<app
        provider>`; the first provider with an appropriately-named
        attribute wins, and that value is returned.

        :returns: The first value found among the set of app
           providers.
        """

        if name == 'model':
            return self.get_model()

        if name == 'providers':
            self.providers = self.get_all_providers()
            return self.providers

        for provider in self.providers.values():
            if hasattr(provider, name):
                return getattr(provider, name)

        raise AttributeError(f"attr not found: {name}")

    def get_all_providers(self):
        """
        Load and return all registered providers.

        Note that you do not need to call this directly; instead just
        use :attr:`providers`.

        The discovery logic is based on :term:`entry points<entry
        point>` using the ``wutta.app.providers`` group.  For instance
        here is a sample entry point used by WuttaWeb (in its
        ``pyproject.toml``):

        .. code-block:: toml

           [project.entry-points."wutta.app.providers"]
           wuttaweb = "wuttaweb.app:WebAppProvider"

        :returns: Dictionary keyed by entry point name; values are
           :class:`AppProvider` instances.
        """
        # nb. must use 'wutta' and not self.appname prefix here, or
        # else we can't find all providers with custom appname
        providers = load_entry_points('wutta.app.providers')
        for key in list(providers):
            providers[key] = providers[key](self.config)
        return providers

    def get_title(self, default=None):
        """
        Returns the configured title for the app.

        :param default: Value to be returned if there is no app title
           configured.

        :returns: Title for the app.
        """
        return self.config.get(f'{self.appname}.app_title',
                               default=default or self.default_app_title)

    def get_model(self):
        """
        Returns the :term:`app model` module.

        Note that you don't actually need to call this method; you can
        get the model by simply accessing :attr:`model`
        (e.g. ``app.model``) instead.

        By default this will return :mod:`wuttjamaican.db.model`
        unless the config class or some :term:`config extension` has
        provided another default.

        A custom app can override the default like so (within a config
        extension)::

           config.setdefault('wutta.model_spec', 'poser.db.model')
        """
        if 'model' not in self.__dict__:
            spec = self.config.get(f'{self.appname}.model_spec',
                                   usedb=False,
                                   default=self.default_model_spec)
            self.model = importlib.import_module(spec)
        return self.model

    def load_object(self, spec):
        """
        Import and/or load and return the object designated by the
        given spec string.

        This invokes :func:`wuttjamaican.util.load_object()`.

        :param spec: String of the form ``module.dotted.path:objname``.

        :returns: The object referred to by ``spec``.  If the module
           could not be imported, or did not contain an object of the
           given name, then an error will raise.
        """
        return load_object(spec)

    def make_appdir(self, path, subfolders=None, **kwargs):
        """
        Establish an :term:`app dir` at the given path.

        Default logic only creates a few subfolders, meant to help
        steer the admin toward a convention for sake of where to put
        things.  But custom app handlers are free to do whatever.

        :param path: Path to the desired app dir.  If the path does
           not yet exist then it will be created.  But regardless it
           should be "refreshed" (e.g. missing subfolders created)
           when this method is called.

        :param subfolders: Optional list of subfolder names to create
           within the app dir.  If not specified, defaults will be:
           ``['data', 'log', 'work']``.
        """
        appdir = path
        if not os.path.exists(appdir):
            os.makedirs(appdir)

        if not subfolders:
            subfolders = ['data', 'log', 'work']

        for name in subfolders:
            path = os.path.join(appdir, name)
            if not os.path.exists(path):
                os.mkdir(path)

    def make_session(self, **kwargs):
        """
        Creates a new SQLAlchemy session for the app DB.  By default
        this will create a new :class:`~wuttjamaican.db.sess.Session`
        instance.

        :returns: SQLAlchemy session for the app DB.
        """
        from .db import Session

        return Session(**kwargs)

    def make_uuid(self):
        """
        Generate a new UUID value.

        By default this simply calls
        :func:`wuttjamaican.util.make_uuid()`.

        :returns: UUID value as 32-character string.
        """
        return make_uuid()

    def get_session(self, obj):
        """
        Returns the SQLAlchemy session with which the given object is
        associated.  Simple convenience wrapper around
        :func:`sqlalchemy:sqlalchemy.orm.object_session()`.
        """
        from sqlalchemy import orm

        return orm.object_session(obj)

    def short_session(self, **kwargs):
        """
        Returns a context manager for a short-lived database session.

        This is a convenience wrapper around
        :class:`~wuttjamaican.db.sess.short_session`.

        If caller does not specify ``factory`` nor ``config`` params,
        this method will provide a default factory in the form of
        :meth:`make_session`.
        """
        from .db import short_session

        if 'factory' not in kwargs and 'config' not in kwargs:
            kwargs['factory'] = self.make_session

        return short_session(**kwargs)

    def get_setting(self, session, name, **kwargs):
        """
        Get a setting value from the DB.

        This does *not* consult the config object directly to
        determine the setting value; it always queries the DB.

        Default implementation is just a convenience wrapper around
        :func:`~wuttjamaican.db.conf.get_setting()`.

        :param session: App DB session.

        :param name: Name of the setting to get.

        :returns: Setting value as string, or ``None``.
        """
        from .db import get_setting

        return get_setting(session, name)

    ##############################
    # getters for other handlers
    ##############################

    def get_auth_handler(self, **kwargs):
        """
        Get the configured :term:`auth handler`.

        :rtype: :class:`~wuttjamaican.auth.AuthHandler`
        """
        if 'auth' not in self.handlers:
            spec = self.config.get(f'{self.appname}.auth.handler',
                                   default=self.default_auth_handler_spec)
            factory = self.load_object(spec)
            self.handlers['auth'] = factory(self.config, **kwargs)
        return self.handlers['auth']

    def get_people_handler(self, **kwargs):
        """
        Get the configured "people" :term:`handler`.

        :rtype: :class:`~wuttjamaican.people.PeopleHandler`
        """
        if 'people' not in self.handlers:
            spec = self.config.get(f'{self.appname}.people.handler',
                                   default=self.default_people_handler_spec)
            factory = self.load_object(spec)
            self.handlers['people'] = factory(self.config, **kwargs)
        return self.handlers['people']

    ##############################
    # convenience delegators
    ##############################

    def get_person(self, obj, **kwargs):
        """
        Convenience method to locate a
        :class:`~wuttjamaican.db.model.base.Person` for the given
        object.

        This delegates to the "people" handler method,
        :meth:`~wuttjamaican.people.PeopleHandler.get_person()`.
        """
        return self.get_people_handler().get_person(obj, **kwargs)


class AppProvider:
    """
    Base class for :term:`app providers<app provider>`.

    These can add arbitrary extra functionality to the main :term:`app
    handler`.  See also :doc:`/narr/providers/app`.

    :param config: The app :term:`config object`.

    Instances have the following attributes:

    .. attribute:: config

       Reference to the config object.

    .. attribute:: app

       Reference to the parent app handler.
    """

    def __init__(self, config):

        if isinstance(config, AppHandler):
            warnings.warn("passing app handler to app provider is deprecated; "
                          "must pass config object instead",
                          DeprecationWarning, stacklevel=2)
            config = config.config

        self.config = config
        self.app = self.config.get_app()

    @property
    def appname(self):
        """
        The :term:`app name` for the current app.

        See also :attr:`AppHandler.appname`.
        """
        return self.app.appname


class GenericHandler:
    """
    Generic base class for handlers.

    When the :term:`app` defines a new *type* of :term:`handler` it
    may subclass this when defining the handler base class.

    :param config: Config object for the app.  This should be an
       instance of :class:`~wuttjamaican.conf.WuttaConfig`.
    """

    def __init__(self, config, **kwargs):
        self.config = config
        self.app = self.config.get_app()

    @property
    def appname(self):
        """
        The :term:`app name` for the current app.

        See also :attr:`AppHandler.appname`.
        """
        return self.app.appname
