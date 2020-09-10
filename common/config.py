from dotenv import load_dotenv
from os import getenv
from pathlib import Path  # python3 only
import re


env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

# Mongo creds
MONGO_HOSTNAME = getenv("MONGO_HOSTNAME")
MONGO_USERNAME = getenv("MONGO_USERNAME")
MONGO_PASSWORD = getenv("MONGO_PASSWORD")
MONGO_DBNAME = getenv("MONGO_DBNAME")

# Reddit configs
REDDIT_USER = getenv("REDDIT_USER")
REDDIT_CLIENT_ID = getenv("REDDIT_CLIENT_ID")
REDDIT_SECRET = getenv("REDDIT_SECRET")
REDDIT_DUMMY_REDIRECT = "http://localhost:8080"
REDDIT_USER_AGENT = "script for /r/2020PoliceBrutality"
SUBREDDITS = [
    "2020PoliceBrutality",
    "BrutalityArchive",
    "news",
    "politics",
    "worldpolitics",
    "publicfreakout",
    "bad_cop_no_donut",
]
EXPLICIT_SUBREDDITS = {"2020policebrutality", "brutalityarchive"}
REDDIT_KEYWORDS = {"police", "cop", "officer"}

REDDIT_KEYWORD_REGEX = re.compile(r".*(police|cop|officer).*")

READER_MODE = getenv("READER_MODE")
if not READER_MODE:
    raise ValueError(f"READER_MODE not set.")

JOB_SLEEP_TIME_SECONDS = int(getenv("JOB_SLEEP_TIME_SECONDS", 30))


IMAGE_FORMATS = {"png", "jpg", "jpeg"}

REDDIT_LARAVEL_API_KEY = getenv("REDDIT_LARAVEL_API_KEY")
LARAVEL_HOST = getenv("LARAVEL_HOST")
LARAVEL_ENDPOINT = "api/link-submission"

TWITTER_LARAVEL_API_KEY = getenv("TWITTER_LARAVEL_API_KEY")

DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

TWITTER_LAST_RUN_FILENAME = "twitter_job_last_run.json"
TWITTER_LAST_RUN_BUCKET = "last-id-cache"
DEFAULT_TWITTER_LAST_RUN_ID = 1270867714505158656
TWITTER_CONSUMER_KEY = getenv("TWITTER_CONSUMER_KEY")
TWITTER_CONSUMER_SECRET = getenv("TWITTER_CONSUMER_SECRET")
TWITTER_ACCESS_TOKEN = getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = getenv("TWITTER_ACCESS_TOKEN_SECRET")


def str2bool(v):
    if not v:
        return False
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


LOCAL_STORE = str2bool(getenv("LOCAL_STORE"))


DATADOG_OPTIONS = {
    "statsd_socket_path": getenv("DATADOG_SOCKET_PATH", "/var/run/dogstatsd/statsd.socket"),
    "api_key": getenv("DATADOG_API_KEY"),
    "app_key": getenv("DATADOG_APP_KEY"),
}

QUERIES = [
    recommended by freezman
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
    "#defendpdx",
    # found from 949mac's endpoint https://api.846policebrutality.com/api/incidents?include=evidence
    "#AbolishThePolice",
    '"tear gas"',
    # Users
    "from:greg_doucette",
    "from:1misanthrophile",
    "from:TheRealCoryElia",
    "from:hungrybowtie",
    "from:PDocumentarians",
    "from:suzettesmith",
    "from:chadloder",
    "from:R3volutionDaddy",
    "from:spekulation",
    "from:MrOlmos",
    "from:gravemorgan",
    "from:KohzKah",
    "from:bogwitchenergy",
    "from:danielvmedia",
    "from:HayesGardner",
    "from:JLJLovesRVA",
    "from:MaranieRae",
    "from:queencitynerve",
    "from:jefftaylorhuman",
    "from:themariague",
    "from:MrJesusJMontero",
    "from:RichieRequena",
    "from:hgflores_",
    "from:ChuckModi1",
]
