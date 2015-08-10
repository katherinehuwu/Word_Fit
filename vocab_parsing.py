import string
import os
import tempfile
import re
import string
from lemma import LEMMA_DICT

""" Additional Parse Transcript Info: To identify the sentence the word belongs to, will 1) need to work with splitta.
	To work with splitta, 2) need to be able to work with os to interact with command lines
	Also 3) need to be able to write trancript on to temporary files as input text and
							4) read from the output text given by splitta."""


def parse_transcript(transcript_string):
	"""Parse complete sentences out of a given string of text.

	Returns a dict where the key is an index num and the value is a sentence.
	Uses command lines in the splitta package. Will involve temp input and out files. """

	output_text = tempfile.NamedTemporaryFile(mode = 'r')

	with tempfile.NamedTemporaryFile(delete=False) as input_text:
		input_text.write(transcript_string.encode('UTF-8'))
		#the transcript_string type is unicode; in order to write to the
		#the file, will need to be converted to utf-8, which is more generally accepted
		#(with the exception of jinja in html-- will need to convert it back to unicode)

	#creates an output file: each line is the splitted sentence.
	os.popen("python resources/splitta/sbd.py -m  resources/splitta/model_nb -t " + input_text.name +" -o " + output_text.name)
	os.remove(input_text.name)

	#read lines from the outpue file and store each line in a dictionary
	with open(output_text.name) as parsed_text:
		sentence_index = {}
		for index, sentence in enumerate(parsed_text):
			sentence = sentence.rstrip()
			sentence_index[index] = sentence

	sentence_index[len(sentence_index)] = "Unable_to_find_matching_sentence"
	#adds a sentence index to prevent outlier vocabulary
	#has already accounted for words that are in caps
	return sentence_index


#Vocab Selection Functions:
def purge_words(transcript_string):
	"""Creates a clean list of lower-case words from the given transcript string.

	Compare this transcript_string with lemma_dict and sentence index.
	Takes in the transcript as a string.
	Encode it as 'UTF-8'
	Removes sound words: '(Applause)' and non-alpha characters. 
	Changes uppercase letters to lower case letters
	."""

	word_list = transcript_string.encode('UTF-8').split()
	#both the sentence dictionary and the word has to be in the same format: utf-8
	purged_word_list = {}
	
	#Ensure non-alpha characters are not considered in the list
	for word in word_list:
		if word.isalpha():
			if word.islower():
				purged_word_list[word] = word #key:value are both original word
			else:
				lower_word = word.lower()
				purged_word_list[lower_word] = word #key is lowercase; value is original word
		else:
			continue #ignore words with nonalpha characters

	print purged_word_list
	return purged_word_list


def analyze_words(word_list, sentence_index):
	"""Creates a dictionary of each word from the word_list(purged) and their corresponding values.

	To reference the example sentence, the sentence_index needs to be passed in.
	In each key-value pair, the key is each word, the value is a tuple
	that contains these elements:
	 	-word in LEMMA_DICT: True/False 
	 	-the length of the word
	 	-usage frequency in text
	 	-the stem
	 	-word location: the example sentence index in text.
	 	-selection criteria: academic word, complexity, frequency"""
	
	word_analysis = {}
	for word in word_list:
		if word in word_analysis:
			word_analysis[word][2] = word_analysis.get(word)[2] + 1
			#word_analysis[word][2] refers to the freq
			#update freq if the word is already in there/ignore other values
			word_analysis[word][5] = 'high frequency'
			#if freq > 2, considered as high frequency word

		else:
			academic = (word in LEMMA_DICT)
			length = len(word)
			frequency = 1
			stem = LEMMA_DICT.get(word, word)
			word_location_index = len(sentence_index)-1
			#access word location index
			
			for index, sentence in sentence_index.items():
				if word in sentence: 
					word_location_index = index 
					break
				if word_list[word] in sentence:
					word_location_index = index
		
			#determine selection critera
			if academic:
				selection_criteria = 'academic word'
			else:
				selection_criteria = 'word length'

			word_analysis[word] = [academic, length, frequency, stem, word_location_index, selection_criteria]
			
			
			
	return word_analysis
	

def sort_word_analysis(word_analysis, sentence_index):
	"""Weighs the importance of each word and returns the top 10 most important vocab with attributes.

	Importance is evaluated based on the following, from most to least important:
									academic word, word length, usage frequency in text
	
	The vocab attributes include the stem, 
									frequency, 
									sentence it occured in, 
									selection_criteria.

	Return a list of 10 tuple pairs: (vocab, (attributes))
	"""

	reverse_word_analysis = [(tuple(value),key) for key, value in word_analysis.items()]
	reverse_word_analysis.sort(reverse=True)

	vocab_list = [	(reverse_word_analysis[i][1], 
					
					# reverse_word_analysis[i]refer to top 10 tuples of([values], word) 
					# [1]refer to the word; [0]refer to [values] 

					(reverse_word_analysis[i][0][3], #stem;3rd index in tuple 
					reverse_word_analysis[i][0][2], #frequency; 2nd index
					sentence_index[reverse_word_analysis[i][0][4]], #word_location_index; 4th index 
					reverse_word_analysis[i][0][5], #the selection criteria; 5th index 
					)) for i in range(10)]
	

	return vocab_list
	# returns a list of tuple pairs, (vocab, (stem, sentence))
            
def get_vocab(transcript):
	"""Returns a list of 10 vocabulary based on given transcript.

	Selection criteria includes academic level, length, and frequency.
	Utilizes three functions in the following order:
		-purge_words
		-analyze_words
		-sort_word_analysis. """

	sentence_index = parse_transcript(transcript) 
	# a dict of {0: sentence1, 1:sentence2}. 
	#Caps and punctuation are kepted.

	purged_words = purge_words(transcript)

	analyzed_words = analyze_words(purged_words, sentence_index)
	sorted_word_analysis = sort_word_analysis(analyzed_words, sentence_index)

	return sorted_word_analysis

if __name__ == "__main__":
	sample_text = "Of course, its no secret that governments are able to intercept telephone calls and text messages. Its for that reason that many activists specifically avoid using the telephone. Instead, they use tools like Skype, which they think are immune to interception. Theyre wrong. There have now been over the last few years an industry of companies who provide surveillance technology to governments, specifically technology that allows those governments to hack into the computers of surveillance targets. Rather than intercepting the communications as they go over the wire, instead they now hack into your computer, enable your webcam, enable your microphone, and steal documents from your computer."
 
	print get_vocab(sample_text)







