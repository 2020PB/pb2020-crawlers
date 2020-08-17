import tweepy
from typing import Dict, List, Any, Set, Tuple
from datetime import datetime
import json
import logging

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

# from common.utils import write_raw_submissions_to_csv

QUERIES = [
    # May want to remove later on,
    "#PrideMarch",
    # recommended by freezman
    "#bluefall",
    "#PoliceBrutality",
    "#PoliceBrutalityPandemic",
    "#Protests2020",
    # cities by population - protests
    "#nycProtests",
    "#newyorkProtests",
    "#losangelesProtests",
    "#laprotests",
    "#stLouisProtests",
    "#stlProtests",
    "#philadelphiaprotests",
    "#phillyprotests",
    "#chicagoprotests",
    "#houstonprotests",
    "#phoenixProtests",
    "#miamiProtests",
    "#dcprotests",
    "#WashingtonDCProtest",
    "#seattleprotest",
    "#seattleprotests",
    "#seattleprotestcomms",
    "#austinprotest",
    "defendpdx",
    # found from 949mac's endpoint https://api.846policebrutality.com/api/incidents?include=evidence
    "#GeorgeFloyd",
    "#JusticeForGeorgeFloyd",
    "#AbolishThePolice",
    "#BlackLivesMatter",
    "tear gas",
    # Common occurrences
    "#DefundThePolice",
    # Users
    "@greg_doucette",
    "@misanthrophile",
    "@TheRealCoryElia",
    "@hungrybowtie",
    "@PDocumentarians",
    "@suzettesmith",
    "@chadloder",
    "@R3volutionDaddy",
    "@spekulation",
    "@MrOlmos",
    "@gravemorgan",
    "@KohzKah",
    "@bogwitchenergy",
    "@danielvmedia",
]


def run_twitter_searches(since_id: int) -> int:
    if not since_id:
        since_id = get_since_id_from_file()
    api = build_tweepy_api()
    # tweets = []
    total_returned_tweets = 0
    processed_id_tweets = set()
    max_processed_id = 0
    max_processed_time_stamp = 0
    for query in QUERIES:
        logger.info(f"Querying: {query}")
        cursor = query_twitter(api, query, since_id)
        for resp in cursor:
            logger.info("Found a tweet!")
            total_returned_tweets += 1
            tweet = resp._json
            id_tweet = tweet["id"]
            if id_tweet > max_processed_id:
                max_processed_id = id_tweet
                max_processed_time_stamp = tweet["created_at"]
                # TODO: should we keep updating this file, so it is up to date if the job quits unexpectedly?
                # pro: can pick up where we left off and avoid duplicates
                # con: may miss hits from searches that were not yet performed
                # log_last_processed_id(max_processed_id, max_processed_time_stamp)
            # submissions is a list so we can handle single tweet with multiple media objects
            submissions, processed_id_tweets = convert_tweet(tweet, processed_id_tweets)
            if not submissions:
                continue
            bulk_upload_submissions(submissions, TWITTER_LARAVEL_API_KEY, READER_MODE)
    logger.info(f"total_returned_tweets {total_returned_tweets}")
    log_last_processed_id(max_processed_id, max_processed_time_stamp)
    return max_processed_id


def build_tweepy_api():
    auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
    auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
    return tweepy.API(auth, wait_on_rate_limit=True)


def query_twitter(api, query: str, since_id: int):
    # TODO: include result_type? (mixed, recent, popular) probably want recent once batching is set up
    # TODO: why wasn't count working
    return tweepy.Cursor(api.search, q=query, lang="en", since_id=since_id, include_entities=True).items()


def convert_tweet(tweet: Dict[str, Any], processed_id_tweets: Set[int]) -> Tuple[List[RawSubmission], Set[int]]:
    submissions = []
    # TODO: add "monetizable" logger. like, is somebody profiting off this shit?
    if not is_tweet_relevant(tweet):
        return None, processed_id_tweets
    if "retweeted_status" in tweet:
        tweet = tweet["retweeted_status"]
    id_tweet = tweet["id"]
    if id_tweet in processed_id_tweets:
        return None, processed_id_tweets
    logger.info("Found a tweet to add!")
    processed_id_tweets.add(id_tweet)

    converted_date = twitter_created_at_to_utc(tweet["created_at"])
    submission_body = ""
    if tweet["geo"]:
        submission_body = f"Provided geo: {tweet['geo']}"
    elif tweet["user"].get("location"):
        submission_body = f"User Location: {tweet['user']['location']}"

    for media in tweet["extended_entities"]["media"]:
        if media["type"] != "video":
            continue
        logger.info(f"found video for tweet: {tweet['text']}")
        media_url = get_media_url_from_variants(media["video_info"]["variants"])
        if not media_url:
            continue

        submission = RawSubmission(
            data_source=DataSource.twitter,
            id_source=id_tweet,
            submission_title=tweet["text"],
            submission_datetime_utc=converted_date,
            submission_community="",  # TODO: is this ok? I
            submission_url=media["expanded_url"],
            submission_media_url=media_url,
            submission_body=submission_body,
            id_submitter=tweet["user"]["id"],
        )
        submissions.append(submission)
    return submissions, processed_id_tweets


def is_tweet_relevant(tweet: Dict[str, Any]):
    media = tweet.get("extended_entities", {}).get("media")
    if media:
        return True
    return False


def twitter_created_at_to_utc(created_at: str):
    # created at format: "Mon Aug 06 19:28:16 +0000 2018",
    return datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y")


def get_media_url_from_variants(variants: List[Dict[str, str]]):
    for variant in variants:
        if variant["content_type"] == "video/mp4":
            # TODO: multiple bitrates are available, does it matter which?
            return variant["url"]
    return None


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
