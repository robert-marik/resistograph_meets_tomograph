# Makefile pro generování prezentace a upload

all:
	docker run --rm --init -v $(PWD):/home/marp/app/ -e LANG=$(LANG) -e MARP_USER="$(id -u):$(id -g)"  marpteam/marp-cli talk.md --pdf --allow-local-files
	docker run --rm --init -v $(PWD):/home/marp/app/ -e LANG=$(LANG) -e MARP_USER="$(id -u):$(id -g)"  marpteam/marp-cli talk.md 

