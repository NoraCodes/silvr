# all the imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from contextlib import closing # For init.ing database

app = Flask(__name__)
app.config.from_object('config') # Import configuration data

def init_db():
    with closing(connect_db()) as database: # Closes the connection once the following work is done
        with app.open_resource(app.config['SCHEMA'], mode='r') as schema: # Open the app schema for reading
            # Reads in SQL script and executes it in the database
            database.cursor().executescript(schema.read())
        # Commit the database now that the script is done
        database.commit()

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
