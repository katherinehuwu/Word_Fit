import urllib2
import json
import string
import os
ted_talk_api = os.environ['TED_TALK_API_KEY']
#will need to source in the terminal env this whenever you start the virutalenv
from bs4 import BeautifulSoup
import pprint


def query_talk_info(key_word):
	"""Based on query keyword, returns talk info.
	
	Takes in user key word query and returns a list of tuple pairs
	with each pair in the following format:[(talk_id, [name, date, slug])]
	"""

	the_url = 'https://api.ted.com/v1/search.json?'
	search = 'q='+ key_word +'&categories=talks&api-key='
	api = "".join([char for char in ted_talk_api])
	final_url = the_url + search + api 

	json_object = urllib2.urlopen(final_url)
	data = json.load(json_object)#returns a list of json_object of each talk

	final_results = {}
	for talk in data['results']: # each talk is a dictionary
		for item in talk:		 # each talk has one key: talk 
								 # the value of talk is a dictionary
			talk_id =  talk[item]['id'] 
			talk_name = talk[item]['name'] 
			talk_date = talk[item]['published_at'].split()[0]
			talk_slug = talk[item]['slug']   
			

			final_results[talk_id] = [  talk_name,
										talk_date,
										talk_slug]
	return final_results.items()

def get_image(talk_id):
	image_url = 'https://api.ted.com/v1/talks/'
	image_search = str(talk_id) + '.json?api-key='
	image_api = "".join([char for char in ted_talk_api])
	final_image_url = image_url + image_search + image_api

	image_json = urllib2.urlopen(final_image_url)
	image_data = json.load(image_json)


	image_link = image_data['talk']['images'][1]['image']['url']
	description_blurb = image_data['talk']['description']
	return image_link

def get_blurb(talk_id):
	blurb_url = 'https://api.ted.com/v1/talks/'
	blurb_search = str(talk_id) + '.json?api-key='
	blurb_api = "".join([char for char in ted_talk_api])
	final_blurb_url = blurb_url + blurb_search + blurb_api

	blurb_json = urllib2.urlopen(final_blurb_url)
	blurb_data = json.load(blurb_json)

	description_blurb = blurb_data['talk']['description']
	return description_blurb


def get_video(slug):
	"""Return embeded video link based on given slug."""

	return "https://embed-ssl.ted.com/talks/" + slug + ".html" 

def get_transcript_soup(slug):
	"""Returns the html elements based on given slug."""
	url = 'http://www.ted.com/talks/' + slug + "/transcript?language=en"

	content = urllib2.urlopen(url)
	soup = BeautifulSoup(content, "html.parser")
	
	#CHECK ME!
	soup.prettify() #turn a BS parse tree into a nicely formatted Unicode string
	soup.get_text() #gets only the text within elements, can probably be cancelled
	
	return soup

def get_vocab_transcript(slug):
	"""Returns the entire transcript as a string based on given slug."""
	
	soup = get_transcript_soup(slug)
	text = []
	for hit in soup.findAll(attrs={'class' : 'talk-transcript__fragment'}):
		text.append(hit.contents[0]) #returns lists of each talk

	transcript =  " ".join(text)
	return transcript


def get_webpage_transcript(slug):
	"""Returns a dictionary with para num as key and para text as values."""

	soup = get_transcript_soup(slug)
	text = {}
	i = 1
	for para_break in soup.findAll(attrs = {'class' : 'talk-transcript__para__text'}):
		para_chunks = []
		for hit in para_break.findAll(attrs={'class' : 'talk-transcript__fragment'}):
			para_chunks.append(hit.contents[0]) #returns lists of each talk
		para_string = " ".join(para_chunks)
		text[i] = para_string
		i += 1

	return text


if __name__ == "__main__":					
	print get_blurb(112)
