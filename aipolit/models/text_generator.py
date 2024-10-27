import logging
import os
import torch
import math
import statistics
import numpy as np
import re
from transformers import AutoTokenizer, AutoModelWithLMHead
from torch.utils.data import Dataset, DataLoader
from transformers import AdamW, get_cosine_with_hard_restarts_schedule_with_warmup


END_OF_TEXT_TOKEN = '<|endoftext|>'


class ListDataset(Dataset):
    def __init__(self, list_of_texts):
        super().__init__()
        self.list_of_texts = [x + ' ' + END_OF_TEXT_TOKEN for x in list_of_texts]

    def __len__(self):
        return len(self.list_of_texts)

    def __getitem__(self, item):
        return self.list_of_texts[item]


class TextGenerator:
    """
    Generative model using PapuGaPT-2
    Allows to:
    - retrain PapuGaPT-2 on the given set
    - save model to the given file
    - load model from the given file
    - evaluate model using perplexity
    - generate text with seed text

    References:
    - base code from: https://github.com/prakhar21/TextAugmentation-GPT2/blob/master/train.py
    - PapuGaPT-2: https://huggingface.co/dkleczek/papuGaPT2
    """

    LEARNING_RATE = 3e-5
    WARMUP_STEPS = 300

    def __init__(self, model_name='flax-community/papuGaPT2'):
        self.batch_size = 64

        self.shuffle_data = True
        self.device = 'cpu'
        if torch.cuda.is_available():
            self.device = 'cuda'

        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.optimizer = None
        self.scheduler = None

    def train_on(self, list_of_texts, epochs=1, eval_after_epoch=None):
        if len(list_of_texts) == 0:
            logging.info("Training omitted... no data provided for training")
            return

        self._prepare_training()

        batch_counter = 0
        data_loader = self._create_data_loader(list_of_texts)

        for epoch in range(epochs):
            logging.info('Start epoch no: %i', epoch + 1)
            total_loss_in_batch = 0.0

            for idx, txt in enumerate(data_loader):
                txt = torch.tensor(self.tokenizer.encode(txt[0]))
                txt = txt.unsqueeze(0).to(self.device)
                outputs = self.model(txt, labels=txt)
                loss, _ = outputs[:2]
                loss.backward()
                total_loss_in_batch += float(loss.data)

                if ((idx + 1) % self.batch_size == 0):
                    if batch_counter % 10 == 0:
                        logging.info(
                            "Epoch: %i / %i | batch_counter: %i | processed data: %i / %i | loss in current batch: %.4f",
                            epoch + 1,
                            epochs,
                            batch_counter + 1,
                            idx + 1,
                            len(data_loader),
                            total_loss_in_batch
                        )

                    batch_counter += 1
                    self.optimizer.step()
                    self.scheduler.step()
                    self.optimizer.zero_grad()
                    self.model.zero_grad()
                    total_loss_in_batch = 0.0
            logging.info('Finished epoch no: %i', epoch + 1)
            if eval_after_epoch:
                epoch_score = self.evaluate(eval_after_epoch)
                logging.info(
                    "-- epoch %i / %i evaluation score: %.4f",
                    epoch + 1,
                    epochs,
                    epoch_score)

        logging.info("Training finished!")

    def evaluate(self, list_of_texts, dont_add_end_token=False):
        """
        We evaluate model using average peplexity of the sentences on input
        Perplexity is computed as exp of the loss for the sentence on input
        reference: https://www.reddit.com/r/LanguageTechnology/comments/bucn53/perplexity_score_of_gpt2/
        """
        if len(list_of_texts) == 0:
            return 0.0

        all_perplexities = [self.compute_perplexity(t, dont_add_end_token) for t in list_of_texts]
        perplexity = statistics.mean(all_perplexities)
        return perplexity

    def compute_perplexity(self, sentence, dont_add_end_token=False):
        if len(sentence) < 5:
            return 1.0

        if not dont_add_end_token:
            sentence = sentence + ' ' + END_OF_TEXT_TOKEN

        tokenize_input = self.tokenizer.tokenize(sentence)

        tensor_input = torch.tensor([self.tokenizer.convert_tokens_to_ids(tokenize_input)])
        tensor_input = tensor_input.to(self.device)
        result = self.model(tensor_input, labels=tensor_input)
        loss = result.loss
        result = math.exp(loss)

        if result > 10000:
            return 10000.0
        return result

    def save_model(self, filepath):
        logging.info("Save model to: %s", filepath)
        torch.save(self.model.state_dict(), filepath)

    def load_model(self, filepath):
        self.load_pretrained_model()
        self.model.load_state_dict(torch.load(filepath))

    def load_pretrained_model(self):
        logging.info("Loading pretrained model: %s", self.model_name)
        logging.info("-- loading model")
        model = AutoModelWithLMHead.from_pretrained(self.model_name)
        self.model = model.to(self.device)
        logging.info("-- loading tokenizer")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        logging.info("Pretrained model loaded.")

    def generate_text(self, prompt, max_length=30, early_stopping=True, num_return_sequences=10):
        """
        Returns list of generated texts using given prompt.
        """
        result = []
        with torch.no_grad():
            for i in range(num_return_sequences):
                finished = False
                cur_ids = torch.tensor(self.tokenizer.encode(prompt)).unsqueeze(0).to(self.device)

                for i in range(max_length):
                    outputs = self.model(cur_ids, labels=cur_ids)
                    loss, logits = outputs[:2]

                    softmax_logits = torch.softmax(logits[0,-1], dim=0)

                    next_token_id = self.choose_from_top_k_top_n(softmax_logits.to('cpu').numpy()) # top-k-top-n sampling
                    cur_ids = torch.cat([cur_ids, torch.ones((1,1)).long().to(self.device) * next_token_id], dim = 1)

                    if next_token_id in self.tokenizer.encode(END_OF_TEXT_TOKEN):
                        finished = True
                        break

                output_list = list(cur_ids.squeeze().to('cpu').numpy())
                output_text = self.tokenizer.decode(output_list)
                output_text = output_text.replace(END_OF_TEXT_TOKEN, '')
                output_text = re.sub(r"\s+", " ", output_text)
                output_text = re.sub(r"^\s+", "", output_text)
                output_text = re.sub(r"\s+$", "", output_text)
                result.append(output_text)

        return result

    def choose_from_top_k_top_n(self, probs, k=50, p=0.8):
        ind = np.argpartition(probs, -k)[-k:]
        top_prob = probs[ind]
        top_prob = {i: top_prob[idx] for idx,i in enumerate(ind)}
        sorted_top_prob = {k: v for k, v in sorted(top_prob.items(), key=lambda item: item[1], reverse=True)}

        t = 0
        f = []
        pr = []
        for k,v in sorted_top_prob.items():
            t += v
            f.append(k)
            pr.append(v)
            if t >= p:
                break

        top_prob = pr / np.sum(pr)
        token_id = np.random.choice(f, 1, p = top_prob)

        return int(token_id)

    def _prepare_training(self):
        logging.info("-- loading optimizer")
        self.optimizer = AdamW(self.model.parameters(), lr=self.LEARNING_RATE)
        logging.info("-- loading scheduler")
        self.scheduler = get_cosine_with_hard_restarts_schedule_with_warmup(
            self.optimizer,
            num_warmup_steps=self.WARMUP_STEPS,
            num_training_steps=-1)

    def _create_data_loader(self, list_of_texts):
        dataset = ListDataset(list_of_texts)
        data_loader = DataLoader(dataset, batch_size=1, shuffle=self.shuffle_data)
        return data_loader
