from nltk.tokenize import word_tokenize, RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.stem import WordNetLemmatizer
import re

class TextProcessor:
    """
    Basic class for processing text. Make sure to always process text with the
    same processor before feeding it to a model.
    """
    def __init__(self):
        """
        Set basic preprocessing rules so the same preprocessing is done when
        an instance of this class is used.
        """
        #self.stem_words = stem_words
        #self.remove_stopwords = remove_stopwords
        # RegexpTokenizer could be used as tokenizer, or we write our own.
        # RegexpTokenizer has some flaws which could be bad for our model.
        self.tokenizer = RegexpTokenizer(r'\b[a-zA-Z0-9$\-_&\.#]+\b')
        self.stopwords = set(stopwords.words('english'))
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()

    def clean_text(self, text):
        """
        text: string of text
        output: list of lowercase words
        """
        #TODO: Optimize preprocessing. What characters to leave in string, what
        # to remove? As long as the input and output format of this function
        # don't change.

        # Remove urls and only keep alphabatical characters and numbers
        # Transform to array of words
        text = self.remove_urls(text)
        tokenized_words = self.tokenize(text)
        # words = self.lemmatize_words(tokenized_words)

        #if self.remove_stopwords:
            #words = self.remove_stopwords(words)

        #if self.stem_words:
            #words = self.stem_words

        return tokenized_words

    def remove_urls(self, text):
        """
        text: string of text
        output: string of text
        """
        # old search for replacing urls, didn't seem to work well
        # return re.sub(r'(https?:\/\/)?([\da-z\.-]+)\.([a-z\.])\S*', '', text)
        text = re.sub('http(\S)*', '', text)
        text = re.sub('www.(\S)*', '', text)
        return text

    def tokenize(self, text):
        """
        text: string of text
        output: array of words
        """
        lemmatizer = WordNetLemmatizer()

        # First regex is to keep abbreviations together
        # Second te remove numbers not surrounded by text
        text = re.sub(r'[,\/\'\(\)\.\n\t\r\^\[\]!"]', '', text)
        text = re.sub(r'[0-9]+', '#', text)
        text = re.sub(r'[-]+','-',text) #replace multiple dashes or spaces
        text = text.rstrip()
        words = []
        for word in self.tokenizer.tokenize(text):
            word = word.lower()
            try:
                words.append(lemmatizer.lemmatize(word))
            except RecursionError:
                words.append(word)


        return words
        # return [word.lower() for word in self.tokenizer.tokenize(text)]

    def remove_stopwords(self, words):
        """
        words: array of words
        output: array of words
        """
        return [word for word in words if word not in self.stopwords]

    def stem_words(self, words):
        """
        words: array of words
        output: array of words
        """
        stemmer = PorterStemmer()
        stemmed_words = []
        for word in words:
            # Try to stem except with error, then just add word
            try:
                stemmed_words.append(stemmer.stem(word))
            except RecursionError:
                stemmed_words.append(word)

        return stemmed_words

    def lemmatize_words(self, words):
        """
        words: array of words
        output: array of words
        """
        lemmatizer = WordNetLemmatizer()
        lemmatized_words = []
        for word in words:
            # Try to lemmatize except with error, then just add word
            try:
                lemmatized_words.append(lemmatizer.lemmatize(word))
            except RecursionError:
                lemmatized_words.append(word)

        return lemmatized_words
