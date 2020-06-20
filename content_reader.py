from datadog import initialize

import argparse
import logging
import time

from common.config import DATADOG_OPTIONS, JOB_SLEEP_TIME_SECONDS, READER_MODE
from reddit.feed_reader import run_reddit_feed
from twitter.searcher import run_twitter_searches

logging.basicConfig()
logging.root.setLevel(logging.INFO)


logger = logging.getLogger(__name__)

initialize(**DATADOG_OPTIONS)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "local_store", help="Whether to store stuff locally or s3", default=False
    )
    args = parser.parse_args()

    twitter_since_id = None
    try:
        while True:
            logger.info(f"Job Starting.")
            if READER_MODE == "reddit":
                run_reddit_feed()
            elif READER_MODE == "twitter":
                twitter_since_id = run_twitter_searches(
                    twitter_since_id, args.local_store
                )
            else:
                raise ValueError(f"READER_MODE {READER_MODE} not supported")
            logger.info(f"Job complete. Sleeping for {JOB_SLEEP_TIME_SECONDS} seconds.")
            time.sleep(JOB_SLEEP_TIME_SECONDS)
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt called. Exiting.")
