#Tests vocab_parsing function

import unittest
from vocab_resources.vocab_parsing import VocabFactory


class VocabFactoryTestCase(unittest.TestCase):
    """Examples of unit tests: discrete code testing."""

    sample_text = """The intensity of the political conversation made you nervous. 
                    Conversation is important.
                    You should take this political opportunity to have another conversation."""

    my_list = VocabFactory(sample_text)

    def test_parse_transcript(self):

    	self.assertEqual(sorted(self.my_list.sentence_index.items()),
    					[(0, 'The intensity of the political conversation made you nervous .'), 
                        (1, 'Conversation is important .'), 
                        (2, 'You should take this political opportunity to have another conversation .'), 
                        (3, 'Unable_to_find_matching_sentence')])


    def test_purge_words(self):
    	self.assertEqual(sorted(self.my_list.word_list.items()), 
    					[('another', ['another']), ('conversation', ['conversation', 'Conversation']), ('have', ['have']), 
                        ('intensity', ['intensity']), ('is', ['is']), ('made', ['made']), ('of', ['of']), ('opportunity', ['opportunity']), 
                        ('political', ['political', 'political']), ('should', ['should']), ('take', ['take']), ('the', ['The', 'the']), 
                        ('this', ['this']), ('to', ['to']), ('you', ['you', 'You'])])
    	
   
    def test_analyze_words(self):
    	self.assertEqual(sorted(self.my_list.analyze_words().items()), 
    					[('another', (False, 7, 1, 'another', 2, 'word length')), 
                        ('conversation', (False, 12, 2, 'conversation', 0, 'high frequency')), 
                        ('have', (False, 4, 1, 'have', 2, 'word length')), 
                        ('intensity', (True, 9, 1, 'intensity', 0, 'academic word')), 
                        ('is', (False, 2, 1, 'is', 1, 'word length')), 
                        ('made', (False, 4, 1, 'made', 0, 'word length')), 
                        ('of', (False, 2, 1, 'of', 0, 'word length')), 
                        ('opportunity', (False, 11, 1, 'opportunity', 2, 'word length')), 
                        ('political', (False, 9, 2, 'political', 0, 'high frequency')), 
                        ('should', (False, 6, 1, 'should', 2, 'word length')), 
                        ('take', (False, 4, 1, 'take', 2, 'word length')), 
                        ('the', (False, 3, 2, 'the', 0, 'high frequency')), 
                        ('this', (False, 4, 1, 'this', 2, 'word length')), 
                        ('to', (False, 2, 1, 'to', 2, 'word length')), ('you', (False, 3, 2, 'you', 0, 'high frequency'))])

    def test_sort_word_analysis(self):
        self.assertEqual(self.my_list.sort_word_analysis(), 
                        [('intensity', ('intensity', 1, 'The intensity of the political conversation made you nervous .', 'academic word')), 
                        ('conversation', ('conversation', 2, 'The intensity of the political conversation made you nervous .', 'high frequency')), 
                        ('opportunity', ('opportunity', 1, 'You should take this political opportunity to have another conversation .', 'word length')), 
                        ('political', ('political', 2, 'The intensity of the political conversation made you nervous .', 'high frequency')), 
                        ('another', ('another', 1, 'You should take this political opportunity to have another conversation .', 'word length')), 
                        ('should', ('should', 1, 'You should take this political opportunity to have another conversation .', 'word length')), 
                        ('this', ('this', 1, 'You should take this political opportunity to have another conversation .', 'word length')), 
                        ('take', ('take', 1, 'You should take this political opportunity to have another conversation .', 'word length')), 
                        ('made', ('made', 1, 'The intensity of the political conversation made you nervous .', 'word length')), 
                        ('have', ('have', 1, 'You should take this political opportunity to have another conversation .', 'word length'))])

    def test_get_vocab(self):
        self.assertEqual(self.my_list.get_vocab(), None)


if __name__ == '__main__':
    unittest.main()
