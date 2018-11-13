class Dictionary:
    """
    Basic class for a dictionary. This basic class is used for the dictionary
    of English words.
    """
    def __init__(self):
        self.words = {}

    def fill_dict_from_txt(self, input_file, textprocessor):
        """
        input_file: a .txt file containing a word on each single line
        textprocessor: in instance of the class TextProcessor. Make sure this is
                       the same as the one used for building a model.

        Fills the dictionary of this class. Dictionary can be accessed via
        self.words.
        """
        with open(input_file, 'r') as inpt:
            for line in inpt:
                # line[:-1] is used because enters appear at the end of the line
                #TODO: read in .txt file properly so [:-1] does not have to be used
                word = textprocessor.clean_text(line[:-1])
                if len(word) > 0:
                    self.add_word(word[0])

    def add_word(self, word):
        """
        word: string

        Add word to the dictionary. Can be accessed via self.words.
        """
        self.words[word] = None

    def remove_word(self, word):
        """
        word: string

        Remove word from the dictionary.
        """
        self.words.pop(word, None)

    def check_word(self, word):
        """
        word: string

        return: boolean

        Check if word exists in the dictionary.
        """
        try:
            x = self.words[word]
            return True
        except KeyError:
            return False

class UrbanDict(Dictionary):
    """
    Advanced class for the Urban Dictionary. Inherits functions from basic
    dictionary class.
    """
    def fill_dict(self, model, words, topn=10, treshold=0.6):
        """
        model: instance of the class Model. Should be initialized first.
        words: list of words. Contains words that should be explained by the
               urban dictionary.
        topn: number of how many explanatory words are allowed
        treshold: float how close the explanatory words and the word to be
                  explained should at least be before explanatory word is added

        Fills the urban dictionary with words given. Adds to each word a dict of
        tuples. Each tuple contains an explanatory word and its similarity score
        to the word to be explained.

        Structure: {'word': [(explained, similarity), etc], 'word': etc}
        """
        # Loop over given words and add to dictionary
        for word in words:
            self.add_word(word)

            # Retrieve similar words and their similarity score
            similar_words = model.model.wv.most_similar(positive=word, topn=topn)

            # Add explanatory word if score is bigger then treshold
            for meaning in similar_words:
                if meaning[1] >= treshold:
                    self.add_meaning(word, meaning)

            # If no explanatory words have a bigger score then treshold, then
            # remove word to be explained from dictionary
            if len(self.words[word]) == 0:
                self.remove_word(word)

    def add_word(self, word):
        """
        word: string

        Add word to dictionary
        """
        self.words[word] = []

    def add_meaning(self, word, meaning):
        """
        word: string
        meaning: tuple with explanatory word and similarity score (expl, score)

        Add meaning to the word to be explained
        """
        self.words[word].append(meaning)

    def remove_meaning(self, word, meaning):
        """
        word: string
        meaning: tuple with explanatory word and similarity score (expl, score)
                 Make sure tuple does exactly exists in meanings word, else
                 an error will occur.

        Remove a meaning from a word to be explained in the dictionary
        """
        #TODO: make sure function doesn't give error when meaning doesn't exists
        self.words[word].remove(meaning)

    def filter_on_dict(self, dictionary):
        """
        dictionary: instance of class Dictionary

        Removes all meaning from the dictionary that are not known by the given
        dictionary. Resulting dictionary can be accessed through self.words.

        Keep in mind that this function overrides the existing dictionary this
        functions is called upon.
        """
        # Iterate over all words in urban dict. Store all meanings that are not
        # known by the given dictionary
        for word in self.words.keys():
            unknown_items = [item for item in self.words[word]
                                  if not dictionary.check_word(item[0])]

            # Remove all unknown meanings from the current word
            for item in unknown_items:
                self.remove_meaning(word, item)

        # Store all words that don't have a meaning anymore
        empty_words = [word for word in self.words.keys()
                            if len(self.words[word]) == 0]

        # Remove all words from the urban dict that don't have a meaning anymore
        for word in empty_words:
            self.remove_word(word)

    def topn_words(self, topn=10):
        """
        topn: number of meanings per word

        return: part of the urban dict (self.words)

        Return part of the urban dict with all words having only their topn meanings
        """
        output = {}
        for word, meaning in self.words.items():
            output[word] = meaning[:topn]
        return output
