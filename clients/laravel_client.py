import time
from datadog import statsd
from json import dumps
import pickle
import requests
from typing import List

from common.config import LARAVEL_HOST, LARAVEL_ENDPOINT
from common.data_classes import RawSubmission


def bulk_upload_submissions(raw_submissions: List[RawSubmission], api_key: str, job_mode: str) -> None:
    start_time = time.time()
    json_submissions = []
    for raw_submission in raw_submissions:
        json_submissions.append(raw_submission.to_dict())

    headers = {"Content-Type": "application/json", "Api-Token": api_key}

    data_dump = dumps({"data": json_submissions})

    resp = requests.post(url=f"{LARAVEL_HOST}/{LARAVEL_ENDPOINT}", data=data_dump, headers=headers)
    end_time = time.time()

    statsd.gauge(f"laravel.{LARAVEL_ENDPOINT}.duration", end_time - start_time, tags=[f"job_mode:{job_mode}"])
    statsd.gauge(
        f"laravel.{LARAVEL_ENDPOINT}.request_size", len(pickle.dumps(data_dump)), tags=[f"job_mode:{job_mode}"]
    )
    statsd.increment(f"laravel.{LARAVEL_ENDPOINT}.success", 1, tags=[f"job_mode:{job_mode}"])
    statsd.increment(f"laravel.{LARAVEL_ENDPOINT}.num_rows", len(raw_submissions), tags=[f"job_mode:{job_mode}"])

    if resp.status_code != 200:
        raise ValueError(f"Failed to upload to Laravel with resp: {resp.text}")
