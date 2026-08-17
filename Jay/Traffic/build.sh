#!/bin/bash
# Build Traffic paper -> ../Traffic_v<version>.pdf (Jay folder).
# Version is taken from the \date line in Traffic.tex.
set -e
cd "$(dirname "$0")"
pdflatex -interaction=nonstopmode Traffic.tex > /dev/null
pdflatex -interaction=nonstopmode Traffic.tex > /dev/null
V=$(grep -o 'Version [0-9]\.[0-9][0-9]' Traffic.tex | head -1 | cut -d' ' -f2)
cp Traffic.pdf "../Traffic_v${V}.pdf"
echo "built Traffic.pdf -> ../Traffic_v${V}.pdf ($(pdfinfo Traffic.pdf 2>/dev/null | grep Pages || true))"
