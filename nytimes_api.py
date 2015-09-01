import os
import json
import tempfile
import re
import requests


ny_times_api = os.environ['NY_TIMES_API_KEY']


def get_nytimes_snippet_url(vocab):
	"""Returns the snippet of the vocab being used and the web_url"""

	base_uri = "http://api.nytimes.com/svc/search/v2/articlesearch.json?"
	query = "q="+vocab+"&"
	sort = "sort=newest&"
	the_filter = "fl=web_url&"
	highlight = "hl=true&"
	page = "page=1&"
	api_key = "api-key="+ny_times_api
	final_url = base_uri + query + sort + the_filter + highlight + page + api_key

	r = requests.get(final_url, auth=('user', 'pass'))
	nytimes_data = r.json()
	
	i = 0 #snippet is not always present in the first object
	snippet_access = nytimes_data['response']['docs'][i]
	while snippet_access.get('snippet', None) == None:
		i += 1
		snippet_access = nytimes_data['response']['docs'][i]
	
	snippet = snippet_access['snippet']
	web_url = nytimes_data['response']['docs'][i]['web_url']

	return snippet, web_url




def get_sentence_from_snippet(vocab, snippet):
	"""Return a complete sentence from the NY Times Snippet."""
	
	output_text = tempfile.NamedTemporaryFile(mode = 'r')

	with tempfile.NamedTemporaryFile(delete=False) as input_text:
		input_text.write(snippet.encode('utf-8'))
		
	os.popen("python resources/splitta/sbd.py -m  resources/splitta/model_nb -t " + input_text.name +" -o " + output_text.name)
	os.remove(input_text.name)

	with open(output_text.name) as parsed_text:
		for sentence in parsed_text:
			match_obj = re.search(vocab, sentence.lower())
			if match_obj:
				sentence = sentence.rstrip()
				
				#Use regex to parse out <strong> and </strong>
				start_tag = re.search("<strong>", sentence)
				start_start_tag = start_tag.start()
				end_start_tag = start_tag.end()

				end_tag = re.search("</strong>", sentence)
				start_end_tag = end_tag.start()
				end_end_tag = end_tag.end()

				begin_chunk = sentence[:start_start_tag]
				key_word = sentence[end_start_tag:start_end_tag]
				final_chunk = sentence[end_end_tag:]

				sentence = begin_chunk + key_word + final_chunk
				return sentence
			
		return "No matching sentence in NY Times found."




if __name__ == "__main__":
	
	vocab = "individually"
	print "SEARCHING RESULTS FOR:", vocab
	snippet, web_url = get_nytimes_snippet_url(vocab)
	print "THE SNIPPET", snippet
	print "THE WEB URL", web_url

