"Word Fit Routing Hub"

from jinja2 import StrictUndefined
from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, Transcript, Word, User
from ted_api import query_talk_info, get_video, get_transcript
from vocab_parsing import get_vocab
from lemma import LEMMA_DICT


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
	
	vocab_list = []
	for vocab, attributes in get_vocab(transcript): 
	#get_vocab()returns a list of tuple pairs: (vocab, (attributes))
		vocab = vocab
		stem = attributes[0]
		freq = attributes[1]
		sentence = attributes[2]
		selection = attributes[3]

		word = Word.add_word(word=vocab, talk_id=talk_id, stem=stem, 
					freq=freq, sentence=unicode(sentence, 'utf-8'), selection=selection)
					#not passing in pronunciation, meaning, and other_usage yet

		vocab_list.append(word)

	return render_template("display_selection.html",
							video=video,
							transcript=transcript,
							vocab_list = vocab_list)



@app.route('/vocab_exercise', methods=['POST'])
def display_vocab_exercise():

	word1= request.form.get("word1")
	word2= request.form.get("word2")
	word3= request.form.get("word3")
	word4= request.form.get("word4")
	word5= request.form.get("word5")
	word6= request.form.get("word6")
	word7= request.form.get("word7")
	word8= request.form.get("word8")
	word9= request.form.get("word9")
	word10= request.form.get("word10")
	#instead of getting the word, get the word id
	#Use Word.query.get(id) to get each word object
	#Make a method that splits the word.talk_sentence into two as a tuple based on the word
	#Make an input type text between the two parts of the sentence
	#Make users submit the form in the end.
	#Create a new page with a server that checks users answers

	return render_template("vocab_exercise.html",
							word1= word1,
							word2= word2,
							word3= word3,
							word4= word4,
							word5= word5,
							word6= word6,
							word7= word7,
							word8= word8,
							word9= word9,
							word10= word10,)



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
