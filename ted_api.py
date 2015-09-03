import json
import string
import os
from bs4 import BeautifulSoup
import requests
ted_talk_api = os.environ['TED_TALK_API_KEY']


def query_talk_info(key_word):
	"""Based on query keyword, returns talk info.
	
	Takes in user key word query and returns a list of tuple pairs
	with each pair in the following format:[(talk_id, [name, date, slug])]
	"""

	the_url = 'https://api.ted.com/v1/search.json?'
	search = 'q='+ key_word +'&categories=talks&api-key='
	api = "".join([char for char in ted_talk_api])
	final_url = the_url + search + api 

	r = requests.get(final_url)
	data = r.json()

	final_results = {}
	for talk in data['results']: 
		for item in talk:		 
								 
			talk_id =  talk[item]['id'] 
			talk_name = talk[item]['name'] 
			talk_date = talk[item]['published_at'].split()[0]
			talk_slug = talk[item]['slug']   
			

			final_results[talk_id] = [  talk_name,
										talk_date,
										talk_slug]
	return final_results.items()




def get_image_blurb(talk_id):
	"""Get ted talk image and description"""

	image_url = 'https://api.ted.com/v1/talks/'
	image_search = str(talk_id) + '.json?api-key='
	image_api = "".join([char for char in ted_talk_api])
	final_image_url = image_url + image_search + image_api

	r = requests.get(final_image_url)
	image_data = r.json()
	image_link = image_data['talk']['images'][1]['image']['url']

	blurb = image_data['talk']['description']
	blurb = blurb.split("<")[0]

	return image_link, blurb




def get_video(slug):
	"""Return embeded video link based on given slug."""

	return "https://embed-ssl.ted.com/talks/" + slug + ".html" 




def get_transcript_soup(slug):
	"""Returns the html elements based on given slug."""
	url = 'http://www.ted.com/talks/' + slug + "/transcript?language=en"

	result = requests.get(url)
	content= result.content
	soup = BeautifulSoup(content, "html.parser")
	
	soup.prettify()
	soup.get_text() 
	
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
	print query_talk_info('tech')

