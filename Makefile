IMAGE_NAME = "pb2020-content-reader"

READER_MODE = "default"
READER_MODE_REDDIT = "reddit"
READER_MODE_TWITTER = "twitter"
READER_MODE_FORM = "form"

JOB_SLEEP_TIME_SECONDS="30"

REGISTRY_NAME=$(shell grep REGISTRY_NAME .env | cut -d "=" -f2)
IMAGE_PATH = /pb2020/crawlers

azure_login:
	az acr login --name $(REGISTRY_NAME)


build:
	docker build --rm \
	--tag=$(IMAGE_NAME) \
	.

run:
	$(MAKE) build
	docker run -it \
	-v=$(CURDIR):/rss_feeds \
	-e READER_MODE=$(READER_MODE) \
	-e JOB_SLEEP_TIME_SECONDS=$(JOB_SLEEP_TIME_SECONDS) \
	$(IMAGE_NAME) \
	$(cmd)

run_reddit:
	$(MAKE) build
	$(MAKE) run READER_MODE=$(READER_MODE_REDDIT)

run_twitter:
	$(MAKE) build
	$(MAKE) run READER_MODE=$(READER_MODE_TWITTER)

run_form:
	$(MAKE) build
	$(MAKE) run READER_MODE=$(READER_MODE_FORM)

unit:
	$(MAKE) build
	$(MAKE) run cmd="python -m pytest ./tests/unit/"

# Pass in tag an manually increment
push:
	$(MAKE) build IMAGE_NAME=$(REGISTRY_NAME)$(IMAGE_PATH):$(TAG)
	docker push $(REGISTRY_NAME)$(IMAGE_PATH):$(TAG)
