"Word Fit Routing Hub"

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, Transcript, Word, User, UserWord

from ted_api import query_talk_info, get_video, get_webpage_transcript, get_vocab_transcript
from dictionary_api import get_dictionary_info
from nytimes_api import get_nytimes_snippet_url, get_sentence_from_snippet 

from vocab_parsing import get_vocab
from lemma import LEMMA_DICT
from random import shuffle


app = Flask(__name__)
app.secret_key = "secret"

app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    if session.get('user_id', None):
        user_id = session['user_id']
        user = User.query.get(user_id)
        words = user.words
        return render_template("homepage.html", 
                                words=words)
    else: 
        return render_template('homepage.html')

@app.route('/login', methods=['POST'])
def login():
    """Login page."""
    email = request.form.get('email')
    password = request.form.get('password')
    user = User.query.filter_by(email=email, password=password).first()

    if user:
        user_id = user.user_id
        fname = user.fname
        session['user_id']=user_id
        flash("Hey %s! It's good to have you back."%fname)#flashes whatever is the next page; base html needs work
        words = user.words
        return  render_template('homepage.html',
                                words=words)
    else:
        flash('Oops! Login not successful!')
        return redirect("/")

@app.route('/logout')
def logout():
    del session['user_id']
    return redirect('/') 

@app.route('/create_account')
def create_account():
    return render_template('create_account.html')

@app.route('/account_feedback', methods=['POST'])
def account_feedback():
    email = request.form.get('email')
    password = request.form.get('password')
    fname = request.form.get('fname')
    lname = request.form.get('lname')

    user = User.query.filter_by(email=email).first()
    if user:
        flash("Hi, %s, you already have an account"%fname)
        return redirect("/")
    else:
        User.add_user(  email=email, 
                        password=password,
                        fname=fname,
                        lname=lname)
        flash("Congrats %s! You've successfully created an account!\nYou can now log in."%fname)
        return redirect("/")


@app.route('/query', methods=['GET'])
def return_talk_info():
    """Takes in user key word and display search results.

    Search results include talk id, name(speaker: title), date, and slug and
    come in the form of a list of tuple pairs with each pair in the 
    following format:[(talk_id, [name, date, slug])]."""
    
    key_word = request.args.get('key_word')
    print "1. I'm going to start querying the word."

    query_results = query_talk_info(key_word)
    print "4. I queried the key word you entered: '%s', and I'm ready to render template"%(key_word)
    return render_template("query_results.html", 
                            query_results=query_results,
                            key_word=key_word)

