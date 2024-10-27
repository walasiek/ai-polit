from sentimentpl.models import SentimentPLModel
import torch
import logging


class SentimentModel:
    MIN_TXT_CHARACTERS = 20
    MIN_WORDS = 5

    def __init__(self, model_batch_size=128):
        self.device = 'cpu'
        if torch.cuda.is_available():
            self.device = 'cuda'

        self.model = None
        self.model_batch_size = model_batch_size

    def load_sentiment_model(self):
        logging.info("Loading sentiment model...")
        self.model = SentimentPLModel(from_pretrained='latest')
        self.model = self.model.to(self.device)

    def compute_sentiment(self, list_of_texts):
        all_batches = self._create_batches(list_of_texts)
        if len(list_of_texts) > 1:
            logging.info("Run model... Batches to process: %i", len(all_batches))

        result_sentiments = []
        for i, batch in enumerate(all_batches):
            if len(list_of_texts) > 1:
                logging.info("Run batch %i out of %i", i + 1, len(all_batches))
            model_input = []
            for entry in batch:
                model_input.append(entry)

            model_result = self.model(model_input)
            for i, mr_val in enumerate(model_result):
                val = mr_val.item()
                result_sentiments.append(val)
        return result_sentiments

    def _create_batches(self, list_of_texts):
        all_batches = []
        current_batch = []
        for entry in list_of_texts:
            current_batch.append(entry)
            if len(current_batch) >= self.model_batch_size:
                all_batches.append(current_batch)
                current_batch = []

        if len(current_batch) > 0:
            all_batches.append(current_batch)

        return all_batches
