# -*- coding: utf-8; -*-

import os
import shutil
import tempfile
import warnings
from unittest import TestCase
from unittest.mock import patch, MagicMock

import pytest

from wuttjamaican import app
from wuttjamaican.conf import WuttaConfig
from wuttjamaican.util import UNSPECIFIED


class TestAppHandler(TestCase):

    def setUp(self):
        self.config = WuttaConfig(appname='wuttatest')
        self.app = app.AppHandler(self.config)
        self.config.app = self.app

    def test_init(self):
        self.assertIs(self.app.config, self.config)
        self.assertEqual(self.app.handlers, {})
        self.assertEqual(self.app.appname, 'wuttatest')

    def test_load_object(self):

        # just confirm the method works on a basic level; the
        # underlying function is tested elsewhere
        obj = self.app.load_object('wuttjamaican.util:UNSPECIFIED')
        self.assertIs(obj, UNSPECIFIED)

    def test_make_appdir(self):

        # appdir is created, and 3 subfolders added by default
        tempdir = tempfile.mkdtemp()
        appdir = os.path.join(tempdir, 'app')
        self.assertFalse(os.path.exists(appdir))
        self.app.make_appdir(appdir)
        self.assertTrue(os.path.exists(appdir))
        self.assertEqual(len(os.listdir(appdir)), 3)
        shutil.rmtree(tempdir)

        # subfolders still added if appdir already exists
        tempdir = tempfile.mkdtemp()
        self.assertTrue(os.path.exists(tempdir))
        self.assertEqual(len(os.listdir(tempdir)), 0)
        self.app.make_appdir(tempdir)
        self.assertEqual(len(os.listdir(tempdir)), 3)
        shutil.rmtree(tempdir)

    def test_make_session(self):
        try:
            from wuttjamaican import db
        except ImportError:
            pytest.skip("test is not relevant without sqlalchemy")

        session = self.app.make_session()
        self.assertIsInstance(session, db.Session.class_)

    def test_short_session(self):
        short_session = MagicMock()
        mockdb = MagicMock(short_session=short_session)

        with patch.dict('sys.modules', **{'wuttjamaican.db': mockdb}):

            with self.app.short_session(foo='bar') as s:
                short_session.assert_called_once_with(
                    foo='bar', factory=self.app.make_session)

    def test_get_setting(self):
        try:
            import sqlalchemy as sa
            from sqlalchemy import orm
        except ImportError:
            pytest.skip("test is not relevant without sqlalchemy")

        Session = orm.sessionmaker()
        engine = sa.create_engine('sqlite://')
        session = Session(bind=engine)
        session.execute(sa.text("""
        create table setting (
                name varchar(255) primary key,
                value text
        );
        """))
        session.commit()

        value = self.app.get_setting(session, 'foo')
        self.assertIsNone(value)

        session.execute(sa.text("insert into setting values ('foo', 'bar');"))
        value = self.app.get_setting(session, 'foo')
        self.assertEqual(value, 'bar')

    def test_model(self):
        try:
            from wuttjamaican.db import model
        except ImportError:
            pytest.skip("test not relevant without sqlalchemy")

        self.assertNotIn('model', self.app.__dict__)
        self.assertIs(self.app.model, model)

    def test_get_model(self):
        try:
            from wuttjamaican.db import model
        except ImportError:
            pytest.skip("test not relevant without sqlalchemy")

        self.assertIs(self.app.get_model(), model)

    def test_get_title(self):
        self.assertEqual(self.app.get_title(), 'WuttJamaican')

    def test_make_uuid(self):
        uuid = self.app.make_uuid()
        self.assertEqual(len(uuid), 32)

    def test_get_session(self):
        try:
            import sqlalchemy as sa
            from sqlalchemy import orm
        except ImportError:
            pytest.skip("test not relevant without sqlalchemy")

        model = self.app.model
        user = model.User()
        self.assertIsNone(self.app.get_session(user))

        Session = orm.sessionmaker()
        engine = sa.create_engine('sqlite://')
        mysession = Session(bind=engine)
        mysession.add(user)
        session = self.app.get_session(user)
        self.assertIs(session, mysession)

    def test_get_person(self):
        people = self.app.get_people_handler()
        with patch.object(people, 'get_person') as get_person:
            get_person.return_value = 'foo'
            person = self.app.get_person('bar')
            get_person.assert_called_once_with('bar')
            self.assertEqual(person, 'foo')

    def test_get_auth_handler(self):
        from wuttjamaican.auth import AuthHandler

        auth = self.app.get_auth_handler()
        self.assertIsInstance(auth, AuthHandler)

    def test_get_people_handler(self):
        from wuttjamaican.people import PeopleHandler

        people = self.app.get_people_handler()
        self.assertIsInstance(people, PeopleHandler)


class TestAppProvider(TestCase):

    def setUp(self):
        self.config = WuttaConfig(appname='wuttatest')
        self.app = app.AppHandler(self.config)
        self.config._app = self.app

    def test_constructor(self):

        # config object is expected
        provider = app.AppProvider(self.config)
        self.assertIs(provider.config, self.config)
        self.assertIs(provider.app, self.app)
        self.assertEqual(provider.appname, 'wuttatest')

        # but can pass app handler instead
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=DeprecationWarning)
            provider = app.AppProvider(self.app)
        self.assertIs(provider.config, self.config)
        self.assertIs(provider.app, self.app)

    def test_get_all_providers(self):

        class FakeProvider(app.AppProvider):
            pass

        # nb. we specify *classes* here
        fake_providers = {'fake': FakeProvider}

        with patch('wuttjamaican.app.load_entry_points') as load_entry_points:
            load_entry_points.return_value = fake_providers

            # sanity check, we get *instances* back from this
            providers = self.app.get_all_providers()
            load_entry_points.assert_called_once_with('wutta.app.providers')
            self.assertEqual(len(providers), 1)
            self.assertIn('fake', providers)
            self.assertIsInstance(providers['fake'], FakeProvider)

    def test_hasattr(self):

        class FakeProvider(app.AppProvider):
            def fake_foo(self):
                pass

        self.app.providers = {'fake': FakeProvider(self.config)}

        self.assertTrue(hasattr(self.app, 'fake_foo'))
        self.assertFalse(hasattr(self.app, 'fake_method_does_not_exist'))

    def test_getattr(self):

        class FakeProvider(app.AppProvider):
            def fake_foo(self):
                return 42

        # nb. using instances here
        fake_providers = {'fake': FakeProvider(self.config)}

        with patch.object(self.app, 'get_all_providers') as get_all_providers:
            get_all_providers.return_value = fake_providers

            self.assertNotIn('providers', self.app.__dict__)
            self.assertIs(self.app.providers, fake_providers)
            get_all_providers.assert_called_once_with()

    def test_getattr_providers(self):

        # collection of providers is loaded on demand
        self.assertNotIn('providers', self.app.__dict__)
        self.assertIsNotNone(self.app.providers)

        # custom attr does not exist yet
        self.assertRaises(AttributeError, getattr, self.app, 'foo_value')

        # but provider can supply the attr
        self.app.providers['mytest'] = MagicMock(foo_value='bar')
        self.assertEqual(self.app.foo_value, 'bar')


class TestGenericHandler(TestCase):

    def setUp(self):
        self.config = WuttaConfig(appname='wuttatest')
        self.app = app.AppHandler(self.config)
        self.config._app = self.app

    def test_constructor(self):
        handler = app.GenericHandler(self.config)
        self.assertIs(handler.config, self.config)
        self.assertIs(handler.app, self.app)
        self.assertEqual(handler.appname, 'wuttatest')
