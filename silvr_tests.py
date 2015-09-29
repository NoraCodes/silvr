# Unit Testing for Silvr Blog
import os
import silvr
import unittest
import tempfile
import time

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
        # Now look up and remember out creds
        self.username = silvr.app.config['USERNAME']
        self.password = silvr.app.config['PASSWORD']

    def tearDown(self):
        # Close and unlink the database
        os.close(self.database_file_descriptor)
        os.unlink(silvr.app.config['DATABASE'])

    def login(self, username, password):
        return self.app.post('/login', data=dict(
         username=username,
         password=password
        ), follow_redirects=True)

    def new_entry(self, title, text, category=None):
        """
        Make a POST request to create a new entry
        :param title: The title for the post.
        :param text: The text for the body of the post.
        :param category: The category into which we want to add the post.
        :return: The time that the POST request was sent.
        """
        self.app.post('/add', data=dict(
            title=title,
            text=text,
            category=category
        ), follow_redirects = True)
        return str(time.strftime(silvr.app.config['DATETIME']))

    def new_category(self, name, text):
        """
        Make a POST request to create a new category
        :param name: The name for the category
        :param text: The text for the description of the category
        :return: None
        """
        self.app.post('/add_category', data=dict(
            name=name,
            text=text,
        ), follow_redirects = True)
        return str(time.strftime(silvr.app.config['DATETIME']))

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_login_logout(self):
        """
        Get the username and password values from the config file and try logging in with them and variants
        :return:
        """
        username = self.username
        password = self.password
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

    def test_categories_add_requires_login(self):
        """
        Make sure adding a new category doesn't work if not logged in
        :return:
        """
        self.new_category('Category2', 'Description')
        rv = self.app.get("/new_post")
        assert '<option value="Category">Category</option>' not in str(rv.data)

    def test_categories_add(self):
        """
        Make sure adding a new category works and actually adds it to the database
        :return:
        """
        self.login(self.username, self.password)
        self.new_category('Category', 'Description')
        rv = self.app.get("/new_post")
        assert '<option value="Category">Category</option>' in str(rv.data)
        self.logout()

    def test_entries_add_requires_login(self):
        """
        Make sure that the /add endpoint does NOT add posts when the user is not logged in
        :return:
        """
        datetime = self.new_entry('<Title2>', '<i>Text</i>', category='Category')
        rv = self.app.get("/")
        assert "<h2>&lt;Title&gt;</h2>" not in str(rv.data)

    def test_entries_add(self):
        """
        Make sure that the /add endpoint actually adds an entry based on its POST values
        :return:
        """
        self.login(self.username, self.password)
        datetime = self.new_entry('<Title>', '<i>Text</i>', category='Category')
        rv = self.app.get("/")
        assert "<h2>&lt;Title&gt;</h2>" in str(rv.data) # Angle brackets replaced!
        assert "<i>Text</i>" in str(rv.data) # Angle brackets NOT replaced. HTML is allowed in posts.
        assert datetime in str(rv.data) # The post should be made with the right date
        self.logout()

    def test_entries_delete_requires_login(self):
        """
        Ensure that deleting a post requires login
        :return:
        """
        silvr.init_db()  # Clear the database

        # Login and make a new post
        self.login(self.username, self.password)
        self.new_entry('DeleteMe', 'Text', category='Category')
        # Now logout BEFORE deletion
        self.logout()
        rv = self.app.get('/del/1')
        assert "Unauthorized" in str(rv.data) # We were rejected when trying to delete the post
        rv = self.app.get('/')
        assert "DeleteMe" in str(rv.data) # The post is still there

    def test_entries_delete(self):
        """
        Ensure that deleting a post deletes the post
        :return:
        """
        silvr.init_db()  # Clear the database

        # Login and make a new post
        self.login(self.username, self.password)
        self.new_entry('DeleteMe', 'Text', category='Category')
        # Try to delete the post
        rv = self.app.get('/del/1')
        # Now logout AFTER deletion
        self.logout()
        rv = self.app.get('/')
        assert "DeleteMe" not in str(rv.data) # The post isn't still there





if __name__ == "__main__":
    unittest.main()