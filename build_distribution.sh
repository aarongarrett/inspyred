#!/bin/sh
paver sdist
#WAIT ON THIS --> paver sdist upload
cd docs
make latex
cd _build/latex
pdflatex inspyred.tex
cd ../../..
#AND THIS --> paver upload_docs --upload-dir html

