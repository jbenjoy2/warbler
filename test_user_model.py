"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


from app import app
import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        # create two users to follow each other
        user1 = User.signup("u1", "u1@test.com", "testpass", None)
        id1 = 111
        user1.id = id1

        user2 = User.signup("u2", "u2@test.com", "testpass", None)
        id2 = 222
        user2.id = id2

        db.session.commit()

        u1 = User.query.get(id1)
        u2 = User.query.get(id2)

        self.user1 = u1
        self.user2 = u2
        self.id1 = id1
        self.id2 = id2

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_follows(self):
        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertEqual(len(self.user1.following), 1)
        self.assertEqual(len(self.user2.following), 0)
        self.assertEqual(len(self.user1.followers), 0)
        self.assertEqual(len(self.user2.followers), 1)

        # test to make sure correct users are in followers lists

        self.assertEqual(self.user2.followers[0].id, self.user1.id)
        self.assertEqual(self.user1.following[0].id, self.user2.id)

    def test_following_method(self):
        """method returns boolean"""
        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertTrue(self.user1.is_following(self.user2))
        self.assertFalse(self.user2.is_following(self.user1))

    def test_followed_method(self):
        """method returns boolean"""

        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertTrue(self.user2.is_followed_by(self.user1))
        self.assertFalse(self.user1.is_followed_by(self.user2))

    def test_good_signup(self):
        """make sure if all info is given, user is returned"""

        test_user = User.signup("test", "test@test.com", "testpass", None)
        test_user.id = 123456
        db.session.commit()

        user = User.query.get(123456)

        # test user exists after quer7
        self.assertIsNotNone(user)
        # test that queried user comes up with correct info
        self.assertEqual(user.username, "test")
        self.assertEqual(user.email, "test@test.com")
        # test password got hashed by bcrypt and didnt get stored as plaintext
        self.assertNotEqual(user.password, "testpass")
        self.assertTrue(user.password.startswith("$2b$"))

    def test_missing_email_signup(self):
        """email is meant to be not nullable"""
        test = User.signup("test", None, "testpass", None)
        test.id = 123456
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_missing_username_signup(self):
        """username is meant to be not nullable"""
        test = User.signup(None, "test@test.com", "testpass", None)
        test.id = 123456
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_missing_password_signup(self):
        """password is meant to be not nullable"""
        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "email@email.com", "", None)

        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "email@email.com", None, None)

    def test_auth(self):
        user = User.authenticate(self.user1.username, "testpass")
        self.assertIsNotNone(user)
        self.assertEqual(user.id, self.id1)

    def test_bad_auth(self):
        self.assertFalse(User.authenticate('abcdefg', 'badpassword'))
