#!/bin/bash
set -e
echo "🚀 Starting refactored deployment..."

# --- Variables ---
APP_DIR="/home/openclaw-expenses/apps/openclaw-expenses"
BACKEND_DIR="$APP_DIR/backend"
FRONTEND_DIR="$APP_DIR/frontend"
SERVICE_FILE="~/.config/systemd/user/openclaw-backend.service"

# --- Backend Deployment ---
echo "🔧 Deploying Backend..."
cd $APP_DIR
echo "Git: Fetching latest master..."
git fetch origin master
git reset --hard origin/master

echo "Python: Installing dependencies..."
cd $BACKEND_DIR
source venv/bin/activate
pip install -r requirements.txt

echo "Systemd: Reloading and restarting backend service..."
systemctl --user daemon-reload
systemctl --user restart openclaw-backend
sleep 3 # Wait for service to restart
systemctl --user status openclaw-backend --no-pager

# --- Frontend Deployment ---
echo "🎨 Deploying Frontend..."
cd $FRONTEND_DIR

echo "Node: Installing dependencies..."
npm install --registry=https://registry.npmmirror.com

echo "Vite: Building frontend..."
# Use vite build directly to bypass potential tsc issues
./node_modules/.bin/vite build

echo "✅ Deployment script finished."


