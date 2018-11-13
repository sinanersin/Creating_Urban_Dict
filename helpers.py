import json
from datetime import datetime, date, timedelta

def create_stream_from_files(files, textprocessor, time_delta=12,
                             minimum_words=20, **kwargs):
    """
    files: list of filepaths to extract text from. Needs to be in list, even
           when only one file given. Should be files in the same format as the
           ones provided in de dataset.
    textprocessor: an instance of the class TextProcessor.
    batch_size: number of comments retrieved before moving forward to the model.
                Because this function yields a list to the model, whenever the
                model asks for a new batch (due to a forloop), this function is
                proceeded again.
                Find some more information about yield here:
        https://pythontips.com/2013/09/29/the-python-yield-keyword-explained/
    minimum_words: minimum words in a comment after preprocessing before this
                   comment is actually added to the batch

    **kwargs are arguments passed to clean_text function. If no extra arguments,
    default is taken in clean_text. Pass arguments for clean_text by calling
    create_stream_from_files and after batch_size and minimum_words, add more
    arguments in the form key=value. If key matches argument from clean_text,
    it is used. I implemented this, but then never used it. But can maybe be
    usefull for extracting only known words at initialization of a model.
    (see model TODO for that)

    yield: list of comments. Comments being a list of words.
    """

    # Setup variables, mostly used for printing updates of the progress
    #TODO: make nice updates of the progress... Now it is still a bit messy...
    batch = []
    starting_line = True

    # Iterate over the input files until caller (the model in our case) stops
    # asking for a new batch
    for file_number, fle in enumerate(files):

        # Open file and read line by line. Each line contains a json object.
        # Each json object consists of a body and the utc time the comment
        # was created.
        with open(fle, 'r') as inpt:
            for line in inpt:

                text = json.loads(line)

                # Filter out comments of the Reddit bot (saying that you can't
                # spam or whatever...)
                if '*[I am a bot]' in text['body']:
                    continue

                # Send text of a comment to the preprocessor
                date = datetime.fromtimestamp(text['created_utc'])

                if starting_line:
                    current_date = date
                    batch = {'date': current_date.strftime('%Y-%m-%d %H:%M'), 'comments': []}
                    starting_line = False

                text = textprocessor.clean_text(text['body'])


                # Append comment text to the batch if it has the minimum
                # required number of words
                if date - current_date < timedelta(hours=time_delta):
                    if len(text) >= minimum_words:
                        batch['comments'].append(text)

                else:
                    current_date = date
                    yield batch
                    batch = {'date': current_date.strftime('%Y-%m-%d %H:%M'), 'comments': [text]}

    # And yield last batch, which isn't the size of batch_size because there
    # are no more comments in the files given
    if len(batch) > 0:
        yield batch
