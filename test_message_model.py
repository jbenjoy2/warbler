"""message model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


from app import app
import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows, Likes

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

        # create a sample user
        user = User.signup("test", "test@test.com", "testpass", None)
        self.uid = 111
        user.id = self.uid

        db.session.commit()

        self.user = User.query.get(self.uid)

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_message(self):
        """test basic model functionality"""
        msg = Message(
            text="a warble",
            user_id=self.uid
        )

        db.session.add(msg)
        db.session.commit()

        self.assertEqual(len(self.user.messages), 1)
        self.assertEqual(self.user.messages[0].text, 'a warble')

    def test_likes(self):
        """test message like functionality"""
        # add second user to like msg
        u2 = User.signup('test2', 'test2@test.com', 'testpass', None)
        uid = 234567
        u2.id = uid

        # add a message for u2 to like
        msg = Message(
            text="a warble",
            user_id=self.uid
        )

        db.session.add_all([u2, msg])
        db.session.commit()

        u2.likes.append(msg)
        db.session.commit()

        likes = Likes.query.filter(Likes.user_id == uid).all()
        self.assertEqual(len(likes), 1)
        self.assertEqual(likes[0].message_id, msg.id)
