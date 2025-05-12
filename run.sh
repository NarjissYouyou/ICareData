#!/bin/bash

set -e
ENV_NAME=".venv"

python3 -m venv $ENV_NAME
source $ENV_NAME/bin/activate
pip install --upgrade pip

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

# Launch each party in background
# python3 -m mpyc run_match.py -M3 -I0  
python3 run_match.py -M2 -I0 --loopback &
python3 run_match.py -M2 -I1 --loopback &

wait
echo "MPC run complete."
