from src.engine.nlp.sentiment import Sentiment


def check_output_pipeline(expected_output, output):
    for tag in ["positive", "negative", "neutral"]:
        assert tag in output, f"sentiment pipeline didn't return tag {tag}"
        score = output[tag]
        expected_score = expected_output[tag]
        assert abs(score - expected_score) < 1e-3, f"model return un-expected score"
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
