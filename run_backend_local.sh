#!/bin/bash
cd /home/openclaw-expenses/apps/openclaw-expenses/backend
source venv/bin/activate
uvicorn main_v2:app --host 127.0.0.1 --port 8000 --no-server-header --loop asyncio > app.log 2>&1

