# all the imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from contextlib import closing  # For init.ing database
import time

app = Flask(__name__.split('.')[0])
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
    try:
        current = get_db().execute(query, args)
    except sqlite3.OperationalError:
        return None
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

@app.context_processor
def inject_config():
    """
    Inject the configuration
    """
    navbar = app.config['NAVBAR_ADDL']
    title = app.config['TITLE']
    copyright = app.config['COPYRIGHT']
    return dict(navbar=navbar, title=title, copyright=copyright)


@app.route('/')
def show_entries():
    """
    Display all stored entries.
    :return: Rendered template.
    """
    entries = query_db('select id, title, text, posted, category from entries')
    if app.config['LATEST_FIRST']:
        # Reverse the entries list so that the latest entries are first
        entries = list(reversed(entries))  # Reversed returns an iterable so we need to make it a list
    if entries is not None:
        return render_template('show_entries.html', entries=entries)
    else:
        return render_template('show_entries.html')


@app.route('/add', methods=['POST'])
def add_entry():
    """
    Add an entry to the list of entries.
    """
    if not session.get('logged_in'):
        abort(401)  # Unauthorized
    query_db('insert into entries (title, text, posted, category) values (?, ?, ?, ?)', [request.form['title'],
                                                                         request.form['text'],
                                                                         str(time.strftime(app.config['DATETIME'])),
                                                                         request.form['category']])
    commit_db()
    flash('New entry was successfully posted!')
    return redirect(url_for('show_entries'))  # Redirect the user to see some requests

@app.route('/add_category', methods=['POST'])
def add_category():
    """
    Add an entry to the list of entries.
    """
    if not session.get('logged_in'):
        abort(401)  # Unauthorized
    query_db('insert into categories (category, description) values (?, ?)', [request.form['name'],
                                                                         request.form['text']])
    commit_db()
    flash('New category was successfully added!')
    return redirect(url_for('new_post'))  # Redirect the user to see some requests


@app.route('/del/<int:entry_id>')
def del_entry(entry_id):
    """
    Remove a post, if logged in.
    :param entry_id: The ID of the post to remove.
    :return:
    """
    if not session.get('logged_in'):
        abort(401)  # Unauthorized
    else:
        # Person is logged in
        query_db('delete from entries where id == ?', [entry_id])
        commit_db()
        flash("Deletion successful!")
    return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Log the user in, if xir credentials are correct
    :return:
    """
    error = None
    if request.method == 'POST':
        # TODO: Make this not leak info
        # TODO: Use hashed passwords
        if request.form['username'] != app.config['USERNAME']:
            error = "Invalid Credentials"
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid Credentials'
        else:
            # At this point, we're successfully validated.
            session['logged_in'] = True
            flash('You are now logged in.')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route("/new_post")
def new_post():
    """
    The form for submitting new posts.
    :return:
    """
    categories = query_db("select category from categories")
    if session.get('logged_in'):
        return render_template("new_post.html", categories=categories)
    else:
        abort(401) # Unauthorized

@app.route("/new_category")
def new_category():
    """
    The form for submitting new categories.
    :return:
    """
    if session.get('logged_in'):
        return render_template("new_category.html")
    else:
        abort(401) # Unauthorized


@app.route('/view_category/<category>')
def view_category(category):
    """
    List the entries in a category
    :param category: The category to list
    :return:
    """
    entries = query_db("select id, title, text, posted, category from entries WHERE category == (?)", [category])
    if app.config['LATEST_FIRST_IN_CATEGORIES']:
        # Reverse the entries list so that the latest entries are first
        entries = list(reversed(entries))  # Reversed returns an iterable so we need to make it a list
    if entries is not None:
        return render_template('show_entries.html', entries=entries)
    else:
        return render_template('show_entries.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    """
    Log the user out
    :return:
    """
    session.pop('logged_in', None)
    flash('You were logged out.')
    return redirect(url_for('show_entries'))

@app.route('/favicon.ico')
def favicon_redirect():
    """
    Redirect the user to the correct favicon.ico
    :return:
    """
    return redirect(url_for('static', filename='favicon.ico'))

if __name__ == '__main__':
    app.run()


