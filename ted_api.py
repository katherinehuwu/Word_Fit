import urllib2
import json
api_key = 'yeskku7xkzzvqeggpga2uxg6'
from bs4 import BeautifulSoup

#The query api to search for talks 
# query_url = 'https://api.ted.com/v1/search.json?q=culture&categories=talks&api-key=yeskku7xkzzvqeggpga2uxg6'


def query_talk_info(key_word):
	"""Based on query keyword, returns talk info.
	
	Takes in user key word query and returns a list of tuple pairs: the first element is the 
	talk id; the second element is a list that contains the name, date, and slug of the talk. 
	"""

	the_url = 'https://api.ted.com/v1/search.json?'
	search = 'q='+ key_word +'&categories=talks&'
	api = 'api-key=yeskku7xkzzvqeggpga2uxg6'
	final_url = the_url + search + api 

	json_object = urllib2.urlopen(final_url)
	data = json.load(json_object)#returns a list of json_object of each talk

	final_results = {}
	for talk in data['results']: # each talk is a dictionary
		for item in talk:		 # each talk has one key: talk 
								 # the value of talk is a dictionary
			talk_id =  talk[item]['id'] 
			talk_name = talk[item]['name'] 
			talk_date = talk[item]['published_at']
			talk_slug = talk[item]['slug']   
			final_results[talk_id] = [  talk_name,
										talk_date,
										talk_slug]
	return final_results.items()

def get_video(slug):
	"""Return embeded video link based on given slug."""

	return "https://embed-ssl.ted.com/talks/" + slug + ".html" 

def get_transcript(slug):
	url = 'http://www.ted.com/talks/' + slug + "/transcript?language=en"

	content = urllib2.urlopen(url)
	soup = BeautifulSoup(content, "html.parser")

	soup.prettify()
	soup.get_text() #gets all the text from the url

	text = []
	for hit in soup.findAll(attrs={'class' : 'talk-transcript__fragment'}):
		text.append(hit.contents[0]) #returns lists of each talk

	return " ".join(text)
            

if __name__ == "__main__":					
	results = query_talk_info('imagine')
	#results is a list of tuple pairs with id as first
	#element and the info as a list

	print "results is a type of ", type(results)
 
	for key, info in results:
		print "The talk id is '%s'" %key
		print "The talk title is '%s'" %info[0]
		print "The talk date is '%s'" %info[1]
		print "The talk slug is '%s'" %info[2]

