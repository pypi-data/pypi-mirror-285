#!/bin/bash

export root=$(pwd)
echo "root:  $root"



######## PYTHON #########################################
export PYTHONPATH="$root/"
echo "PYTHONPATH:  $PYTHONPATH"


######## Tesseract ######################################
export tesseract_path=$(which tesseract)
echo "tesseract_path:  $tesseract_path"

export PATH="$PATH:$tesseract_path"



