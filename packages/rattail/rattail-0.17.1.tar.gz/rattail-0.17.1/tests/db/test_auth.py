# -*- coding: utf-8; -*-

try:
    from rattail.db import auth, model
    from .. import DataTestCase
except ImportError:
    pass
else:

    class TestAuthenticateUser(DataTestCase):

        def test_nonexistent_user_returns_none(self):
            self.assertTrue(auth.authenticate_user(self.session, u'fred', u'fredpass') is None)

        def test_correct_credentials_returns_user(self):
            fred = model.User(username=u'fred')
            auth.set_user_password(fred, u'fredpass')
            self.session.add(fred)
            self.session.commit()
            user = auth.authenticate_user(self.session, u'fred', u'fredpass')
            self.assertTrue(user is fred)

        def test_wrong_password_user_returns_none(self):
            fred = model.User(username=u'fred', active=False)
            auth.set_user_password(fred, u'fredpass')
            self.session.add(fred)
            self.session.commit()
            self.assertTrue(auth.authenticate_user(self.session, u'fred', u'BADPASS') is None)

        def test_inactive_user_returns_none(self):
            fred = model.User(username=u'fred', active=False)
            auth.set_user_password(fred, u'fredpass')
            self.session.add(fred)
            self.session.commit()
            self.assertTrue(auth.authenticate_user(self.session, u'fred', u'fredpass') is None)
