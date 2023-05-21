import os
import re
import logging
import shutil
from tqdm import tqdm
from collections import OrderedDict
from sklearn.model_selection import train_test_split
import statistics

from aipolit.utils.globals import AIPOLIT_TWEET_GENERATORS_ROOT_DIR
from aipolit.utils.text import save_list_as_tsv, save_dict_as_tsv, read_tsv
from aipolit.models.text_generator import TextGenerator
from aipolit.models.sentiment_model import SentimentModel

# TODO do usuniecia
#from ttcrawler.dumped_tweets import DumpedTweets


def list_all_generated_models():
    all_model_names = []
    for filename in sorted(os.listdir(AIPOLIT_TWEET_GENERATORS_ROOT_DIR)):
        matched = re.match(r"^ttgen-(.*)$", filename)
        if matched:
            model_name = matched.group(1)
            all_model_names.append(model_name)
    return all_model_names


def print_all_available_models():
    print("Available models are:")
    for model_name in list_all_generated_models():
        print(f"  {model_name}")


class TweetGenerator:
    """
    Manages Tweet Generators for given User tweets.
    """
    TRAIN_FILENAME = 'train.tsv'
    TEST_FILENAME = 'test.tsv'
    TRAIN_SENTIMENT_FILENAME = 'train_sentiment.tsv'
    TEST_SENTIMENT_FILENAME = 'test_sentiment.tsv'
    MODEL_FILENAME = 'model-dump.pt'
    SCORES_FILENAME = 'evaluation-scores.tsv'

    def __init__(self, generator_name):
        self.generator_name = generator_name

        self.text_generator = TextGenerator()
        self.sentiment_model = SentimentModel()

    def get_dir(self):
        return os.path.join(AIPOLIT_TWEET_GENERATORS_ROOT_DIR, f"ttgen-{self.generator_name}")

    def get_filepath(self, filename):
        return os.path.join(self.get_dir(), filename)

    def train_new_generator(self, tweets_list, epochs=1, limit=None):
        """
        This will train new TweetGenerator and save it to disk
        if generator of the same name already exists then it will be removed.

        Params:
        tweets_list - array of tweets to finetune the model, can be empty
        limit - if set, then limits data to first N tweets
        """
        self._prepare_generator_dir()
        train, test = self._prepare_datasets(tweets_list, limit)

        self.text_generator.load_pretrained_model()

        scores = OrderedDict()
        scores['before'] = self.text_generator.evaluate(test)
        logging.info("Model score before training: %.4f", scores['before'])
        self.text_generator.train_on(train, epochs=epochs, eval_after_epoch=test)

        scores['after'] = self.text_generator.evaluate(test)
        logging.info("Model score after training: %.4f", scores['after'])

        save_dict_as_tsv(self.get_filepath(self.SCORES_FILENAME), scores)
        self.text_generator.save_model(self.get_filepath(self.MODEL_FILENAME))

    def load_generator(self):
        """
        This will load TweetGenerator from already trained model.
        """
        self.text_generator.load_model(self.get_filepath(self.MODEL_FILENAME))

    def load_sentiment_model(self):
        self.sentiment_model.load_sentiment_model()

    def generate_tweets(self, prompt, num_return_sequences=10):
        """
        Returns array of tweets generated using given prompt and parameters.
        """
        normalized_prompt = self._normalize_tweet_text(prompt)
        generated_tweets = self.text_generator.generate_text(
            normalized_prompt,
            num_return_sequences=num_return_sequences)
        return generated_tweets

    def generate_tweets_for_list(self, prompts, save_to_filename=None, with_sentiment=False, num_return_sequences=10):
        all_generated = []

        logging.info("Start generation of tweets for list of %i prompts", len(prompts))
        for i, prompt in enumerate(tqdm(prompts)):
            generated = self.generate_tweets(prompt, num_return_sequences=num_return_sequences)
            for generated_text in generated:
                sentiment = None
                if with_sentiment:
                    sentiment_result = self.sentiment_model.compute_sentiment([generated_text])
                    if sentiment_result:
                        sentiment = sentiment_result[0]

                entry = [i, prompt, generated_text, sentiment]
                all_generated.append(entry)
        if save_to_filename:
            logging.info("Saving generated tweets to file %s", self.get_filepath(save_to_filename))
            save_list_as_tsv(self.get_filepath(save_to_filename), all_generated, header=['prompt_id', 'prompt', 'text', 'sentiment'])
        return all_generated

    def evaluate_model(self, filepath=None):
        """
        Evaluates model on its test set.
        Can also give filepath to the tsv file to take evaluation texts
        """
        if filepath is None:
            filepath = self.get_filepath(self.TEST_FILENAME)

        raw_data = read_tsv(filepath)
        test = [x['text'] for x in raw_data]
        score = self.text_generator.evaluate(test)
        return score

    def compute_train_test_sentiment(self):
        self._compute_train_test_sentiment_on_file(self.get_filepath(self.TRAIN_FILENAME), self.get_filepath(self.TRAIN_SENTIMENT_FILENAME))
        self._compute_train_test_sentiment_on_file(self.get_filepath(self.TEST_FILENAME), self.get_filepath(self.TEST_SENTIMENT_FILENAME))

    def _prepare_generator_dir(self):
        gen_dir = self.get_dir()
        if os.path.isdir(gen_dir):
            logging.info("TweetGenerator[%s] dir [%s] already exists and will be removed!",
                             self.generator_name,
                             gen_dir)
            shutil.rmtree(gen_dir)

        logging.info("Create generator dir: %s", gen_dir)
        os.mkdir(gen_dir)

    def _prepare_datasets(self, tweets_list, limit):
        all_tweets = self._prepare_tweets_for_train(tweets_list, limit)

        test_size = self._compute_test_size(len(all_tweets))
        train_tweets = []
        test_tweets = []
        if test_size > 0:
            train_tweets, test_tweets = train_test_split(all_tweets, test_size=test_size)

        save_list_as_tsv(self.get_filepath(self.TRAIN_FILENAME), train_tweets, ['tweet_id', 'text'])
        save_list_as_tsv(self.get_filepath(self.TEST_FILENAME), test_tweets, ['tweet_id', 'text'])
        logging.info("We have %i tweets in train set and %i in test set", len(train_tweets), len(test_tweets))

        result_train = [x[1] for x in train_tweets]
        result_test = [x[1] for x in test_tweets]
        return result_train, result_test

    def _prepare_tweets_for_train(self, tweets_list, limit):
        all_tweets = []
        for entry in tweets_list:
            tt_id = entry['tweet_id']
            tt_raw_text = entry['text']
            tt_text = self._normalize_tweet_text(tt_raw_text)

            all_tweets.append([tt_id, tt_text])
            if limit:
                if len(all_tweets) >= limit :
                    return all_tweets
        return all_tweets

    def _compute_test_size(self, no_of_all_entries):
        if no_of_all_entries > 10000:
            return 1000
        else:
            return int(no_of_all_entries * 0.1)

    def _normalize_tweet_text(self, txt):
        # TODO to zrobić za pomocą preprocessorów
        #txt = txt.lower()
        txt = re.sub(r'https?:\/\/.*(\s|$)', ' ', txt, re.IGNORECASE)
        #txt = re.sub(r"[^!?:_.@#$&a-zA-ZąćęłńóśźżабвгдеёжзийклмнопрстуфхцчшщъыьэюяàãåèêìîñòøûāăěıŌōşţūàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿčœæĄĆĘŁŃÓŚŹŻАБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЭЮЯÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞßŸČŒÆ0-9'-]+", " ", txt)
        txt = re.sub(r"\s+", " ", txt)
        txt = re.sub("^\s+", "", txt)
        txt = re.sub("\s+$", "", txt)
        return txt

    def _compute_train_test_sentiment_on_file(self, input_tsv_fp, output_tsv_fp):
        raw_data = read_tsv(input_tsv_fp)
        list_of_texts = [x['text'] for x in raw_data]
        list_of_ids = [x['tweet_id'] for x in raw_data]

        logging.info("Need to compute sentiment for %i tweets from %s", len(list_of_texts), input_tsv_fp)
        result_sentiments = self.sentiment_model.compute_sentiment(list_of_texts)

        data_to_save = []
        for sentiment, tweet_id in zip(result_sentiments, list_of_ids):
            data_to_save.append([tweet_id, str(sentiment)])

        logging.info("Average sentiment: %.4f", statistics.mean(result_sentiments))
        logging.info("Save sentiment scores to: %s", output_tsv_fp)
        save_list_as_tsv(output_tsv_fp, data_to_save, header=['tweet_id', 'sentiment'])
