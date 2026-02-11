#!/bin/bash
cd /home/openclaw-expenses/apps/openclaw-expenses/backend
source venv/bin/activate
uvicorn main_v2:app --host 0.0.0.0 --port 8000 > app.log 2>&1

