#!/bin/bash

RESUME_DIR=`dirname "$0"`/assets/resume

cd $RESUME_DIR

lualatex -synctex=1 -interaction=nonstopmode "resume_simple".tex

lualatex -synctex=1 -interaction=nonstopmode "resume_large".tex
