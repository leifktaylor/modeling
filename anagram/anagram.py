# Anagrams for choate
import random
import itertools

class WordList(object):
    def __init__(self, wordfile='biglist.txt'):
        self.wordfile = wordfile
        with open(wordfile) as word_file:
            self.wordlist = [line.rstrip('\n') for line in word_file]

    def create_sentence(self, word_length):
        """
        :param word_length: amount of words in sentence
        :return: list of words
        """
        return [random.choice(self.wordlist) for i in range(0, word_length)]

    def is_word(self, word):
        """
        Checks if word is in word list.
        :param word: word to check
        :return: True or False
        """
        return word in self.wordlist

    def anagram_word(self, word, shuffle=True):
        """
        :param word: a string
        :return: anagram of that word
        """
        permuation_list = self._string_permuations(word)
        if shuffle:
            random.shuffle(permuation_list)
        for test_word in permuation_list:
            # Make sure if apostrophe (') in word, that it is the second to last letter
            if "'" in test_word:
                test_word = test_word.replace("'", "")
                test_word = test_word[:-1] + "'" + test_word[-1:]

            # If the shuffled word exists in the dictionary return it, otherwise keep trying
            if self.is_word(test_word):
                return test_word

        raise RuntimeError('Unable to anagram word')

    def _string_permuations(self, string):
        """
        Shuffles the letters of a string
        :param string: string to shuffle
        :return: shuffled string
        """
        permutation_list = list(map(''.join, itertools.permutations(string)))
        permutation_list.pop(permutation_list.index(string))
        return permutation_list

