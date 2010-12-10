PDFLATEX = pdflatex
BIBTEX = bibtex
TARGETS = report

all: $(TARGETS:%=%.pdf)

%.pdf: %.tex %.bib
	$(PDFLATEX) $<
	$(BIBTEX) $(<:%.tex=%)
	$(PDFLATEX) $<
	$(PDFLATEX) $<

clean:
	rm -f $(TARGETS:%=%.pdf) $(TARGETS:%=%.log) $(TARGETS:%=%.aux)
	rm -f $(TARGETS:%=%.bbl) $(TARGETS:%=%.blg)