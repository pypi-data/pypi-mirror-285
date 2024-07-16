#!/bin/bash

# Keeps Python from generating .pyc files in container
export PYTHONDONTWRITEBYTECODE=1   

# Turns off buffering for easier container logging
export PYTHONUNBUFFERED=1          

#### Remove Assert and Docstring
## Need to remove it because create issue with smart_open at loading of module
#export PYTHONOPTIMIZE=2 


