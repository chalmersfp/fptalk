REMOTE := remote11.chalmers.se
REMOTE_DIR := /chalmers/groups/w3ifl/www/fptalks.cse.chalmers.se

HUGO_IMAGE := hugomods/hugo:exts
DOCKER_RUN := docker run \
    --rm \
    --interactive \
    --tty \
	--user "$(shell id -u):$(shell id -g)" \
	--volume "$(PWD):/src"

.PHONY: serve build deploy clean

serve: build
	python -m http.server --directory public

clean:
	rm -rf public resources .hugo_build.lock

build: clean
	$(DOCKER_RUN) $(HUGO_IMAGE) \
		hugo --source /src --buildFuture --minify
	python generate_ics.py

deploy: build
	@read -p "CID: " user; \
	rsync --archive --verbose --human-readable --compress --delete \
    	public/* "$$user@$(REMOTE):$(REMOTE_DIR)/"