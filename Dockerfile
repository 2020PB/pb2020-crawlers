FROM python:3.7-slim-buster as base

WORKDIR /rss_feeds

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# We clean up a lot of space by deleting rogue .c files etc:
RUN find /usr/local/lib/python3.7 -name '*.c' -delete
RUN find /usr/local/lib/python3.7 -name '*.pxd' -delete
RUN find /usr/local/lib/python3.7 -name '*.pyd' -delete
# Cleaning up __pycache__ gains more space
RUN find /usr/local/lib/python3.7 -name '__pycache__' | xargs rm -r
		
FROM python:3.7-slim-buster
WORKDIR  /rss_feeds

COPY --from=base /usr/local/lib/python3.7 /usr/local/lib/python3.7
COPY ./. /rss_feeds
RUN chmod 700 /rss_feeds/content_reader.py

CMD ["python", "/rss_feeds/content_reader.py", "local_store"]
