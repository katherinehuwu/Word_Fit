import string
import os
import tempfile
from lemma import LEMMA_DICT

# from nltk.stem.wordnet import WordNetLemmatizer
# lmtzr = WordNetLemmatizer()


class VocabFactory(object):

	def __init__(self, transcript_string):
		self.transcript_string = transcript_string
		self.parse_transcript()
		self.purge_words()

	def __repr__(self):
		return "<VocabFactory sentence_index=%s word_list=%s>" %(self.sentence_index, self.word_list)




	def parse_transcript(self):
		"""Parse complete sentences out of a given string of text.

		Returns a dict where the key is an index num and the value is a sentence.
		Uses command lines in the splitta package. Will involve temp input and out files. """
		
		output_text = tempfile.NamedTemporaryFile(mode = 'r')
		with tempfile.NamedTemporaryFile(delete=False) as input_text:
			input_text.write(self.transcript_string.encode('utf-8'))
			#to write to the file, convert to utf-8; to use for jinja, convert it back to unicode

		os.popen("python vocab_resources/splitta/sbd.py -m  vocab_resources/splitta/model_nb -t " + input_text.name +" -o " + output_text.name)
		os.remove(input_text.name)

		with open(output_text.name) as parsed_text:
			sentence_index = {}
			for index, sentence in enumerate(parsed_text):
				sentence = sentence.rstrip()
				sentence_index[index] = sentence

		sentence_index[len(sentence_index)] = "Unable_to_find_matching_sentence" #avoid outliers
		self.sentence_index = sentence_index




	def purge_words(self):
		"""Creates a dictionary of lower-case words as keys and values is a list of each occurence.

		Encode transcript string as utf-8. Removes sound words: '(Applause)' and non-alpha characters."""

		word_list = self.transcript_string.encode('utf-8').split()
		purged_word_list = {}
		for word in word_list:
			if word.isalpha():
				if word.islower():
					purged_word_list.setdefault(word, []).append(word)
				else:
					lower_word = word.lower()
					purged_word_list.setdefault(lower_word, []).append(word) 
			else:
				continue 
		
		self.word_list = purged_word_list




	def analyze_words(self):
		"""Creates a dictionary with each word as they keys and weight as values.

		References sentence_index and word list. In each key-value pair, the key is each word, the value is a tuple
		that contains these elements:
		 	-word in LEMMA_DICT: True/False                         -the length of the word
		 	-usage frequency in text                                -the stem
		 	-word location: the example sentence index in text      -selection criteria: academic word, complexity, frequency"""
		
		word_analysis = {}
		for word in self.word_list:
			if word not in word_analysis:
				academic = (word in LEMMA_DICT)
				length = len(word)
				frequency = len(self.word_list[word])
				stem = word	
				word_location_index = len(self.sentence_index)-1 #first set it as the last index
				
				for index, sentence in self.sentence_index.items():
					if word in sentence.split():#need to be individual words, not parts of a word
						word_location_index = index 
						break
					if self.word_list[word][0] in sentence.split():#accounts for words with upper cases
						word_location_index = index
					
				#selection critera
				if academic:
					selection_criteria = 'academic word'
				elif frequency > 1: 
					selection_criteria = 'high frequency'
				else:
					selection_criteria = 'word length'

				word_analysis[word] = (academic, length, frequency, stem, word_location_index, selection_criteria)
		
		self.word_analysis = word_analysis
		
		return self.word_analysis
		



	def sort_word_analysis(self):
		"""Weighs the importance of each word and returns the top 10 most important vocab with attributes.

		Select 10 important vocabulary based on:academic word, word length, usage frequency 
		The vocab attributes include the stem, frequency, sentence, and selection_criteria
		Return a list of 10 tuple pairs: [(vocab, (stem, freq, sentence, selection))]"""

		reverse_word_analysis = [(value,key) for key, value in self.word_analysis.items()]
		reverse_word_analysis.sort(reverse=True)

		vocab_list = [	(reverse_word_analysis[i][1],                        #[1]: the word; [0]: the attribute values 
						(reverse_word_analysis[i][0][3],                     #stem: 3rd index 
						reverse_word_analysis[i][0][2],                      #frequency; 2nd index
						self.sentence_index[reverse_word_analysis[i][0][4]], #the sentence location index; 4th index 
						reverse_word_analysis[i][0][5],                      #selection criteria: 5th index 
						)) for i in range(10)]
		
		self.vocab_list = vocab_list
		
		return vocab_list
	  



	def get_vocab(self):
		"""Returns a list of 10 vocabulary based on given transcript. """

		self.parse_transcript() 
		self.purge_words()
		self.analyze_words()
		self.sort_word_analysis()



if __name__ == "__main__":
	
	sample_text = "The intensity of the political conversation made you nervous. Conversation is important. You should take this political opportunity to have another conversation."
	my_text = VocabFactory(sample_text)
	print my_text
	my_text.get_vocab()
	print my_text.vocab_list

	






