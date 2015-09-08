"Word Fit Routing Hub"

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension

import json
import os

from model import connect_to_db, db, Transcript, Word, User, UserWord

from external_api.ted_api import query_talk_info, get_image_blurb, get_video, get_webpage_transcript, get_vocab_transcript
from external_api.dictionary_api import get_dictionary_info
from external_api.nytimes_api import get_nytimes_snippet_url, get_sentence_from_snippet 

from vocab_resources.vocab_parsing import VocabFactory
from random import shuffle, choice

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage"""

    if session.get('user_id'):
        user_id = session['user_id']
        user = User.query.get(user_id)
        words = user.words
        flash("Hey %s! It's good to have you back."%user.name)

        return render_template("homepage.html",
                                words=words)
    else:
        return render_template('homepage.html')


@app.route('/login', methods=['POST'])
def login():
    """Log in page"""

    name = request.form.get('name')
    email = request.form.get('email')
    image = request.form.get('image')

    user = User.query.filter_by(email=email).first()

    if user:
        user_id = user.user_id
        session['user_id']=user_id
        session['name']=name
        session['image']=image
       
        return "%s is in session" %(name)

    if not user:
        User.add_user(email=email, name=name, image=image)
        session['user_id']=user_id
        session['name']=name
        session['image']=image
       
        return "%s is in session" %(name)

    else:
        return None


@app.route('/logout')
def logout():
    """Log out: Deletes user from session"""

    if session.get('user_id'):
        del session['user_id']
        del session['name']
        del session['image']
    
    return redirect('/') 


@app.route('/get_pie_info', methods=['POST'])
def get_pie_info():
    """Provide pie info based on user's selected vocab"""
    
    if session.get('user_id'):
        user_id = session['user_id']
        user = User.query.get(user_id)
        words = user.words

    talks = {}
    for word in user.words:
        talk_id = word.talk_id
        transcript = Transcript.query.get(talk_id)
        slug = transcript.slug
        title = transcript.title

        talks.setdefault((talk_id, title, slug), []).append(word.word)
    
    talks_vocab = talks.items()
    return json.dumps(talks_vocab)


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


@app.route('/get_images')
def get_images():
    """Loads ted talk images"""

    talk_id = request.args.get('talk_id')
    image, blurb = get_image_blurb(talk_id)

    return jsonify({'image':image, 'blurb':blurb})


@app.route('/selection', methods=['GET'])
def display_selection():
    """Stores and displays embedded video, transcript, and vocabulary of selected talk."""
    
    key_word = request.args.get('key_word')
    title = request.args.get('title')
    slug = request.args.get('slug')
    talk_id = request.args.get('talk_id')

    video= get_video(slug) 
    stored_transcript = Transcript.query.get(talk_id)
    
    #vocab_transcript:   a string --used for parsing vocabulary
    #webpage_transcript: a dict   --used display text in paragraph format
    if stored_transcript:
        webpage_transcript = get_webpage_transcript(slug)
        vocab_list = Word.query.filter_by(talk_id=talk_id).all()
    else:
        vocab_transcript = get_vocab_transcript(slug) #a string that get's stored for parsing
        Transcript.add_transcript(talk_id, slug, vocab_transcript, title)
        webpage_transcript = get_webpage_transcript(slug) # a dict of transcript paragraphs     
    
        vocab_list = []

        my_text = VocabFactory(vocab_transcript)
        my_text.get_vocab()#get_vocab()returns a list of tuple pairs: [(vocab, (attributes))]

        for vocab, attributes in my_text.vocab_list:
        
        #make sure each vocabulary is stored first
            stored_word = Word.query.filter_by(word = vocab, talk_id = talk_id).first()
                    
            if stored_word:
                vocab_list.append(stored_word)
            else:
                vocab = vocab
                stem = attributes[0]
                freq = attributes[1]
                sentence = attributes[2]
                selection = attributes[3]

                word = Word.add_word(word=vocab, 
                                    talk_id=talk_id, 
                                    stem=stem, 
                                    freq=freq, 
                                    sentence=unicode(sentence, 'utf-8'), 
                                    selection=selection)                        
                vocab_list.append(word)

    return render_template("display_selection.html",
                            video = video,
                            webpage_transcript = webpage_transcript,
                            vocab_list = vocab_list,
                            key_word = key_word,
                            slug = slug,
                            talk_id = talk_id,
                            title = title)


@app.route('/fetch_api_info', methods=['POST'])
def fetch_api_info():
    """Retrieves each vocab's external api info via ajax"""

    toggle_word_id = request.form.get('toggle_word_id')
    word_id = toggle_word_id.split("-")[1]
    word = Word.query.get(word_id)

    if word.other_usage == "":
        vocab = word.word

        #using dictionary api
        dictionary_info = get_dictionary_info(vocab)
        parts_of_speech = dictionary_info[0] 
        pronunciation = dictionary_info[1]
        definition = dictionary_info[2]

        #using nytimes api
        snippet_url = get_nytimes_snippet_url(vocab)
        snippet = snippet_url[0]
        other_usage = get_sentence_from_snippet(vocab, snippet)
        other_usage_link = snippet_url[1]

        word.update_api_records(parts_of_speech=parts_of_speech,
                                pronunciation=pronunciation,
                                definition=definition,
                                other_usage=unicode(other_usage, 'utf-8'),
                                other_usage_link=other_usage_link)
    else:
       
        parts_of_speech = word.parts_of_speech
        pronunciation = word.pronunciation
        definition = word.definition
        other_usage = word.other_usage
        other_usage_link = word.other_usage_link

    #definitions is a string, will need to be parsed and indexed
    defs = definition.split(":")
    
    #parts_of_speech is a string, will need to be parsed and indexed
    parts = [item.encode('utf-8')for item in parts_of_speech.split("-")]
    
    return jsonify({'parts_of_speech': parts,
                    'pronunciation': pronunciation,
                    'definition': defs[1:],#first element is an empty string
                    'other_usage':other_usage, 
                    'other_usage_link': other_usage_link})


