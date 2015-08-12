import urllib2
import os
from bs4 import BeautifulSoup
from xml.etree import ElementTree as ET


dictionary_api = os.environ['DICTIONARY_API_KEY']
#will need to source in the terminal env this whenever you start the virutalenv


def get_dictionary_soup(vocab):
	"""Based on vocab, returns dictionary entry info as bs4 html elements.
	"""

	the_url ='http://www.dictionaryapi.com/api/v1/references/learners/xml/'
	vocab = vocab+"?key="
	api = "".join([char for char in dictionary_api])

	final_url = the_url + vocab + api 
	url_info = urllib2.urlopen(final_url)
	
	soup = BeautifulSoup(url_info, "html.parser")
	soup.prettify()#Turns the soup into a nicely formated Unicode string
		
	return soup


def get_parts_of_speech(soup, vocab):
	"""Return the vocab's part-of-speech in a list.

	Based on the given soup from dictionary and vocab
	looks for all the part-of-speech of the vocab"""

	pos = []
	for hit in soup.find_all('fl'):
		pos.append(hit.contents[0].encode('utf-8'))
	return list(set(pos))#remove duplicate parts of speech


def get_vocab_phonetics(soup, vocab):
	"""Return the phonetic transcription of vocab as a string.
	"""

	for hit in soup.find('pr'):
		# hit = hit.encode('utf-8')
		return hit


def get_vocab_pronunciation(soup, vocab, phonetics):
	"""Return vocab's pronunciation sound link.

	Based on the given soup from dictionary and vocab
	look return the vocab pronunciation link."""

	audio_file = ""
	for hit in soup.find('wav'):
		hit = hit.strip(".wav")
		audio_file += hit

	audio_url = "http://www.learnersdictionary.com/audio?"
	audio_file = "file="+audio_file+"&format=mp3&"
	phonetics
	word = "word="+vocab+"&pron="+phonetics

	final_url = audio_url + audio_file + word
	return final_url


def get_vocab_definition(soup):
	"""Return vocab's definitions.

	Takes in the dictionary html, finds all heading numbers and definition entries,
	assign each entry to the corresponding heading numbers. Returns a list of tuple
	pairs: [('heading num', 'defintion')]
	"""

	definition = []
	raw_definition =  soup.find('def')
	dt_tag = raw_definition.findAll(['sn', 'dt'])
	
	for item in dt_tag:
		definition.append(item.get_text())

	definition_length = len(definition)	
	organized_definition = []
	
	key = ""
	for i in range(definition_length):
		if len(definition[i]) < 2:
			key += definition[i]
		else:
			definition_string = str(definition[i].encode('utf-8'))
			
			if "[=" in definition_string:
				cutting_index = definition_string.index("[=")
				definition_elements = list(definition_string)[:cutting_index]
				definition_only = "".join(definition_elements)

				# print key, definition_only
				organized_definition.append((key.encode('utf-8'), definition_only))
				key = ""
	
	return organized_definition 

def get_dictionary_info(vocab):
	"""Return vocab's part-of-speech, phonetics, pronunciation, and definition"

	Given the vocab, returns a list in the following format:
	[part-of-speech, pronunciation, [(num1, definition), (num2, definition)] )
	"""

	soup = get_dictionary_soup(vocab)
	parts_of_speech = get_parts_of_speech(soup, vocab)
	phonetics =  get_vocab_phonetics(soup, vocab)
	pronunciation = get_vocab_pronunciation(soup, vocab, phonetics)
	definition = get_vocab_definition(soup)

	dictionary_info = [parts_of_speech,
						pronunciation,
						definition]

	return dictionary_info



if __name__ == "__main__":

	vocab = "business"
	# soup = get_dictionary_soup(vocab)
	# parts_of_speech = get_parts_of_speech(soup, vocab)
	# print parts_of_speech
	
	# phonetics =  get_vocab_phonetics(soup, vocab)
	# print phonetics

	# pronunciation = get_vocab_pronunciation(soup, vocab, phonetics)
	# print pronunciation

	# definition = get_vocab_definition(soup)
	# print definition

	print get_dictionary_info(vocab)


	






