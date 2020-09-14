from datadog import statsd
from datetime import datetime
import gspread
from typing import Any, List, Optional

from clients.laravel_client import bulk_upload_submissions
from common.cache import LocalCache, S3Cache
from common.config import (
    GOOGLE_DATETIME_FORMAT,
    GOOGLE_LAST_RUN_FILENAME,
    TWITTER_LAST_RUN_BUCKET,
    GOOGLE_DATETIME_FORMAT,
    GOOGLE_FORMS_LARAVEL_API_KEY,
)
from common.data_classes import RawSubmission
from common.enums import DataSource


def run_form_reader(
    account_creds_file: str,
    form_id: str,
    job_mode: str,
    last_run_date_str: Optional[str] = None,
    local_store: bool = False,
) -> None:

    curtime = datetime.now()

    cache = LocalCache(GOOGLE_LAST_RUN_FILENAME)
    if not local_store:
        cache = S3Cache(GOOGLE_LAST_RUN_FILENAME, TWITTER_LAST_RUN_BUCKET)

    if not last_run_date_str:
        last_run_date_str = cache.get_last_processed_time_stamp_from_file()

    last_run_datetime = datetime.strptime(last_run_date_str, GOOGLE_DATETIME_FORMAT)

    gc = gspread.service_account(filename=account_creds_file)
    sh = gc.open_by_key(form_id)
    ws = sh.get_worksheet(0)

    rows = ws.get_all_values()
    statsd.increment(f"google_form.rows_processed", len(rows), tags=[f"job_mode:{job_mode}"])

    results = _process_form_results(rows, last_run_datetime)
    if results:
        bulk_upload_submissions(results, GOOGLE_FORMS_LARAVEL_API_KEY, job_mode)

    cache.log_last_processed_timestamp(curtime.strftime(GOOGLE_DATETIME_FORMAT))


def _process_form_results(rows: List[List[Any]], last_run_datetime: datetime) -> List[RawSubmission]:
    results = []
    for idx, row in enumerate(rows):
        if idx == 0 or row[0] == "":
            continue

        row_timestamp = datetime.strptime(row[0], GOOGLE_DATETIME_FORMAT)
        if row_timestamp < last_run_datetime:
            continue

        results.append(
            RawSubmission(
                data_source=DataSource.google_form,
                id_source=idx,
                submission_community="",
                submission_datetime_utc=row_timestamp,
                submission_title=f"{row[8]} - {row[4]} - {row[5]} - {row[6]}",
                submission_body=f"{row[3]} - {row[9]}",
                submission_url=row[1],
                submission_media_url=row[1],
                id_submitter="N/A",
            )
        )
    return results
