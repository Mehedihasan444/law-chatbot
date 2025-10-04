#!/bin/bash
# Quick test script for Bangladesh Constitution Chatbot

echo "🏛️ Bangladesh Constitution Chatbot - Quick Test"
echo "================================================"
echo ""

# Activate venv
source venv/Scripts/activate

echo "1️⃣ Testing CLI with a simple query..."
echo ""
python cli.py -q "What does Article 27 say?" --no-llm --no-banner

echo ""
echo "================================================"
echo "✅ Test completed!"
echo ""
echo "To use the chatbot:"
echo "  • CLI: python cli.py"
echo "  • API: python api.py"
echo "  • Web: streamlit run src/streamlit_app.py"
