#!/bin/bash

echo "Checking if initial region needs to be deleted..." 

python3 --version
python3 -m venv venv 
source venv/bin/activate
pip install -r requirements.txt

python3 flask_app/app.py
