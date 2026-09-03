#!/bin/bash

echo "======================================"
echo "       SKILLPROOF AUTO START"
echo "======================================"

# Stop any old Flask process using port 5001
echo ""
echo "[1/5] Checking port 5001..."

PID=$(lsof -ti :5001)

if [ -n "$PID" ]; then
    echo "Stopping old process: $PID"
    kill -9 $PID 2>/dev/null
fi

# Activate virtual environment
echo ""
echo "[2/5] Activating virtual environment..."

if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "ERROR: venv folder not found."
    exit 1
fi

# Check Python syntax
echo ""
echo "[3/5] Checking Python files..."

python -m py_compile app.py database.py qr_generator.py

if [ $? -ne 0 ]; then
    echo ""
    echo "======================================"
    echo "ERROR: Python syntax check failed."
    echo "Fix the error above."
    echo "======================================"
    exit 1
fi

echo "Python syntax: OK"

# Set public URL
echo ""
echo "[4/5] Setting public URL..."

export PUBLIC_BASE_URL="http://127.0.0.1:5001"

echo "PUBLIC_BASE_URL=$PUBLIC_BASE_URL"

# Start Flask
echo ""
echo "[5/5] Starting SkillProof..."
echo ""
echo "======================================"
echo " SkillProof is running!"
echo "======================================"
echo ""
echo "Open:"
echo "http://127.0.0.1:5001"
echo ""
echo "Press CTRL+C to stop."
echo ""

flask --app app run --host 0.0.0.0 --port 5001
