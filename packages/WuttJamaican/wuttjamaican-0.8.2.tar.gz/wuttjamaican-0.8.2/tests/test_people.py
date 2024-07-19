# -*- coding: utf-8; -*-

from unittest import TestCase

from wuttjamaican import people as mod
from wuttjamaican.conf import WuttaConfig

try:
    import sqlalchemy as sa
except ImportError:
    pass
else:


    class TestPeopleHandler(TestCase):

        def setUp(self):
            self.config = WuttaConfig()
            self.app = self.config.get_app()
            self.handler = mod.PeopleHandler(self.config)

            self.engine = sa.create_engine('sqlite://')
            self.app.model.Base.metadata.create_all(bind=self.engine)
            self.session = self.make_session()

        def tearDown(self):
            self.session.close()
            self.app.model.Base.metadata.drop_all(bind=self.engine)

        def make_session(self):
            return self.app.make_session(bind=self.engine)

        def test_get_person(self):
            model = self.app.model
            myperson = model.Person(full_name='Barny Rubble')
            self.session.add(myperson)
            self.session.commit()

            # empty obj is ignored
            person = self.handler.get_person(None)
            self.assertIsNone(person)

            # person is returned as-is
            person = self.handler.get_person(myperson)
            self.assertIs(person, myperson)

            # find person from user
            myuser = model.User(username='barney', person=myperson)
            self.session.add(myuser)
            self.session.commit()
            person = self.handler.get_person(myuser)
            self.assertIs(person, myperson)
