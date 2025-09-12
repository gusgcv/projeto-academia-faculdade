import sqlite3
from flask import Flask, render_template_string, request, redirect, url_for, g
 
# Flask # 
app = Flask(__name__)
DATABASE = 'academia.db'

#Base banco de dados em SQlite#
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g. _database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app .teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():