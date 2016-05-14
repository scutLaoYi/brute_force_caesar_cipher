import io
import logging
import tools.common

dictionary_file = "dictionary.txt"

import string

#remove everything except alphabet in lowercase
class Del:
    def __init__(self, keep=string.ascii_lowercase):
        self.comp = dict((ord(c),c) for c in keep)
    def __getitem__(self, k):
        return self.comp.get(k)
DD = Del()

class SpellChecker:
    def __init__(self, words_file):
        self.load_words(words_file)
        logging.info('[SPELL CHECKER] Init ok!')

    def load_words(self, file_name):
        with open(file_name) as f:
            text = f.read()
            self.words_list = text.split()
        logging.info('[SPELL CHECKER] Init with dictionary size: {}'.format(len(self.words_list)))

    def score(self, text):
        if (len(self.words_list) == 0) :
            logging.error('[SPELL CHECKER] Dictionary empty! Will always failed in word check!')
            return 0
        score = 0
        total = 0
        for word in text.split():
            word = word.translate(DD)
            total += 1
            if word in self.words_list:
                logging.debug('[SPELL CHECKER] Found a word:{}'.format(word))
                score += 1
        return score * 100 / total

def build_dictionary(in_file):
    with open(in_file) as f:
        text = f.read()
        words = text.split()
        dic_file = open(dictionary_file, 'w')
        for word in words:
            dic_file.write(word.translate(DD)+' ')
        dic_file.close()

def build():
    build_dictionary("plain_text.txt")

def test_score(test_file):
    sc = SpellChecker(dictionary_file)
    with open(test_file) as f:
        logging.info('[SPELL CHECKER][TEST] Score for {} is {}'.format(
                test_file,
                sc.score(f.read())
                )
            )



if __name__ == '__main__':
    #test_score("encrypt_caesar.txt")
    test_score("plain_text.txt")
