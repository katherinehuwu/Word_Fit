"""Models and databse functions for Wordfit project."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#Model definitions

class Transcript(db.Model): 
	"""Talk info and transcript of each talk that users selected."""

	__tablename__ = 'transcripts'

	talk_id = db.Column(db.Integer, primary_key=True)
	slug = db.Column(db.String, nullable=False)
	transcript = db.Column(db.String, nullable=False)

	def __repr__(self):
		return "<Talk talk_id=%d slug=%s>" %(self.talk_id, self.slug)

	@classmethod
	def add_transcript(cls, talk_id, slug, transcript):
		"""Insert a new Transcript object to db based on user selection.

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
	word = db.Column(db.String, nullable=False)
	talk_id = db.Column(db.Integer, db.ForeignKey('transcripts.talk_id'))
	

	transcript = db.relationship('Transcript', backref=db.backref('words', order_by=word_id))

	def __repr__(self):
		return "<Word word_id=%d word=%s talk_id=%d>" %(self.word_id, self.word, self.talk_id)

	@classmethod
	def add_words(cls, talk):
		"""Add word objects to db by parsing the given transcript.

		Words are selected based on its usage frequency in the transcript and 
		whether they are in the academic word list. """

		pass

#Word.add_word(word_id, ......sentence)
		#will need to change model set up and add a method to match this
		#then pass in word objects to render template
		#everything can then be displayed!!

		#vocab attributes: word_id(autoincrement)
					#  talk_id --is already up there
					#  the_word 
					#  the stem
					#  sentence it occured in
					# 	selection criteria
	# #store vocab in db

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






