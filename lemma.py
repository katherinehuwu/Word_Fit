

def create_lemma_dict(lemma_file):
	"""Creates a dictionary of lemmatized academic words.

	For each pair, the key is the word inflection; the value is the stem."""
	academic_words= open(lemma_file)
	LEMMA_DICT = {}
	for line in academic_words:
		line =line.rstrip().rstrip(',')
		words = line.split(',')
		stem = words[0]
		for word in words:
			LEMMA_DICT[word] = stem

	return LEMMA_DICT


LEMMA_DICT = create_lemma_dict('resources/Lemma.csv')
print LEMMA_DICT