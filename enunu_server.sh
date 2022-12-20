#!/bin/bash


## just in case
sudo apt install python3.8-venv
python -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt --no-cache-dir
python synthesis/enunu_server.py 