# all the imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from contextlib import closing  # For init.ing database

app = Flask(__name__)
app.config.from_object('config')  # Import configuration data


def make_dicts(cursor, row):
    """
    Make dicts from rows selected in database.
    :param cursor:
    :param row:
    :return: Dict
    """
    return dict((cursor.description[idx][0], value) for idx, value in enumerate(row))


def init_db():
    with closing(connect_db()) as database:  # Closes the connection once the following work is done
        with app.open_resource(app.config['SCHEMA'], mode='r') as schema:  # Open the app schema for reading
            # Reads in SQL script and executes it in the database
            database.cursor().executescript(schema.read())
        # Commit the database now that the script is done
        database.commit()


def connect_db():
    database = sqlite3.connect(app.config['DATABASE'])
    database.row_factory = make_dicts  # Set the default row factory
    return database


def get_db():
    database = getattr(g, 'db', None)
    if database is not None:
        return database
    else:
        connect_db()  # We're not connected, so connect and then recurse.
        return get_db()


def query_db(query, args=(), one=False):
    """
    Query the database and return the results
    :param query: The query to execute.
    :param args: Query args, sent to the database
    :param one: Return only one result (default: False)
    :return: dict of args
    """
    current = get_db().execute(query, args)
    rv = current.fetchall()
    current.close()
    if one:
        return rv[0] if rv else None
    else:
        return rv


def commit_db():
    """
    Commit the database.
    :return: None
    """
    get_db().commit()


@app.before_request
def before_request():
    """
    Connects to the database for the request.
    """
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    """
    Disconnect from the database.
    :param exception:
    :return:
    """
    database = getattr(g, 'db', None)
    if database is not None:
            database.close()


@app.route('/')
def show_entries():
    """
    Display all stored entries.
    :return: Rendered template.
    """
    entries = query_db("select title, text from entries")
    if entries is not None:
        return render_template('show_entries', entries=entries)
    else:
        return "No entries in database."


@app.route('/add', methods=['POST'])
def add_entry():
    """
    Add an entry to the list of entries.
    """
    if not session.get('logged_in'):
        abort(401) # Unauthorized
    query_db('insert into entries (title, text) values (?, ?)', [request.form['title'],\
                                                                 request.form['text']])
    commit_db()
    flash('New entry was successfully posted!')
    return redirect(url_for('show_entries'))  # Redirect the user to see some requests


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Log the user in, of xir credentials are correct
    :return:
    """
    error = None
    if request.method == 'POST':
        # TODO: Make this not leak info
        # TODO: Use hashed passwords
        if request.form['username'] != app.config['USERNAME']:
            error = "Invalid Username"
        if request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid Password'
        else:
            # At this point, we're successfully validated.
            session['logged_in'] = True
            flash('You are now logged in.')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    """
    Log the user out
    :return:
    """
    session.pop('logged_in', None)
    flash('You were logged out.')
    return redirect(url_for('show_entries'))

if __name__ == '__main__':
    app.run()
