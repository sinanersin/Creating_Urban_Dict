import praw

class Communicator:
    """
    Basic class to communicate with the Reddit API
    """
    def __init__(self):
        """
        Initialize authentication settings
        """
        self.client_id = 'TPOJZUicpXGY4A'
        self.client_secret = '8l_joBY9v1XoTDjOOVEdr7_FKyY'
        self.user_agent = 'PizzaPlace'

    def authenticate(self):
        """
        Authenticate communicator. Needed to communicate with the API.
        """
        self.auth = praw.Reddit(client_id=self.client_id,
                                client_secret=self.client_secret,
                                user_agent=self.user_agent)

    def stream_comments(self, textprocessor, subreddit='all', batch_size=1000,
                              minimum_words=20):
        """
        textprocessor: an instance of the class TextProcessor.
        subreddit: which subreddit to use. Only one subreddit per stream possible.
                   Other subreddits then 'all' might not yield enough responses.
                   For subreddit 'all' about 1000 responses per minute.
        batch_size: number of comments retrieved before moving forward to the model.
                    Because this function yields a list to the model, whenever the
                    model asks for a new batch (due to a forloop), this function is
                    proceeded again.
                    Find some more information about yield here:
            https://pythontips.com/2013/09/29/the-python-yield-keyword-explained/
        minimum_words: minimum words in a comment after preprocessing before this
                       comment is actually added to the batch

        yield: list of comments. Comments being a list of words.
        """
        # Connect to the subreddits comment stream, yields comments
        stream = self.auth.subreddit(subreddit).stream.comments()
        batch = []

        # Iterate over yielded comments
        for comment in stream:

            # Extract text from comment, add to batch if required number of words
            text = textprocessor.clean_text(comment.body)
            if len(text) >= minimum_words:
                batch.append(text)

            # Yield and empty batch if number of comments exceeds batch_size
            if len(batch) >= batch_size:
                yield batch
                batch = []
