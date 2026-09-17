#!/bin/bash
# ============================================================
# జ్యోతిష — Vedic Astrology System — Startup Script
# Usage:  ./start.sh
# ============================================================
cd "$(dirname "$0")"

echo "🌟 Starting జ్యోతిష Vedic Astrology System..."

# Kill any previous instance on port 7575
lsof -ti:7575 | xargs kill -9 2>/dev/null && echo "  ↳ Cleared old process on :7575"

# Start server in background, log to file
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 7575 --reload > /tmp/jyotisha.log 2>&1 &
SERVER_PID=$!

# Wait for it to be ready
echo "  ↳ Waiting for server (PID $SERVER_PID)..."
for i in {1..10}; do
  sleep 1
  if curl -s -o /dev/null -w "%{http_code}" http://localhost:7575/ | grep -q "200"; then
    echo "  ✅ Server is up!"
    break
  fi
  echo "    attempt $i/10..."
done

echo ""
echo "  🌐 App running at: http://localhost:7575"
echo "  📋 Logs:          tail -f /tmp/jyotisha.log"
echo "  🛑 Stop:          lsof -ti:7575 | xargs kill -9"
echo ""

# Open browser (Mac)
open http://localhost:7575
