import pytest
from aipolit.ttgenerators.tweet_generator import TweetGenerator


def test_train_and_run_empty_model():
    model_name = 'test-empty-model'
    gen = TweetGenerator(model_name)
    gen.train_new_generator([])

    sample_prompt = "To jest przykładowe zdanie"
    generated_count = 10

    generated = gen.generate_tweets(sample_prompt, num_return_sequences=generated_count)

    assert len(generated) == generated_count
    for sentence in generated:
        assert sentence.startswith(sample_prompt)
