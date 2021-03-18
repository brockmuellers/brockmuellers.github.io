#!/bin/bash

# Designed for a csv file exported by google sheets, which may have carriage returns.

INFILE=$1 # e.g. 2020_03_31

OUTFILE=`dirname "$0"`/_data/plants.csv

mv "$INFILE" $OUTFILE &&
echo "Imported ${INFILE}" &&

dos2unix $OUTFILE &&
echo "Removed carriage returns"


