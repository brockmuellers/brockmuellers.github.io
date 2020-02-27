#!/bin/bash

RESUME_DIR=`dirname "$0"`/assets/resume
JSON_OUT_FILE=resume.json
JSON_PATH=${RESUME_DIR}/${JSON_OUT_FILE}

# Translate pretty YAML file into ugly JSON file so lua can handle it
cat _data/resume.yml | python3 -c 'import sys, yaml, json; y=yaml.load(sys.stdin.read()); print(json.dumps(y))' > $JSON_PATH &&

cd $RESUME_DIR &&
lualatex -synctex=1 -interaction=nonstopmode "resume_simple".tex &&
lualatex -synctex=1 -interaction=nonstopmode "resume_large".tex &&
rm $JSON_OUT_FILE
