# Makefile pro generování prezentace a upload

PDF = talk.pdf
HTML = talk.html
MD = talk.md
REMOTE = cornus.mendelu.cz:html/talks/Marik_Ohrid_2025.pdf

all:
	marp $(MD) -o $(PDF) --allow-local-file
	marp $(MD) -o $(HTML)

upload: $(PDF)
	scp $(PDF) $(REMOTE)
