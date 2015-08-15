import urllib2
import os
from bs4 import BeautifulSoup
dictionary_api = os.environ['DICTIONARY_API_KEY']

def get_dictionary_soup(vocab):
	"""Based on vocab, returns the dictionary entry info as bs4 html elements.
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
	"""Return the vocab's part-of-speech in a string.

	Based on the given soup from dictionary and vocab, return
	format as 'verb-noun' 
	"""

	pos = []
	for hit in soup.find_all('fl'):
		pos.append(hit.contents[0].encode('utf-8'))
	pos = list(set(pos))#remove duplicate parts of speech

	return "-".join(pos)


def get_vocab_phonetics(soup, vocab):
	"""Return the phonetic transcription of vocab as a string.
	"""
	# for hit in soup.find(['pr','altpr']):
	if soup.find('pr'):
		for hit in soup.find('pr'):
			return hit
	else:
		return None


def get_vocab_pronunciation(soup, vocab, phonetics):
	"""Return vocab's pronunciation sound link as a string.
	"""
	if phonetics:
		if soup.find('wav'):
			audio_file = ""
			for hit in soup.find('wav'):
				hit = hit.strip(".wav")
				audio_file += hit

			audio_url = "http://www.learnersdictionary.com/audio?"
			audio_file = "file="+audio_file+"&format=mp3&"
			
			word = "word="+vocab+"&pron="+phonetics
			final_url = audio_url + audio_file + word
			return final_url
		else:
			return "/no_pronunciation"
	
	else:
		return "/no_pronunciation"


def get_vocab_definition(soup):
	"""Return vocab's definitions.

	Takes in the dictionary html, finds all heading numbers and definition entries,
	assign each entry to the corresponding heading numbers. Returns a string in 
	the following format: ':def1 :def2 :def3'
	"""

	definition = []
	raw_definition = soup.find('def')###FIX ME-catch unfound dictionary entries
	
	if raw_definition: 
		dt_tag = raw_definition.find_all('dt')

		for item in dt_tag:
			if len(item.contents[0]) > 2:
				definition.append(item.contents[0])

	 
		organized_definition = "" #needs to be a string to store in sqlite

		for entry in definition:
			entry_string = unicode(entry)
			print entry_string
			organized_definition += entry_string
		
		return organized_definition
	else:
		return "No dictionary definition found."

def get_dictionary_info(vocab):
	"""Return vocab's part-of-speech, phonetics, pronunciation, and definition"

	Given the vocab, returns a list in the following format:
	[part-of-speech, pronunciation, definition]
	['verb-noun-adjective', link_to_pronunciation, ':def1 :def2']
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

	vocab = "scrolling"
	soup = get_dictionary_soup(vocab)
	# parts_of_speech = get_parts_of_speech(soup, vocab)
	# print parts_of_speech
	
	# phonetics =  get_vocab_phonetics(soup, vocab)
	# print phonetics

	# pronunciation = get_vocab_pronunciation(soup, vocab, phonetics)
	# print pronunciation

	# definition = get_vocab_definition(soup)
	# print definition
	# print get_dictionary_info(vocab)

	parts_of_speech = get_dictionary_info(vocab)[0]
	print parts_of_speech 
	pronunciation = get_dictionary_info(vocab)[1]
	print pronunciation
	definition = get_dictionary_info(vocab)[2]
	print definition
	other_usage = " "


	






