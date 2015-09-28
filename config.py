# Configuration for silvr blog

DATABASE = '/home/sws/projects/silvr/silvr.db' # CHANGE this to point to your database.
SCHEMA = 'schema.sql'
DEBUG = True  # Are we in debug mode?
SECRET_KEY = 'dev key'
USERNAME = 'admin'
PASSWORD = 'default'  # TODO: Make this not awful

TITLE = 'Silvr'
COPYRIGHT = 'Copyright (C) Leo Tindall 2015'

LATEST_FIRST = True  # If True, display the latest posts first; if False, displays in chronological order
NAVBAR_ADDL = [('http://silverwingedseraph.net', 'Main Site')]  # List of tuples of (URI, display name) to be added to the navbar