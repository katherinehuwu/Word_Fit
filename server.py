"Word Fit Routing Hub"

from jinja2 import StrictUndefined
from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, Transcript, Word, User
from ted_api import query_talk_info, get_video, get_transcript, get_vocab

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
	talk_id = request.args.get('talk_id')
	video= get_video(slug) #a link to embed
	
	#check to see if transcript is stored
	stored_transcript = Transcript.query.get(talk_id)
	if stored_transcript:
		transcript = stored_transcript.transcript
	else:
		transcript = get_transcript(slug) #a string of transcript
		Transcript.add_transcript(talk_id, slug, transcript)
		
	vocab_list = get_vocab(transcript)
	
	# need academic word list, a dictionary to count the frequency
	# #store vocab in db

	return render_template("display_selection.html",
							video=video,
							transcript=transcript,
							vocab_list = vocab_list)

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
