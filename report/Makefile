PDFLATEX = pdflatex
TARGETS = report

all: $(TARGETS:%=%.pdf)

%.pdf: %.tex
	$(PDFLATEX) $<
	$(PDFLATEX) $<

clean:
	rm -f $(TARGETS:%=%.pdf) $(TARGETS:%=%.log) $(TARGETS:%=%.aux)