"Word Fit Routing Hub"

from jinja import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, Transcript, Word, User, UserWord

app = Flask(__name__)
app.secret_key = "secret"