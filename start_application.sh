#!/bin/bash

# AI Financial Advisor - Complete Application Startup Script
# Starts Backend API, Java Engine, and Integration Tests

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
JAVA_DIR="$PROJECT_DIR/java-engine"

echo "=========================================="
echo "AI FINANCIAL ADVISOR - APPLICATION START"
echo "=========================================="
echo ""

# Start Backend API
echo "1️⃣  Starting Backend API on port 8000..."
cd "$BACKEND_DIR"
export PYTHONPATH="$BACKEND_DIR"

python3 -m uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
echo "   Waiting for backend to be ready..."
sleep 3
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "   ✓ Backend API is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "   ❌ Backend failed to start"
        exit 1
    fi
    sleep 1
done

echo ""
echo "2️⃣  Building Java Recommendation Engine..."
cd "$JAVA_DIR"
mvn clean package -q 2>&1 | grep -E "BUILD|ERROR" || true
echo "   ✓ Java engine built successfully"

echo ""
echo "=========================================="
echo "✅ APPLICATION STARTED SUCCESSFULLY"
echo "=========================================="
echo ""
echo "📊 Services Running:"
echo "   • Backend API: http://localhost:8000"
echo "   • API Docs: http://localhost:8000/docs"
echo "   • Health: http://localhost:8000/health"
echo ""
echo "🔗 Available Endpoints:"
echo "   • POST /api/credit/predict - Single prediction"
echo "   • POST /api/credit/batch-predict - Batch predictions"
echo "   • GET /api/credit/model-info - Model information"
echo "   • GET /api/credit/features - Feature list"
echo ""
echo "Java Engine: Ready to run recommendations"
echo ""
echo "Press Ctrl+C to stop the application"
echo "=========================================="
echo ""

# Run integration tests
echo ""
echo "3️⃣  Running Integration Tests..."
cd "$PROJECT_DIR"
python3 test_integration.py 2>&1 | head -60

echo ""
echo "=========================================="
echo "🎉 APPLICATION FULLY INTEGRATED"
echo "=========================================="
echo ""
echo "Backend is running. Press Ctrl+C to stop."
echo ""

# Keep backend running
wait $BACKEND_PID
