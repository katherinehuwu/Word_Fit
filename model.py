"""Models and databse functions for Wordfit project."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#Model definitions

class Transcript(db.Model): 
	"""Talk info and transcript of each talk that users selected."""

	__tablename__ = 'transcripts'

	talk_id = db.Column(db.Integer, primary_key=True)
	slug = db.Column(db.String(150), nullable=False)
	transcript = db.Column(db.Text, nullable=False)

	def __repr__(self):
		return "<Talk talk_id=%d slug=%s>" %(self.talk_id, self.slug)

	@classmethod
	def add_transcript(cls, talk_id, slug, transcript):
		"""Create and insert a new Transcript object to db based on user selection.

		Retrieves transcript of a specific talk through Ted's API and scrapping.
		Stores transcript object in database.
		"""
		transcript = cls(talk_id=talk_id, slug=slug, transcript=transcript)
		db.session.add(transcript)
		db.session.commit()

class Word(db.Model):
	"""Words selected from each talk."""

	__tablename__ = 'words'

	word_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	word = db.Column(db.String(50), nullable=False)
	talk_id = db.Column(db.Integer, db.ForeignKey('transcripts.talk_id'))
	stem = db.Column(db.String(50), nullable=False)
	freq = db.Column(db.Integer, nullable=False)
	sentence = db.Column(db.Text, nullable=False)
	selection = db.Column(db.String(50), nullable=False)
	parts_of_speech = db.Column(db.String(50), nullable=True)
	meaning =  db.Column(db.Text, nullable=True)
	pronunciation = db.Column(db.String(50), nullable=True)
	other_usage = db.Column(db.Text, nullable=True)

	transcript = db.relationship('Transcript', backref=db.backref('words', order_by=word_id))

	def __repr__(self):
		return "<Word word_id=%d word=%s talk_id=%d>" %(self.word_id, self.word, self.talk_id)


	@classmethod
	def add_word(cls, word, talk_id, stem, 
				freq, sentence, selection):
		"""Create and insert a new Word objects to db. Returns new Word object. 

		New objects are selected by the parsing algorithm in get_vocab() in vocab_parsing.py .
		The selection critera for these words are academic importance, word length, and frequency.
		"""

		word = cls( word=word,
					talk_id=talk_id, 
					stem=stem,
					freq=freq,
					sentence=sentence,
					selection=selection)
		
		db.session.add(word)
		db.session.commit()
		return word

	def create_exercise_prompt(self):
		"""Creates a tuple of the two halves of the sentence and the length of the deleted word.

		This halves will act as the prompt for the fill-in-the-blank vocab exercise.
		The lenght of the deleted word will inform the size attribute in input type text.
		"""
		vocab = self.word
		sentence = self.sentence.split()
		
		for word in sentence:
			if word.lower() == vocab:#accounts for words at the beginning of the sentence too
				splitting_index = sentence.index(word)
				first_half_of_sentence = " ".join(sentence[:splitting_index]) + " "
				second_half_of_sentence = " " + " ".join(sentence[splitting_index+1:])
				#space strings to help make the fron look prettier
				return (first_half_of_sentence, second_half_of_sentence, len(vocab)) #will change to length in a bit!


class User(db.Model):
	"""Users of Wordfit."""

	__tablename__ = 'users'

	user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	email = db.Column(db.String, nullable=False)
	password = db.Column(db.String, nullable=False)
	fname = db.Column(db.String, nullable=False)
	lname = db.Column(db.String,nullable=False)

	words = db.relationship('Word', secondary='user_word', backref=db.backref('users'))
	# made small changes: backref=db.backref('users') to backref='users'-didin't work
	#not sure if I'm setting this up right--is probablu throwing the error

	@classmethod
	def add_user(cls, user_id, email, password, fname, lname):
		"""Add user objects to db when users sign up in the app"""
		pass 

# Another way to create tables that won't be actual objects
# user_word = db.Table('user_word',
# 					db.Column('user_word_id', db.Integer, primary_key=True, autoincrement=True),
# 					db.Column('user_id', db.Integer, db.ForeignKey('users.user_id')),
# 					db.Column('word_id', db.Integer, db.ForeignKey('words.word_id'))
	# )
class UserWord(db.Model):
	"""Maps each user to each individual word object they stored."""

	__tablename__ = 'user_word'

	user_word_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
	word_id = db.Column(db.Integer, db.ForeignKey('words.word_id'))

###################################################################################
#Helper Functions

def connect_to_db(app):
	"""Connect the databse to the Flask app"""

	app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wordfit.db'
	db.app = app
	db.init_app(app)


if __name__ == "__main__":
	from server import app
	connect_to_db(app)
	print "Connected to DB"






