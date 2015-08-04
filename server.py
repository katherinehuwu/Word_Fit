"Word Fit Routing Hub"

from jinja2 import StrictUndefined
from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, Transcript, Word, User, UserWord
from ted_api import query_talk_info, get_video, get_transcript

app = Flask(__name__)
app.secret_key = "secret"

app.jinja_env.undefined = StrictUndefined

@app.route('/')
def index():
	"""Homepage."""

	return render_template("homepage.html")

@app.route('/query', methods=['POST'])
def return_talk_info():
	"""Takes in user key word and display search results.

	Search results include talk id, name(speaker: title), date, and slug and
	come in the form of a list of tuple pairs: first element is the talk id,
	the rest of the info are in a list according to the given order."""
	
	key_word = request.form.get('key_word')
	query_results = query_talk_info(key_word)
	
	return render_template("query_results.html", 
							query_results=query_results)

@app.route('/selection')
def display_selection():
	"""Stores and displays embedded video, transcript, and vocabulary of selected talk."""
	slug = request.args.get('slug')
	video= get_video(slug) #a link to embed
	transcript = get_transcript(slug) #a string of transcript
	# #store transcript db
	# vocab = get_vocab(transcript)
	# #store vocab in db

	return render_template("display_selection.html",
							video=video,
							transcript=transcript)

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
