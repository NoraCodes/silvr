# Unit Testing for Silvr Blog
import os
import silvr
import unittest
import tempfile

class SilvrTestCase(unittest.TestCase):

    def setUp(self):
        # Create and register a temporary database for use with our test instance of Silvr
        self.database_file_descriptor, silvr.app.config['DATABASE'] = tempfile.mkstemp()
        # Set the app to be in TESTING mode, preventing catching of errors so we get better data on them
        silvr.app.config['TESTING'] = True
        # Create and give ourselves a test_client
        self.app = silvr.app.test_client()
        # Now, init the database. This is safe because the DATABASE config key is now pointing to a temporary DB
        silvr.init_db()

    def tearDown(self):
        # Close and unlink the database
        os.close(self.database_file_descriptor)
        os.unlink(silvr.app.config['DATABASE'])

    def login(self, username, password):
        return self.app.post('/login', data=dict(
         username=username,
         password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_login_logout(self):
        """
        Get the username and password values from the config file and try logging in with them and variants
        :return:
        """
        # Get the username and password from the database. This means that the tests will pass, even in production.
        username = silvr.app.config['USERNAME']
        password = silvr.app.config['PASSWORD']
        # Now, try logging in.
        rv = self.login(username, password)
        assert 'You are now logged in.' in str(rv.data)
        # Now log out.
        rv = self.logout()
        assert 'You were logged out.' in str(rv.data)
        # Now, let's try logging in with some invalid creds.
        rv1 = self.login(username + 'x', password)
        assert 'You are now logged in.' not in str(rv1.data)
        self.logout()
        rv2 = self.login(username, password + 'x')
        assert 'You are now logged in.' not in str(rv2.data)
        self.logout()
        rv3 = self.login(username + 'x', password + 'x')
        assert 'You are now logged in.' not in str(rv3.data)

    def test_database_begins_empty(self):
        """
        Make sure that the database begins with nothing in it.
        :return:
        """
        # Grab
        rv = self.app.get('/')
        assert "No posts so far." in str(rv.data)


    def test_entries_add(self):
        """
        Make sure that the /add endpoint actually adds an entry based on its POST values
        :return:
        """





if __name__ == "__main__":
    unittest.main()