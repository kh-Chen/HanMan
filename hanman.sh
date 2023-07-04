#!/bin/bash

cd /home/chenkh/workspace/HanMan/

source venv/bin/activate
nohup python -u main.py >> console.log 2>&1 &
