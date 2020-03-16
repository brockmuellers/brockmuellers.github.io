#!/bin/bash

DATE_FOR_BACKUP=$1 # e.g. 2020_03_31

BACKUP_DIR=~/Dropbox/Documents/Work/Resumes
RESUME_DIR=`dirname "$0"`/assets/resume
JSON_OUT_FILE=resume.json
JSON_PATH=${RESUME_DIR}/${JSON_OUT_FILE}

# Translate pretty YAML file into ugly JSON file so lua can handle it
cat _data/resume.yml | python3 -c 'import sys, yaml, json; y=yaml.load(sys.stdin.read()); print(json.dumps(y))' > $JSON_PATH &&

cd $RESUME_DIR &&
lualatex -synctex=1 -interaction=nonstopmode "resume".tex &&
lualatex -synctex=1 -interaction=nonstopmode "resume_large".tex &&
echo "Successfully generated resumes." &&

if [ "$DATE_FOR_BACKUP" != "" ]
then
    BACKUP_DEST=${BACKUP_DIR}/${DATE_FOR_BACKUP} &&
    mkdir $BACKUP_DEST &&
    cp ./{resume_large.tex,resume.tex,resume_large.pdf,resume.pdf,resume.json} $BACKUP_DEST/ &&
    echo "Copied files to ${BACKUP_DEST}."
fi
