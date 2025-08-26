#!/bin/bash

echo "Checking if initial region needs to be deleted..." 

python3 --version

#REGION_PATH="$HOME/Library/Application Support/minecraft/saves/krithi/region/r.0.0.mca"
#if [ -f "$REGION_PATH" ]; then
#    rm "$REGION_PATH"
#    echo "Deleted initial region" 
#else
#    echo "Initial region does not exist!" 
#fi

python3 -m venv venv 
source venv/bin/activate
pip install -r requirements.txt

python3 flask_app/generate_blocks.py
#python3 test.py
