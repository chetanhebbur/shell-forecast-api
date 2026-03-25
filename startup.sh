#!/bin/bash
cd /home/chethan/shell_api
pip install -r requirements.txt --user
uvicorn app.main:app --host 0.0.0.0 --port 8000
