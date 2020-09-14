from datadog import initialize, statsd

import logging
import time

from common.config import (
    DATADOG_OPTIONS,
    JOB_SLEEP_TIME_SECONDS,
    READER_MODE,
    QUERIES,
    LOCAL_STORE,
    GOOGLE_FORM_ID,
    GOOGLE_SERVICE_ACCOUNT_FILE,
)
from google_forms.reader import run_form_reader
from reddit.feed_reader import run_reddit_feed
from twitter.searcher import run_twitter_searches


logging.basicConfig()
logging.root.setLevel(logging.INFO)


logger = logging.getLogger(__name__)

initialize(**DATADOG_OPTIONS)


if __name__ == "__main__":
    twitter_since_id = None
    try:
        while True:
            logger.info(f"Job Starting.")
            statsd.increment(f"job.start", 1, tags=[f"job_mode:{READER_MODE}"])
            if READER_MODE == "reddit":
                run_reddit_feed()
            elif READER_MODE == "twitter":
                twitter_since_id = run_twitter_searches(twitter_since_id, QUERIES, READER_MODE, LOCAL_STORE)
            elif READER_MODE == "form":
                run_form_reader(GOOGLE_SERVICE_ACCOUNT_FILE, GOOGLE_FORM_ID, READER_MODE)
            else:
                raise ValueError(f"READER_MODE {READER_MODE} not supported")
            statsd.increment(f"job.finish", 1, tags=[f"job_mode:{READER_MODE}"])
            logger.info(f"Job complete. Sleeping for {JOB_SLEEP_TIME_SECONDS} seconds.")
            time.sleep(JOB_SLEEP_TIME_SECONDS)
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt called. Exiting.")
