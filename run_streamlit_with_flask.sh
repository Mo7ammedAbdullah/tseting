#!/usr/bin/env bash
set -e

# Start Flask app in background
python3 app.py &
FLASK_PID=$!

echo "Started Flask (PID=${FLASK_PID}). Waiting for it to become available..."
sleep 2

# Run streamlit (will block)
streamlit run streamlit_app.py

# When Streamlit exits, kill Flask
echo "Stopping Flask (PID=${FLASK_PID})"
kill ${FLASK_PID} || true
