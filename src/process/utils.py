import pandas as pd
from typing import Callable, Iterable, Literal
from praw.models import MoreComments
from praw.reddit import Submission

from src.praw_tools import get_date_from_submission
from src.praw_tools import (
    get_comments_from_submission,
)
from src.process.callbacks import (
    Base, 
    SentimentProcessor, 
    CommentProcessor
)


def submission_processor(submission: Submission, callbacks: Iterable[Base]):
    submission_id = submission.id
    date = get_date_from_submission(submission)

    for praw_comment in get_comments_from_submission(submission):
        if isinstance(praw_comment, MoreComments):
            continue

        for callback in callbacks:
            callback(
                date=date,
                submission_id=submission_id,
                comment_id=praw_comment.id,
                comment=praw_comment
            )

    return callbacks


def get_sentiment_and_comments_from_submission(
        submission: Submission,
        praw_comment_preprocesser: Callable[[str], str],
        sentiment_model: Callable[[str], tuple[Literal["positive", "neutral", "negative"], float]],
        phrase_finder: Callable[[str], Iterable[str]],
        add_summary_to_database: bool = False, 
        add_comments_to_database: bool = False, 
        root: str | None = None):

    if (add_comments_to_database or add_summary_to_database) and not root:
        raise Exception("root must be set")
    
    sentiment = SentimentProcessor(
        praw_comment_preprocesser=praw_comment_preprocesser, 
        sentiment_model=sentiment_model,
        phrase_finder=phrase_finder
    )
    comments = CommentProcessor()

    _ = submission_processor(submission, [sentiment, comments])

    if add_comments_to_database and root is not None:
        comments.comments.write(root)

    if add_summary_to_database and root is not None:
        sentiment.sentiment.write(root)

    return sentiment.sentiment, comments.comments


def table_sentiment_summariztion(
        table: str | pd.DataFrame,
        praw_comment_preprocesser: Callable[[str], str],
        sentiment_model: Callable[[str], tuple[Literal["positive", "neutral", "negative"], float]],
        phrase_finder: Callable[[str], Iterable[str]]):

    if isinstance(table, str):
        table = pd.read_csv(table, index_col=0)

    table["comment"] = table["comment"].map(praw_comment_preprocesser).map(lambda x: None if x == "" else x)
    table = table.dropna()
    table[["sentiment", "sentiment_score"]] = table["comment"].map(sentiment_model).apply(pd.Series)
    table["tickers_mentioned"] = table["comment"].map(phrase_finder)
    return table.drop(columns="comment")


if __name__ == "__main__": 
    from src.sentiment_models.models import get_twitter_roberta_base
    from src.text_processing import default_comment_processer
    
    model = get_twitter_roberta_base()
    
    def finder(string: str):
        ticks = ["gme", "amzn"]
        return_ticks = []
        for word in string.split(" "):
            if word in ticks:
                return_ticks.append(word)
        return ", ".join(list(set(return_ticks)))
    
    x = pd.DataFrame(
        {
            "com_ids": [
                "qe43", 
                "asdf", 
                "34532"
            ], 
            "comment": [
                "GME is the first and amzn sucks", 
                "hello there", 
                "this is shitty"
            ], 
        }
    )
    
    table_sentiment_summariztion(x, default_comment_processer(512), model, finder)