#!/bin/bash
# ResearchAI - Startup Check and Initialization Script
# Run this before your interview demo to ensure everything is ready

echo "🚀 ResearchAI - Interview Demo Startup Check"
echo "=" * 60

# 1. Start all services
echo ""
echo "1️⃣  Starting all Docker containers..."
docker-compose up -d

# 2. Wait for services to be healthy
echo ""
echo "2️⃣  Waiting for services to be healthy (30 seconds)..."
sleep 30

# 3. Run health check
echo ""
echo "3️⃣  Running health check..."
./scripts/infra/healthcheck.sh

# 4. Check if Ollama model is loaded
echo ""
echo "4️⃣  Checking Ollama LLM model..."
MODEL_CHECK=$(docker exec researchai-ollama ollama list | grep llama3.2 || echo "")

if [ -z "$MODEL_CHECK" ]; then
    echo "⚠️  llama3.2 model not found. Pulling now (this will take ~5-10 minutes)..."
    docker exec researchai-ollama ollama pull llama3.2
    echo "✅ Model downloaded!"
else
    echo "✅ llama3.2 model is ready"
fi

# 5. Check indexed chunks count
echo ""
echo "5️⃣  Checking indexed chunks..."
CHUNK_COUNT=$(curl -s 'http://localhost:9200/chunks/_count' | python3 -c "import sys, json; print(json.load(sys.stdin)['count'])" 2>/dev/null || echo "0")
echo "📊 Indexed chunks: $CHUNK_COUNT/1992"

if [ "$CHUNK_COUNT" -lt 100 ]; then
    echo "⚠️  WARNING: Very few chunks indexed. Search may return limited results."
    echo "   Run: docker exec researchai-airflow airflow dags trigger embed_and_index"
fi

# 6. Test search endpoint
echo ""
echo "6️⃣  Testing search endpoint..."
SEARCH_TEST=$(curl -s -X POST http://localhost:8000/search \
  -H 'Content-Type: application/json' \
  -d '{"query": "machine learning", "k": 3}' | python3 -c "import sys, json; print('OK' if 'results' in json.load(sys.stdin) else 'FAIL')" 2>/dev/null || echo "FAIL")

if [ "$SEARCH_TEST" = "OK" ]; then
    echo "✅ Search endpoint working"
else
    echo "❌ Search endpoint not responding"
fi

# 7. Test Q&A endpoint
echo ""
echo "7️⃣  Testing Q&A endpoint..."
ASK_TEST=$(curl -s -X POST http://localhost:8000/ask \
  -H 'Content-Type: application/json' \
  -d '{"question": "What is AI?"}' | python3 -c "import sys, json; data=json.load(sys.stdin); print('OK' if 'answer' in data else data.get('detail', 'FAIL'))" 2>/dev/null || echo "FAIL")

if [ "$ASK_TEST" = "OK" ]; then
    echo "✅ Q&A endpoint working"
else
    echo "⚠️  Q&A endpoint status: $ASK_TEST"
    if [[ "$ASK_TEST" == *"unavailable"* ]]; then
        echo "   (LLM model may still be loading - wait 1-2 minutes and try again)"
    fi
fi

# 8. Summary
echo ""
echo "=" * 60
echo "✅ STARTUP CHECK COMPLETE!"
echo ""
echo "📱 Access your demo:"
echo "   - UI:      http://localhost:7860"
echo "   - API:     http://localhost:8000/docs"
echo "   - Airflow: http://localhost:8080 (airflow/airflow)"
echo ""
echo "📝 See INTERVIEW_DEMO_GUIDE.md for presentation tips"
echo "=" * 60
