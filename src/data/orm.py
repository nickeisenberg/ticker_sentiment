import os
import pandas as pd
from typing import Callable, Iterable, Literal

from src.orm.base import Row, Table


def common_write(table: pd.DataFrame, root: str, overwrite: bool = False):
    columns = table.columns
    if not "submission_id" in columns and not "date" in columns:
        raise Exception("submission_id and date are not in the columns of summary")
    submission_id = table["submission_id"].values[0]
    date_str = table["date"].values[0]
    save_csv_to = os.path.join(root, f"{date_str}_{submission_id}.csv")
    if not overwrite and os.path.isfile(save_csv_to):
        raise Exception(f"{save_csv_to} exists")
    table.to_csv(save_csv_to)


class SentimentRow(Row):
    def __init__(self, submission_id: str, comment_id: str, date: str, 
                 sentiment: Literal["positive", "negative", "neutral"], 
                 sentiment_score: float, 
                 tickers_mentioned: Iterable[str]):
        self.submission_id = submission_id
        self.comment_id = comment_id
        self.date = date
        self.sentiment = sentiment
        self.sentiment_score = sentiment_score
        self.tickers_mentioned = ", ".join(tickers_mentioned) if tickers_mentioned else "N/A"
    
    @property
    def row_dict(self):
        return {
            "submission_id": self.submission_id,
            "comment_id": self.comment_id,
            "date": self.date,
            "sentiment": self.sentiment,
            "sentiment_score": self.sentiment_score,
            "tickers_mentioned": self.tickers_mentioned 
        }
    

class Sentiment(Table):
    @property
    def new_row(self):
        return SentimentRow

    def write(self, root: str, overwrite: bool = False):
        common_write(self.table, root, overwrite)


class CommentsRow(Row):
    def __init__(self, date: str, submission_id: str, comment_id: str,
                 comment: str):
        self.date = date 
        self.submission_id = submission_id 
        self.comment_id = comment_id
        self.comment = comment

    @property
    def row_dict(self):
        return {
            "submission_id": self.submission_id,
            "comment_id": self.comment_id,
            "date": self.date,
            "comment": self.comment 
        }


class Comments(Table):
    @property
    def new_row(self):
        return CommentsRow

    def write(self, root: str, overwrite: bool = False):
        common_write(self.table, root, overwrite)


if __name__ == "__main__":
    coms = Comments()
    row0 = coms.new_row("2024-01-01", "00a1", "00b1", "hello there")
    coms.add_row(row0)
    row1 = coms.new_row("2024-01-02", "00a2", "00b2", "another comment")
    coms.add_row(row1)
    print(coms.table)