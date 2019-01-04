import unittest

from peewee import *

from models import User

test_db = SqliteDatabase(':memory:')
MODELS = [User]

USER_DATA = {
    'username': 'test_user',
    'email': 'test@test.com',
    'password': 'password'
}


class UserModelTests(unittest.TestCase):
    def setUp(self):
        test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)
        test_db.connect()
        test_db.create_tables(MODELS)

    def tearDown(self):
        test_db.drop_tables(MODELS)
        test_db.close()

    @staticmethod
    def create_users(count=2):
         for i in range(count):
             User.create_user(
                username='test_user_{}'.format(i),
                email='test_{}@test.com'.format(i),
                password='password'
             )

    def test_create_user(self):
        self.create_users()
        self.assertEqual(User.select().count(), 2)
        self.assertNotEqual(
            User.select().get().password,
            'password'
        )

    def test_create_duplicate_user(self):
        self.create_users()
        with self.assertRaises(ValueError):
            User.create_user(
                username='test_user',
                email='test_1@test.com',
                password='password'
            )


if __name__ == '__main__':
    unittest.main()
