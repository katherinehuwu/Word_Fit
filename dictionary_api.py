import urllib2
import os
from bs4 import BeautifulSoup
dictionary_api = os.environ['DICTIONARY_API_KEY']
import requests

def get_dictionary_soup(vocab):
	"""Based on vocab, returns the dictionary entry info as bs4 html elements.
	"""

	the_url ='http://www.dictionaryapi.com/api/v1/references/learners/xml/'
	vocab = vocab+"?key="
	api = "".join([char for char in dictionary_api])

	final_url = the_url + vocab + api 
	# url_info = urllib2.urlopen(final_url)

	result = requests.get(final_url, auth=('user', 'pass'))
	content= result.content
	soup = BeautifulSoup(content, "html.parser")
	
	# soup = BeautifulSoup(url_info, "html.parser")
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
	url_base = "http://media.merriam-webster.com/soundc11/"
	sub_dir = ""
	wav = ""
	
	if vocab.startswith("bix"):
		sub_dir = "bix"
	elif vocab.startswith("gg"):
		sub_dir = "gg"
	elif vocab[0].isdigit():
		sub_dir = "number"
	else:
		sub_dir = vocab[0]

	if phonetics:
		if soup.find('wav'):
			for hit in soup.find('wav'):
				wav = hit
		else:
			return "/no_pronunciation"
	else:
		return "/no_pronunciation"

	final_url = url_base + "/" + sub_dir +"/"+ wav
	return final_url


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
		# print "The list", definition
		organized_definition = "" #needs to be a string to store in sqlite

		for entry in definition:
			entry_string = unicode(entry)
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

	vocab = "thermal"
	soup = get_dictionary_soup(vocab)
	parts_of_speech = get_parts_of_speech(soup, vocab)
	phonetics =  get_vocab_phonetics(soup, vocab)
	pronunciation = get_vocab_pronunciation(soup, vocab, phonetics)
	definition = get_vocab_definition(soup)
	
	print get_dictionary_info(vocab)

	


	






