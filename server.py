"Word Fit Routing Hub"

from jinja2 import StrictUndefined
from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, Transcript, Word, User
from ted_api import query_talk_info, get_video, get_webpage_transcript, get_vocab_transcript
from dictionary_api import get_dictionary_info
from vocab_parsing import get_vocab
from lemma import LEMMA_DICT
from random import shuffle


app = Flask(__name__)
app.secret_key = "secret"

app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
	"""Homepage."""

	return render_template("homepage.html")

@app.route('/query', methods=['GET'])
def return_talk_info():
	"""Takes in user key word and display search results.

	Search results include talk id, name(speaker: title), date, and slug and
	come in the form of a list of tuple pairs with each pair in the 
	following format:[(talk_id, [name, date, slug])]."""
	
	key_word = request.args.get('key_word')
	query_results = query_talk_info(key_word)
	
	return render_template("query_results.html", 
							query_results=query_results,
							key_word=key_word)

@app.route('/selection', methods=['GET'])
def display_selection():
	"""Stores and displays embedded video, transcript, and vocabulary of selected talk."""
	key_word = request.args.get('key_word')
	slug = request.args.get('slug')
	talk_id = request.args.get('talk_id')

	video= get_video(slug) #a link to embed
	
	#check to see if transcript is stored
	stored_transcript = Transcript.query.get(talk_id)
	
	#vocab_transcript: a string--used for parsing vocabulary
	#webpage_transcript: a dict --used display text in paragraph format
	if stored_transcript:
		vocab_transcript = stored_transcript.transcript
		webpage_transcript = get_webpage_transcript(slug)
	
	else:
		vocab_transcript = get_vocab_transcript(slug) #a string that get's stored
		Transcript.add_transcript(talk_id, slug, vocab_transcript) 
		webpage_transcript = get_webpage_transcript(slug) # a dict of transcript paragraphs		
		

	vocab_list = []
	for vocab, attributes in get_vocab(vocab_transcript): 
	#get_vocab()returns a list of tuple pairs: (vocab, (attributes))
	#need make sure each vocabulary is stored first

		stored_word = Word.query.filter_by(word = vocab, talk_id = talk_id).first()
				
		if stored_word:
			vocab_list.append(stored_word)
		else:
			vocab = vocab
			stem = attributes[0]
			freq = attributes[1]
			sentence = attributes[2]
			selection = attributes[3]
			#using dictionary api
			parts_of_speech = get_dictionary_info(vocab)[0]
			print parts_of_speech 
			pronunciation = get_dictionary_info(vocab)[1]
			print pronunciation
			definition = get_dictionary_info(vocab)[2]
			print definition
			other_usage = " "

			word = Word.add_word(	word=vocab, 
									talk_id=talk_id, 
									stem=stem, 
									freq=freq, 
									sentence=unicode(sentence, 'utf-8'), 
									selection=selection,
									parts_of_speech=parts_of_speech,
									pronunciation=pronunciation,
									definition=definition,
									other_usage=other_usage)
									#not passing in other_usage yet

			vocab_list.append(word)

	return render_template("display_selection.html",
							video = video,
							webpage_transcript = webpage_transcript,
							vocab_list = vocab_list,
							key_word = key_word,
							slug = slug,
							talk_id = talk_id)


@app.route('/vocab_exercise', methods=['POST'])
def display_vocab_exercise():
	"""
	Generates fill-in-the-blank vocab exercises.

	Uses the word_id to retrieve each word object.
	Invoke Word method, create_exercise_prompt, on each word object.
	Passes each word object and their exercise prompt as a list of tuples to th front-end. 
	"""
	key_word = request.form.get('key_word')
	talk_id = request.form.get('talk_id')
	slug  = request.form.get('slug')

	word1 = Word.query.get(request.form.get("word1"))
	word2 = Word.query.get(request.form.get("word2"))
	word3 = Word.query.get(request.form.get("word3"))
	word4 = Word.query.get(request.form.get("word4"))
	word5 = Word.query.get(request.form.get("word5"))
	word6 = Word.query.get(request.form.get("word6"))
	word7 = Word.query.get(request.form.get("word7"))
	word8 = Word.query.get(request.form.get("word8"))
	word9 = Word.query.get(request.form.get("word9"))
	word10 = Word.query.get(request.form.get("word10"))

	vocab_list = [word1, word2, word3, word4, word5, word6, word7, word8, word9, word10]
	
	vocab_exercise_list = []
	for word in vocab_list:
		word_exercise = word.create_exercise_prompt()
		vocab_exercise_list.append((word, word_exercise))

	#ensure that the sequence of vocab exericse is random
	shuffle(vocab_exercise_list)

	return render_template("vocab_exercise.html",
							vocab_exercise_list = vocab_exercise_list,
							vocab_list = vocab_list,
							key_word = key_word,
							talk_id = talk_id,
							slug = slug)

@app.route('/exercise_submission', methods=['POST'])
def evaluate_answers():
	"""Retrieve user's answers and the key and send to evaluation page.
	
	The evaluation page compares the answers and the keys and offer 
	a summary of performance.
	"""
	word1 = Word.query.get(request.form.get("word1"))
	word2 = Word.query.get(request.form.get("word2"))
	word3 = Word.query.get(request.form.get("word3"))
	word4 = Word.query.get(request.form.get("word4"))
	word5 = Word.query.get(request.form.get("word5"))
	word6 = Word.query.get(request.form.get("word6"))
	word7 = Word.query.get(request.form.get("word7"))
	word8 = Word.query.get(request.form.get("word8"))
	word9 = Word.query.get(request.form.get("word9"))
	word10 = Word.query.get(request.form.get("word10"))

	vocab_list = [word1, word2, word3, word4, word5, word6, word7, word8, word9, word10]

	ans1 = request.form.get("ans1")
	ans2 = request.form.get("ans2")
	ans3 = request.form.get("ans3")
	ans4 = request.form.get("ans4")
	ans5 = request.form.get("ans5")
	ans6 = request.form.get("ans6")
	ans7 = request.form.get("ans7")
	ans8 = request.form.get("ans8")
	ans9 = request.form.get("ans9")
	ans10 = request.form.get("ans10")

	answers = (ans1, ans2, ans3, ans4, ans5, ans6, ans7, ans8, ans9, ans10)

	key1 = request.form.get("key1")
	key2 = request.form.get("key2")
	key3 = request.form.get("key3")
	key4 = request.form.get("key4")
	key5 = request.form.get("key5")
	key6 = request.form.get("key6")
	key7 = request.form.get("key7")
	key8 = request.form.get("key8")
	key9 = request.form.get("key9")
	key10 = request.form.get("key10")

	keys = (key1, key2, key3, key4, key5, key6, key7, key8, key9, key10)

	ans_key = zip(answers, keys)
	#creates a list of tuples (ans, key)

	# calculate_score
	score = 0
	for ans, key in ans_key:
		if ans == key:
			score += 1

	ids = ("Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8", "Q9", "Q10") 

	id_ans_key = dict(zip(ids, ans_key))
	#creates a dictionary { id:(ans, key) }

	key_word = request.form.get('key_word')
	talk_id = request.form.get('talk_id')
	slug  = request.form.get('slug')

	return render_template("evaluate_answers.html",
							id_ans_key = id_ans_key,
							score = score,
							vocab_list = vocab_list,
							key_word = key_word,
							talk_id = talk_id,
							slug = slug )


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
