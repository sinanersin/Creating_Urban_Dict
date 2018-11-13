from copy import deepcopy
import json
import os
import time
from datetime import timedelta, datetime
from dictionary import Dictionary, UrbanDict

def pipeline(stream, model, dictionary, minimum_word_occurence=100, meaning_score_treshold=0.6, time_delta=12, time_frames=7):
    print('starting model {}'.format(model.model))
    updating_model = deepcopy(model)
    to_update = []

    start = datetime.now()
    for batch in stream:
        print('\n\nUpdating model, {}\n'.format(batch['date']))
        str_date = str(batch['date'])

        lookup_datebase_start = datetime.now()
        files = os.listdir('../Database')
        print('number of files', len(files))
        if len(files) >= (time_frames - 1):
            print('updating from past')
            updating_model = deepcopy(model)

            for fle in files:
                with open('../Database/' + fle, 'r') as inpt:
                    old_batch = json.load(inpt)
                    updating_model.update([old_batch])
        lookup_database_end = datetime.now()
        print('{} lookup database'.format(lookup_database_end - lookup_datebase_start))

        updating_start = datetime.now()
        updating_model.update([batch])
        updating_end = datetime.now()
        print('{} updating on new batch'.format(updating_end - updating_start))

        updating_model.save('../Models/' + str_date)

        with open('../Database/' + str_date + '.json', 'w') as outpt:
            json.dump(batch, outpt)

        remove_date = datetime.strptime(batch['date'], '%Y-%m-%d %H:%M') - timedelta(hours=((time_frames - 1) * time_delta))
        remove_file = remove_date.strftime('%Y-%m-%d %H:%M') + '.json'

        try:
            os.remove('../Database/' + remove_file)
        except OSError:
            pass

        define_urbandict_start = datetime.now()
        # Setup Urban Dictionary
        # First get words in model that are unknown by the dictionary
        unknown = updating_model.unknown_words(dictionary, min_occurence=minimum_word_occurence)

        # Create and fill Urban Dictionary
        urban = UrbanDict()
        urban.fill_dict(updating_model, unknown, topn=1000, treshold=meaning_score_treshold)

        # Filter Urban Dict to only keep meanings known by the original dictionary
        urban.filter_on_dict(dictionary)

        define_urbandict_end = datetime.now()
        print('{} define urbandict'.format(define_urbandict_end - define_urbandict_start))

        with open('../Urban_Dicts/' + str_date, 'w') as outpt:
            json.dump(urban.words, outpt, indent='\t')

    print('{} entire process'.format(datetime.now() - start))

if __name__ == '__main__':
    from model import Model
    from dictionary import Dictionary, UrbanDict
    from textprocessor import TextProcessor
    from communicator import Communicator
    import helpers
    from pprint import pprint
    import nltk

    init_stream_files = ['../Data/01-01.txt', '../Data/01-02.txt', '../Data/01-03.txt', '../Data/01-04.txt', '../Data/01-05.txt', '../Data/01-06.txt',
                         '../Data/01-07.txt', '../Data/01-08.txt', '../Data/01-09.txt', '../Data/01-10.txt', '../Data/01-11.txt', '../Data/01-12.txt',
                         '../Data/01-13.txt', '../Data/01-14.txt']
    update_stream_files = ['../Data/01-15.txt', '../Data/01-16.txt', '../Data/01-17.txt', '../Data/01-18.txt', '../Data/01-19.txt', '../Data/01-20.txt',
                           '../Data/01-21.txt','../Data/01-22.txt', '../Data/01-23.txt', '../Data/01-24.txt', '../Data/01-25.txt', '../Data/01-26.txt',
                           '../Data/01-27.txt', '../Data/01-28.txt', '../Data/01-29.txt', '../Data/01-30.txt', '../Data/01-31.txt']

    dictionary_file = 'data/words.txt'
    models_dir = '../Models/'
    minimum_words_in_comments = 20
    minimum_word_count = 100
    time_delta = 24
    time_frames = 7

    # Create instances of classes
    model = Model()
    textProcessor = TextProcessor()
    dictionary = Dictionary()

    # Or initialize model with stream from the dataset
    stream = helpers.create_stream_from_files(init_stream_files, textProcessor, time_delta=time_delta, minimum_words=minimum_words_in_comments)
    model.initialize(stream, min_count=minimum_word_count, iterations=99999999, dictionary=dictionary)
    initialization_end = datetime.now()
    model.load('../Models/Init')

    print('{} created the initialization model. Here is the summary\n{}'.format((initialization_end - initialization_start), model.model))

    model.save('../Models/Init')

    unknown = model.unknown_words(dictionary, min_occurence=1)
    print('If {} is 0, then initalization worked well'.format(unknown))

    stream = helpers.create_stream_from_files(update_stream_files, textProcessor, time_delta=time_delta, minimum_words=minimum_words_in_comments)
    pipeline(stream, model, dictionary, minimum_word_occurence=minimum_word_count, time_delta=time_delta, time_frames=time_frames)
