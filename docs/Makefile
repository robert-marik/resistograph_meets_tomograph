# Makefile for talk compilation and upload
# ----------------------------------------
#
# all        Use Marp to compule talk.md into PDF and HTML
# deploy     Copy outputs to ../dist/ and upload using ghp-import

help:
	@grep -E '^# ' Makefile | sed 's/^# //'

all:
	docker run --rm --init -v $(PWD):/home/marp/app/ -e LANG=$(LANG) -e MARP_USER="$$(id -u):$$(id -g)"  marpteam/marp-cli talk.md --pdf --allow-local-files
	docker run --rm --init -v $(PWD):/home/marp/app/ -e LANG=$(LANG) -e MARP_USER="$$(id -u):$$(id -g)"  marpteam/marp-cli talk.md 

deploy:
	cp *.png ../dist/
	cp *.pdf ../dist/
	cp *.html ../dist/
	cp *.js ../dist/
	cp *.css ../dist/
	ghp-import -n -o -p -f ../dist/	