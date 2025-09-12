import sqlite3
from flask import Flask, render_template_string, request, redirect, url_for, g

app = Flask(__name__)
DATABASE = 'academia.db'

