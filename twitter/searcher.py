from datadog import statsd
from datetime import datetime
import json
import logging
import tweepy
from typing import Dict, List, Any, Set, Tuple


# from boto3 import client as boto_client

from common.data_classes import RawSubmission
from common.enums import DataSource

from clients.laravel_client import bulk_upload_submissions
from common.config import (
    TWITTER_LAST_RUN_FILENAME,
    # TWITTER_LAST_RUN_BUCKET,
    TWITTER_LARAVEL_API_KEY,
    TWITTER_CONSUMER_KEY,
    TWITTER_CONSUMER_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET,
    READER_MODE,
)


logger = logging.getLogger(__name__)


def run_twitter_searches(since_id: int, queries: List[str], job_mode: str) -> int:
    if not since_id:
        since_id = get_since_id_from_file()
    api = build_tweepy_api()
    total_returned_tweets = 0
    processed_id_tweets = set()
    max_processed_id = 0
    max_processed_time_stamp = 0
    for query in queries:
        logger.info(f"Querying: {query}")
        cursor = query_twitter(api, query, since_id)
        query_submissions = []
        for resp in cursor:
            statsd.increment(f"twitter.read_post", 1, tags=[f"job_mode:{job_mode}", f"query:{query}"])
            total_returned_tweets += 1
            tweet = resp._json
            id_tweet = tweet["id"]
            if id_tweet > max_processed_id:
                max_processed_id = id_tweet
                max_processed_time_stamp = tweet["created_at"]
            # submissions is a list so we can handle single tweet with multiple media objects
            submissions, processed_id_tweets = convert_tweet(tweet, processed_id_tweets)
            if not submissions:
                continue
            query_submissions.extend(submissions)

        bulk_upload_submissions(query_submissions, TWITTER_LARAVEL_API_KEY, READER_MODE)
    logger.info(f"total_returned_tweets {total_returned_tweets}")
    if max_processed_id > 0:
        log_last_processed_id(max_processed_id, max_processed_time_stamp)
    return max_processed_id


def build_tweepy_api():
    auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
    auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
    return tweepy.API(auth, wait_on_rate_limit=True)


def query_twitter(api, query: str, since_id: int):
    return tweepy.Cursor(
        api.search,
        q=f"{query} filter:videos -filter:retweets",
        lang="en",
        since_id=since_id,
        include_entities=True,
        result_type="recent",
    ).items()


def convert_tweet(tweet: Dict[str, Any], processed_id_tweets: Set[int]) -> Tuple[List[RawSubmission], Set[int]]:
    submissions = []
    # TODO: add "monetizable" logger. like, is somebody profiting off this shit?
    if "retweeted_status" in tweet:
        tweet = tweet["retweeted_status"]
    id_tweet = tweet["id"]
    if id_tweet in processed_id_tweets:
        return None, processed_id_tweets
    processed_id_tweets.add(id_tweet)

    converted_date = twitter_created_at_to_utc(tweet["created_at"])
    submission_body = ""
    if tweet["geo"]:
        submission_body = f"Provided geo: {tweet['geo']}"
    elif tweet["user"].get("location"):
        submission_body = f"User Location: {tweet['user']['location']}"

    media_url = f'https://twitter.com/{tweet["user"]["id"]}/status/{id_tweet}'
    submission = RawSubmission(
        data_source=DataSource.twitter,
        id_source=id_tweet,
        submission_title=tweet["text"],
        submission_datetime_utc=converted_date,
        submission_community="",  # TODO: is this ok? I
        submission_url=media_url,
        submission_media_url=media_url,
        submission_body=submission_body,
        id_submitter=tweet["user"]["screen_name"],
    )
    submissions.append(submission)
    return submissions, processed_id_tweets


def twitter_created_at_to_utc(created_at: str):
    # created at format: "Mon Aug 06 19:28:16 +0000 2018",
    return datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y")


# TODO: hook up to s3 bucket
def log_last_processed_id(last_processed_id: int, last_processed_time_stamp: str):
    msg = {"last_processed_id": last_processed_id, "last_processed_time_stamp": last_processed_time_stamp}
    with open(TWITTER_LAST_RUN_FILENAME, "w") as f:
        f.write(json.dumps(msg))
    # s3_client = boto_client("s3")
    # response = s3_client.upload_file(TWITTER_LAST_RUN_FILENAME, TWITTER_LAST_RUN_BUCKET, TWITTER_LAST_RUN_FILENAME)
    # return response


def get_since_id_from_file():
    with open(TWITTER_LAST_RUN_FILENAME, "r") as f:
        d = json.load(f)
    return d.get("last_processed_id")


if __name__ == "__main__":
    run_twitter_searches()
