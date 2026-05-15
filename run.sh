#!/bin/bash

# One-click startup for AI Financial Advisor

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"

clear
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║      💰 AI FINANCIAL ADVISOR - COMPLETE SYSTEM 💰        ║"
echo "║                                                           ║"
echo "║              All-in-One Integrated Platform              ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Check if backend is already running
if nc -z localhost 8000 2>/dev/null; then
    echo "✓ Backend API is already running on port 8000"
else
    echo "🚀 Starting Backend API..."
    cd "$BACKEND_DIR"
    export PYTHONPATH="$BACKEND_DIR"
    python3 -m uvicorn main:app --reload --port 8000 > /dev/null 2>&1 &
    BACKEND_PID=$!
    
    # Wait for backend to start
    echo "⏳ Waiting for backend to initialize..."
    sleep 3
    
    if nc -z localhost 8000 2>/dev/null; then
        echo "✓ Backend API started successfully (PID: $BACKEND_PID)"
    else
        echo "❌ Failed to start backend API"
        exit 1
    fi
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "✅ SYSTEM READY FOR INTEGRATION"
echo ""
echo "📊 Available Services:"
echo ""
echo "   1. Web Dashboard (Interactive UI)"
echo "      📂 Open: $PROJECT_DIR/dashboard.html"
echo "      🌐 Or run: python3 -m http.server 8080"
echo "      Then visit: http://localhost:8080/dashboard.html"
echo ""
echo "   2. REST API (http://localhost:8000)"
echo "      📄 Swagger Docs: http://localhost:8000/docs"
echo "      📋 ReDoc: http://localhost:8000/redoc"
echo ""
echo "   3. Integration Tests"
echo "      🧪 Run: cd $PROJECT_DIR && python3 test_integration.py"
echo ""
echo "   4. Java Recommendation Engine"
echo "      ☕ Run: cd $PROJECT_DIR/java-engine && mvn exec:java"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "🔗 Sample Requests:"
echo ""
echo "   Health Check:"
echo "   curl http://localhost:8000/health"
echo ""
echo "   Single Prediction:"
echo "   curl -X POST http://localhost:8000/api/credit/predict \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"loan_amnt\": 15000, \"term\": 60, ...}'"
echo ""
echo "   Model Info:"
echo "   curl http://localhost:8000/api/credit/model-info"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "📚 Documentation:"
echo "   • Complete Guide: README_COMPLETE.md"
echo "   • Backend API: BACKEND_API_DOCS.md"
echo "   • Java Engine: JAVA_ENGINE_DOCS.md"
echo "   • Integration: INTEGRATION_GUIDE.md"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "🎯 Quick Start:"
echo ""
echo "   Step 1: Open dashboard.html in your browser"
echo "   Step 2: Fill in loan details"
echo "   Step 3: Click 'Get Prediction & Recommendation'"
echo "   Step 4: See ML predictions + Java recommendations"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Press Ctrl+C to stop the backend server"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""

# Keep the script running (backend runs in background)
wait