@app.route('/selection', methods=['GET'])
def display_selection():
    """Stores and displays embedded video, transcript, and vocabulary of selected talk."""
    
    key_word = request.args.get('key_word')
    slug = request.args.get('slug')
    talk_id = request.args.get('talk_id')
    print "5. I got to the selection route with the passed in arguments."

    video= get_video(slug) #a link to embed
    print "6. I got the video."
    
    #check to see if transcript is stored
    stored_transcript = Transcript.query.get(talk_id)
    print "7.Check to see if the transcript is already there."
    
    #vocab_transcript: a string--used for parsing vocabulary
    #webpage_transcript: a dict --used display text in paragraph format
    if stored_transcript:
        print "8. Already stored."
        # vocab_transcript = stored_transcript.transcript
        # print "9. Get vocab transcript."
        webpage_transcript = get_webpage_transcript(slug)
        print "10. Get webpage_transcript"
        vocab_list = Word.query.filter_by(talk_id=talk_id).all()
        print "11. Get the 10 vocab that's already stored."
        
    else:
        vocab_transcript = get_vocab_transcript(slug) #a string that get's stored
        print "8. Not stored. Got transcript for vocab"
        Transcript.add_transcript(talk_id, slug, vocab_transcript)
        print '9. Added transcript to db' 
        webpage_transcript = get_webpage_transcript(slug) # a dict of transcript paragraphs     
        print "10. Got webpage_transcript."
        print "BEWARE: GONNA BE SLOW. UNAVOIDABLE: NEED TO PARSE TRANSCRIPT TO SENTENCES."


        vocab_list = []
        for vocab, attributes in get_vocab(vocab_transcript):
            print "11. Selecting the top 10 vocab and getting their attributes."
        #get_vocab()returns a list of tuple pairs: (vocab, (attributes))
        #need make sure each vocabulary is stored first
            stored_word = Word.query.filter_by(word = vocab, talk_id = talk_id).first()
                    
            if stored_word:
                print "12. Vocab is stored! Just get everything!"
                vocab_list.append(stored_word)
            else:
                print "12. Vocab is not stored. Let's get all the values and add each vocab to db. "
                vocab = vocab
                stem = attributes[0]
                freq = attributes[1]
                sentence = attributes[2]
                selection = attributes[3]
                print "13. Got all the pre-stored info from the vocab tuple"
                #using dictionary api
                dictionary_info = get_dictionary_info(vocab)
                
                parts_of_speech = dictionary_info[0] 
                print "14. Got dictinary info on parts of speech"
                pronunciation = dictionary_info[1]
                print "15. Got dictinary info on pronunciation"
                definition = dictionary_info[2]
                print "16. Got dictinary info on definition"

                snippet_url = get_nytimes_snippet_url(vocab)
                snippet = snippet_url[0]
                print "17. Got snippet from nytimes"
                print "BEWARE: GONNA BE SLOW. UNAVOIDABLE: NEED TO PARSE EACH SNIPPET TO SENTENCES."
                other_usage = get_sentence_from_snippet(vocab, snippet)
                print "18. Got the specific sentence in ny times"
                other_usage_link = snippet_url[1]
                print "19. Got url from nytimes"

                word = Word.add_word(   word=vocab, 
                                        talk_id=talk_id, 
                                        stem=stem, 
                                        freq=freq, 
                                        sentence=unicode(sentence, 'utf-8'), 
                                        selection=selection,
                                        parts_of_speech=parts_of_speech,
                                        pronunciation=pronunciation,
                                        definition=definition,
                                        other_usage=unicode(other_usage, 'utf-8'),
                                        other_usage_link=other_usage_link
                                        )
                                        #not passing in other_usage_url yet
                vocab_list.append(word)
                print "20. Added the word in db and appended it to vocab list."
    #definitions is a string, will need to be parsed and indexed
    #definitin_sets structure is {word:[:def1, :def2], word:[def1, def2]}
    #maybe can be a static method of Words
    definition_sets = {}
    for word in vocab_list:
        definition_sets[word.word.encode('utf=8')]= word.split_definition()
    print "21. Got definition parsed"

    #parts_of_speech is a string, will need to be parsed and indexed
    #structure is [verb, noun]
    #maybe can be a static method of Words
    parts_of_speech_sets = {}
    for word in vocab_list:
        parts_string = word.parts_of_speech
        parts = [item.encode('utf-8')for item in parts_string.split("-")]
        parts_of_speech_sets[word.word.encode('utf-8')]= parts
    print "22. Got parts of speech parsed. Ready to render template."


    return render_template("display_selection.html",
                            video = video,
                            webpage_transcript = webpage_transcript,
                            vocab_list = vocab_list,
                            definition_sets=definition_sets,
                            parts_of_speech_sets=parts_of_speech_sets,
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

@app.route('/no_pronunciation')
def provide_no_pronunciation_feedback():
    return render_template("no_pronunciation.html")



@app.route('/store_vocab', methods=['POST'])
def store_vocab():
    word_id = request.form.get('word_id')
    user_id = session['user_id']
    word = db.session.query(Word.word).filter_by(word_id=word_id).one()

    if UserWord.query.filter_by(word_id=word_id, user_id=user_id).first():
        return "This word has already been added."
    else:
        UserWord.add_user_word( word_id = word_id,
                                 user_id = user_id)
        return "Awesome! You just stored another new word: %s."%word



@app.route('/remove_vocab', methods=['POST'])
def remove_vocab():
    word_id = request.form.get('word_id')
    user_id = session['user_id']
    word = db.session.query(Word.word).filter_by(word_id=word_id).one()
    
    #can put this in model to make it prettier
    UserWord.query.filter_by(word_id = word_id, user_id = user_id).delete()
    db.session.commit()
    
    return "You have officially mastered '%s' and it is now removed from your list."%word

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
