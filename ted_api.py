import urllib2
import json
import string
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
	"""Returns the entire transcript as a string based on given slug."""
	url = 'http://www.ted.com/talks/' + slug + "/transcript?language=en"

	content = urllib2.urlopen(url)
	soup = BeautifulSoup(content, "html.parser")

	soup.prettify()
	soup.get_text() #gets all the text from the url

	text = []
	for hit in soup.findAll(attrs={'class' : 'talk-transcript__fragment'}):
		text.append(hit.contents[0]) #returns lists of each talk

	return " ".join(text)

#Vocab Selection Functions:

def create_lemma_dict(file):
	"""Creates a dictionary of academic words.

	For each pair, the key is the lemma; the value is a list of other word forms."""
	academic_words  = open(file)
	lemma_dict = {}
	for line in academic_words:
		line =line.rstrip().rstrip(',')
		words = line.split(',')
		root = words[0]
		lemma_dict[root] = words

	return lemma_dict

def purge_words(text):
	"""Creates a list of lower-case words without non-alpha characters."""

	word_list = text.split()
	purged_word_list = []
	
	#Ensure non-alpha characters are removed from each word
	for word in word_list:
		if word == '(Applause)' or word == '(Laughter)':#ignores sound words
			continue
		word_elements = list(word)
		for char in word_elements:
			if char not in string.ascii_letters:
				word_elements.remove(char)

		word = "".join(word_elements).lower()
		purged_word_list.append(word)

	return purged_word_list

def analyze_words(word_list):
	"""Creates a dictionary of each word and their corresponding values.

	In each key-value pair, the key is each word, the value is a tuple
	that contains three elements:
	 	-word in lemma_dict: True/False 
	 	-the length of the word
	 	-usage frequency in text."""
	
	word_analysis = {}
	for word in word_list:
		if word in word_analysis:
			word_analysis[word][2] = word_analysis.get(word)[2] + 1
		else:
			academic = (word in lemma_dict)
			length = len(word)
			frequency = 1
			word_analysis[word] = [academic, length, frequency]

	return word_analysis
	
def sort_word_analysis(word_analysis):
	"""Weighs the value of each word and returns the top 10 most important vocab."""
	reverse_word_analysis = [(tuple(value),key) for key, value in word_analysis.items()]
	reverse_word_analysis.sort(reverse=True)

	vocab_list = [reverse_word_analysis[i][1]for i in range(10)]
	


	return vocab_list
            
def get_vocab(transcript):
	"""Returns a list of 10 vocabulary based on given transcript.

	Selection criteria includes academic level, length, and frequency.
	Utilizes three functions in the following order:
		-purge_words
		-analyze_words
		-sort_word_analysis. """

	#Get rid of ('Applause') at the end of the transcript
	# transcript = transcript.rstrip('(Applause)')
	purged_words = purge_words(transcript)
	analyzed_words = analyze_words(purged_words)
	sorted_word_analysis = sort_word_analysis(analyzed_words)

	return sorted_word_analysis




lemma_dict = create_lemma_dict('Lemma.csv')

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

