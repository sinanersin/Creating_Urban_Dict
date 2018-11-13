from gensim.models import Word2Vec
import os

class Model:
    """
    Basic class for the Word2Vec model.
    The original gensim Word2Vec class will be stored in self.model.
    """
    def initialize(self, stream, min_count=10, iterations=10, dictionary=None):
        #TODO: make iterations go on forever. (iterations=None, or somehting?)
        #TODO: add more parameters which can be given to to Word2Vec initialization
        # for optimization
        """
        stream: list of text, text being a list of words. Can be a single list
                of text, but mainly a stream of lists.
        min_count: minimal occurence of a word in list of text before its
                   taken in the model.
        iterations: stream can be made definite by setting the iterations. Use
                    high iterations to make sure all comments from file are read

        Initializes the Word2Vec model. However, even in the initalization the
        online training method is already used. If you want to really initalize
        on a bigger set of comments, increase the batch_size of the stream.
        """
        # Instantiate Word2Vec model from gensim
        self.model = Word2Vec(min_count=min_count, workers=2)
        # print(len(list(stream)))
        # Call for first batch in stream to initialize model
        for batch in stream:
            batch = batch['comments']
            if dictionary:
                batch = [[word for word in sentence if dictionary.check_word(word)] for sentence in batch]
            self.build_vocab(batch)
            self.train(batch)
            break

        # Then start online training with 1 iteration less
        if iterations > 1:
            self.update(stream, iterations=iterations-1, dictionary=dictionary)

    def train(self, batch):
        """
        batch: list of comments. Comment being a list of words.
        """
        total_examples = self.model.corpus_count + len(batch)
        epochs = self.model.iter
        self.model.train(batch, total_examples=total_examples, epochs=epochs)

    def build_vocab(self, batch, update=False):
        """
        batch: list of comments. Comment being a list of words.
        update: if new words in comments, update should be set to true
        """
        self.model.build_vocab(batch, update=update)

    def update(self, stream, iterations=10, dictionary=None):
        """
        stream: list of text, text being a list of words. Can be a single list
                of text, but mainly a stream of lists.
        iterations: number of batches to be processed. Set very high number to
                    go on (almost) indefinitely. (see TODO from initialization)
        """
        # Ask stream for a new batch every iteration of the forloop.
        # Keep track of number of batches retrieved to stop when iterations
        # is reached.
        for itr, batch in enumerate(stream):
            batch = batch['comments']
            if dictionary:
                batch = [[word for word in sentence if dictionary.check_word(word)] for sentence in batch]
            self.build_vocab(batch, update=True)
            self.train(batch)
            if itr >= iterations - 1:
                break

    def unknown_words(self, dictionary, min_occurence=100):
        """
        dictionary: instance of class Dictionary
        min_occurence: minimum number of occurences in the Gensim Word2Vec model
                       before taken as unknown word.

        return: list of words

        This function iterates over all words in the Gensim Word2Vec model and
        adds it to the output if it occurs in the given dictionary.
        """
        not_words = []

        for word in self.model.wv.vocab:
            if not dictionary.check_word(word):
                if self.model.wv.vocab[word].count > min_occurence:
                    not_words.append(word)
        return not_words

    def save(self, dir_path):
        """
        dir_path: the folder where you want to save the model

        Saves a model in its own folder
        """
        #TODO: maybe also save textProcessor to ensure always the same
        # preprocessing is done? In this case the textProcessor should also
        # be set as class variable on initialization
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)
        self.model.save(dir_path + '/model')

    def load(self, dir_path):
        """
        dir_path: folder where the model is saved

        Loads the model
        """
        self.model = Word2Vec.load(dir_path + '/model')
