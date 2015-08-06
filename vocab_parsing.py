import string
import os
import tempfile


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
		input_text.write(transcript_string)

	os.popen("python resources/splitta/sbd.py -m  resources/splitta/model_nb -t "+input_text.name+" -o " +output_text.name)
	os.remove(input_text.name)

	#read lines from the outpue file and store each line in a dictionary
	with open(output_text.name) as parsed_text:
		sentence_index = {}
		for index, sentence in enumerate(parsed_text):
			sentence = sentence.rstrip()
			sentence_index[index] = sentence

		return sentence_index


#Vocab Selection Functions:
def create_lemma_dict(file):
	"""Creates a dictionary of lemmatized academic words.

	For each pair, the key is the word inflection; the value is the stem."""
	academic_words  = open(file)
	LEMMA_DICT = {}
	for line in academic_words:
		line =line.rstrip().rstrip(',')
		words = line.split(',')
		stem = words[0]
		for word in words:
			LEMMA_DICT[word] = stem

	return LEMMA_DICT


def purge_words(transcript_string):
	"""Creates a clean list of lower-case words from the given transcript string.

	The purpose is to be able to compare this transcript_string with lemma_dict.
	Takes in the transcript as a string. 
	Removes sound words: '(Applause)' and non-alpha characters. 
	Changes uppercase letters to lower case letters
	."""

	word_list = transcript_string.split()
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


def analyze_words(word_list, sentence_index):
	"""Creates a dictionary of each word from the word_list(purged) and their corresponding values.

	To reference the example sentence, the sentence_index needs to be passed in.
	In each key-value pair, the key is each word, the value is a tuple
	that contains three elements:
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

			#access word location index
			for index, sentence in sentence_index.items():
				if word in sentence:
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
					)
				)for i in range(10)]
	

	return vocab_list
	#right now returns a list of tuple pairs, (vocab, (stem, sentence))
            
def get_vocab(transcript):
	"""Returns a list of 10 vocabulary based on given transcript.

	Selection criteria includes academic level, length, and frequency.
	Utilizes three functions in the following order:
		-purge_words
		-analyze_words
		-sort_word_analysis. """

	#Get rid of ('Applause') at the end of the transcript
	# transcript = transcript.rstrip('(Applause)')
	sentence_index = parse_transcript(transcript)
	purged_words = purge_words(transcript)
	analyzed_words = analyze_words(purged_words, sentence_index)
	sorted_word_analysis = sort_word_analysis(analyzed_words, sentence_index)

	return sorted_word_analysis


LEMMA_DICT = create_lemma_dict('Lemma.csv')


if __name__ == "__main__":
	sample_text = "Of course, its no secret that governments are able to intercept telephone calls and text messages. Its for that reason that many activists specifically avoid using the telephone. Instead, they use tools like Skype, which they think are immune to interception. Theyre wrong. There have now been over the last few years an industry of companies who provide surveillance technology to governments, specifically technology that allows those governments to hack into the computers of surveillance targets. Rather than intercepting the communications as they go over the wire, instead they now hack into your computer, enable your webcam, enable your microphone, and steal documents from your computer."
 
	print get_vocab(sample_text)







