# -*- coding: utf-8; -*-

from unittest import TestCase

try:
    import sqlalchemy as sa
    from wuttjamaican.db.model import base as model
    from wuttjamaican.db.model.auth import User
except ImportError:
    pass
else:

    class TestUUIDColumn(TestCase):

        def test_basic(self):
            column = model.uuid_column()
            self.assertIsInstance(column, sa.Column)
            self.assertIsInstance(column.type, sa.String)
            self.assertEqual(column.type.length, 32)

    class TestUUIDFKColumn(TestCase):

        def test_basic(self):
            column = model.uuid_fk_column('foo.bar')
            self.assertIsInstance(column, sa.Column)
            self.assertIsInstance(column.type, sa.String)
            self.assertEqual(column.type.length, 32)

    class TestSetting(TestCase):

        def test_basic(self):
            setting = model.Setting()
            self.assertEqual(str(setting), "")
            setting.name = 'foo'
            self.assertEqual(str(setting), "foo")

    class TestPerson(TestCase):

        def test_basic(self):
            person = model.Person()
            self.assertEqual(str(person), "")
            person.full_name = "Barney Rubble"
            self.assertEqual(str(person), "Barney Rubble")

        def test_users(self):
            person = model.Person()
            self.assertIsNone(person.user)

            user = User()
            person.users.append(user)
            self.assertIs(person.user, user)
