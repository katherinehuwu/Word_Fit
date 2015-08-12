import urllib2
import os
import json
import tempfile
import re
from bs4 import BeautifulSoup


ny_times_api = os.environ['NY_TIMES_API_KEY']


def get_nytimes_snippet_url(vocab):
	"""Returns the snippet of the vocab being used and the web_url
	"""

	base_uri = "http://api.nytimes.com/svc/search/v2/articlesearch.json?"
	query = "q="+vocab+"&"
	sort = "sort=newest&"
	the_filter = "fl=web_url&"
	facet_filter = "facet_filter=true&"
	highlight = "hl=true&"
	page = "page=1&"
	api_key = "api-key="+ny_times_api

	final_url = base_uri + query + sort + the_filter + facet_filter + highlight + page + api_key

	json_object = urllib2.urlopen(final_url) #returns a json object
	nytimes_data = json.load(json_object) # returns a dictionary of the data
											 	# json.dumps(data) makes the data a string

	#Gets the first snippet of sentence and the web_url
	snippet = nytimes_data['response']['docs'][0]['snippet']
	web_url = nytimes_data['response']['docs'][0]['web_url']

	return snippet, web_url

def get_sentence_from_snippet(vocab, snippet):
	"""Return a complete sentence from the NY Times Snippet."""

	# snippet_vocab = "<strong>" + vocab + "</strong>"
	

	output_text = tempfile.NamedTemporaryFile(mode = 'r')

	with tempfile.NamedTemporaryFile(delete=False) as input_text:
		input_text.write(snippet.encode('UTF-8'))
		#the snippet is unicode; to write to the the file, will need to be converted 
		# to utf-8; will need to convert it back to unicode for jinja

	#creates an output file: each line is the splitted sentence.
	os.popen("python resources/splitta/sbd.py -m  resources/splitta/model_nb -t " + input_text.name +" -o " + output_text.name)
	os.remove(input_text.name)

	#read lines from the outpue file and store each line in a dictionary
	with open(output_text.name) as parsed_text:
		for sentence in parsed_text:
			match_obj = re.search(vocab, sentence)
			if match_obj:
				sentence.rstrip()
				return sentence
			# if snippet_vocab in sentence.split(): 
			# 	sentence = sentence.rstrip()
			# 	return sentence
		return "No matching sentence in NY Times found."


if __name__ == "__main__":
	
	vocab = "intermediate"
	snippet, web_url = get_nytimes_snippet_url(vocab)
	print snippet
	print web_url
	sentence = get_sentence_from_snippet(vocab, snippet)
	print sentence
