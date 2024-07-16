# -*- coding: utf-8 -*-
import fire
from transformers import pipeline

#from src.utils.util_log import log, loge
from utilmy import log, loge


##############################################################################
def check_output_pipeline(expected_output, output):
    for tag in ["positive", "negative", "neutral"]:
        assert tag in output, f"sentiment pipeline didn't return tag {tag}"
        score = output[tag]
        expected_score = expected_output[tag]
        assert abs(score - expected_score) < 1e-3, "model return un-expected score"
    return True


def test_sentiment():
    model = Sentiment(modeluri="finiteautomata/bertweet-base-sentiment-analysis")
    model.load_model()

    output = model.get_sentiment("I love you so much!")
    expected_output = {
        "positive": 0.991788923740387,
        "negative": 0.003384605050086975,
        "neutral": 0.004826517775654793,
    }
    check_output_pipeline(expected_output, output)

    output = model.get_sentiment("You're so fat !!!")
    expected_output = {
        "positive": 0.005917856935411692,
        "negative": 0.9718080163002014,
        "neutral": 0.022274119779467583,
    }
    check_output_pipeline(expected_output, output)

    output = model.get_sentiment("This is my family")
    expected_output = {
        "positive": 0.02613108977675438,
        "negative": 0.05181219428777695,
        "neutral": 0.9220566749572754,
    }
    check_output_pipeline(expected_output, output)

    print("pass all tests")


###########################################################################
class Sentiment:

    def __init__(self, modeluri="finiteautomata/bertweet-base-sentiment-analysis"):
        self.model = None
        self.modeluri = modeluri

    def load_model(self, modeluri=None):
        modeluri2 = modeluri if isinstance(modeluri, str) else self.modeluri

        ### TOOD : load from DataLake
        self.model = pipeline(model=modeluri2, return_all_scores=True, task="sentiment-analysis")

    def preprocess_text(self, text: str):
        """Preprocesses given text by converting it to lowercase.
        Args:
            text (str): text to be preprocessed.

        Returns:
            str: preprocessed text.
        """
        text = text.lower()
        return text

    def get_sentiment(self, text: str):
        """Get sentiment analysis of a given text.
        Args:
            text (str): input text to analyze.

        Returns:
            dict: A dictionary containing sentiment scores for each tag.
                  tags are "negative", "positive", and "neutral".
                  scores range from 0 to 1, where 1 indicates a positive sentiment and 0 indicates a negative sentiment.
        """
        text = self.preprocess_text(text)
        sentiment = self.model(text)[0]

        output = {}
        for tag_output in sentiment:
            tag = tag_output["label"]
            if tag == "NEG":
                tag = "negative"
            elif tag == "POS":
                tag = "positive"
            else:
                tag = "neutral"

            output[tag] = tag_output["score"]
        return output


if __name__ == "__main__":
    fire.Fire()
