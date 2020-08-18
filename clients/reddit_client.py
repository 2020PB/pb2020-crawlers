from datadog import statsd
from praw import Reddit
from praw.models import Submission
import requests
from typing import Generator, List

from common.config import (
    REDDIT_USER,
    REDDIT_CLIENT_ID,
    REDDIT_SECRET,
    REDDIT_USER_AGENT,
    REDDIT_DUMMY_REDIRECT,
    SUBREDDITS,
)


def make_new_reddit_client() -> Reddit:
    return Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_SECRET,
        redirect_uri=REDDIT_DUMMY_REDIRECT,
        user_agent=REDDIT_USER_AGENT,
    )


def stream_posts(reddit_client: Reddit, subreddits: List[str], job_mode: str) -> Generator[Submission, None, None]:
    for submission in reddit_client.subreddit("+".join(SUBREDDITS)).stream.submissions():
        statsd.increment(
            f"reddit.read_post", 1, tags=[f"job_mode:{job_mode}", f"query:{submission.subreddit.display_name}"]
        )
        yield submission
