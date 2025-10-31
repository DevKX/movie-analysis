#!/bin/bash

# Create venv if missing
if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3.12 -m venv venv
fi

# Activate
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run app
uvicorn src.api.main:app --reload &

sleep 2
open "http://127.0.0.1:8000/docs"
wait