@app.route('/vocab_exercise', methods=['POST'])
def display_vocab_exercise():
    """
    Generates fill-in-the-blank vocab exercises.

    Uses the word_id to retrieve each word object.
    Invoke Word method, create_exercise_prompt, on each word object.
    Passes each word object and their exercise prompt as a list of tuples to th front-end. """

    key_word = request.form.get('key_word')
    talk_id = request.form.get('talk_id')
    slug  = request.form.get('slug')
    title = request.form.get('title')

    vocab_list = [] #retrieves the 10 select vocabulary
    for i in range(1, 11):
        word_name = "word%d"%i
        # word = Word.query.get(request.form.get(word_name))

        get_word_id = request.form.get(word_name)
        if get_word_id:
            word = Word.query.get(get_word_id)
            vocab_list.append(word)
        else:
            continue

    #filter out words that come from the same sentence
    sentence_repeated = {} #sentence as keys and word_ids as a list of values
    for word in vocab_list:
        sentence_repeated.setdefault(word.sentence, []).append(word.word_id)
    
    #remove words that have the sentence to test 
    for sentence, word_id_list in sentence_repeated.items():
        chosen_word = choice(word_id_list)
        sentence_repeated[sentence] = chosen_word
    
    words_to_test = sentence_repeated.values()

    for word in vocab_list:   
        if word.word_id not in words_to_test:
            vocab_list.remove(word)

    vocab_exercise_list = []
    for word in vocab_list:
        word_exercise = word.create_exercise_prompt()
        vocab_exercise_list.append((word, word_exercise))

    shuffle(vocab_exercise_list) #ensure that the sequence of vocab exericse is random
    
    return render_template("vocab_exercise.html",
                            vocab_exercise_list = vocab_exercise_list,
                            vocab_list = vocab_list,
                            key_word = key_word,
                            talk_id = talk_id,
                            title = title,
                            slug = slug)


@app.route('/exercise_submission', methods=['POST'])
def evaluate_answers():
    """Retrieve user's answers and the key and send to evaluation page.
    
    The evaluation page compares the answers with the keys and offer 
    a summary of performance.
    """
    #gets each word object, the user ans, the key, and assign 
    i = 1
    vocab_list = []
    answers = []
    keys = []
    ids = []
    
    while True:
        word_name = "word%d"%i #word object
        ans_name = "ans%d"%i   #answer from user
        key_name = "key%d"%i   #key 
        id_name = "Q%d"%i      #an id list to keep trackfor front end
        
        if request.form.get(word_name):
            word = Word.query.get(request.form.get(word_name))
            vocab_list.append(word)

            ans = request.form.get(ans_name)
            answers.append(ans)

            key = request.form.get(key_name)
            keys.append(key)

            ids.append(id_name)

            i += 1
        else:
            break

    ans_key = zip(answers, keys) #creates a list of tuples (ans, key)

    score = 0 # calculate_score
    for ans, key in ans_key:
        if ans == key:
            score += 1

    id_ans_key = dict(zip(ids, ans_key)) #creates a dictionary { id:(ans, key) }

    key_word = request.form.get('key_word')
    talk_id = request.form.get('talk_id')
    slug  = request.form.get('slug')
    title = request.form.get('title')

    return render_template("evaluate_answers.html",
                            id_ans_key = id_ans_key,
                            score = score,
                            vocab_list = vocab_list,
                            key_word = key_word,
                            talk_id = talk_id,
                            title = title,
                            slug = slug )


@app.route('/store_vocab', methods=['POST'])
def store_vocab():
    """Using ajax call to store vocab in user's personal list"""

    word_id = request.form.get('word_id')
    user_id = session['user_id']
    word = db.session.query(Word.word).filter_by(word_id=word_id).one()

    if UserWord.query.filter_by(word_id=word_id, user_id=user_id).first():
        return "Returned from server: vocab already added"
    else:
        UserWord.add_user_word( word_id = word_id,
                                 user_id = user_id)
        return "Returned from server: vocab just added"


@app.route('/remove_vocab', methods=['POST'])
def remove_vocab():
    """Using ajax call to remove vocab in user's personal list"""
    
    word_id = request.form.get('word_id')
    user_id = session['user_id']
    word = db.session.query(Word.word).filter_by(word_id=word_id).one()
    
    #can put this in model to make it prettier
    UserWord.query.filter_by(word_id = word_id, user_id = user_id).delete()
    db.session.commit()
    return "Returned from server: removed vocab"


if __name__ == "__main__":
    connect_to_db(app)
    db.create_all()
    #create database here (safest way)
    
    PORT = int(os.environ.get("PORT", 5000))

    DebugToolbarExtension(app) # Use the DebugToolbar
    DEBUG = "NO_DEBUG" not in os.environ
    #change it back later

    app.run(debug=DEBUG, host="0.0.0.0", port=PORT)










