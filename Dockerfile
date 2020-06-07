FROM python:3.7 as base

WORKDIR /rss_feeds

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./. .

RUN chmod 700 /rss_feeds/content_reader.py

CMD ["python", "/rss_feeds/content_reader.py"]
