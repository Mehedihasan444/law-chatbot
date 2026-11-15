# Bangladesh Constitution Chatbot - Quick Reference Guide

## 🚀 Quick Commands

### First Time Setup
```bash
python start.py setup              # Complete setup wizard
python validate_env.py --auto-fix  # Validate configuration
```

### Running the Chatbot

#### CLI (Fastest)
```bash
python cli.py                      # Interactive mode
python cli.py -q "Your question"   # Single query
python cli.py --no-llm            # Faster, simpler responses
```

#### API Server
```bash
python start.py api                # Start API on port 8000
python api.py --port 8080         # Custom port
python api.py --reload            # Development mode
```

#### Web Interface
```bash
python start.py streamlit          # Start Streamlit on port 8501
streamlit run src/streamlit_app.py # Direct command
```

#### Docker
```bash
docker-compose up -d               # Start all services
docker-compose logs -f             # View logs
docker-compose down                # Stop services
```

## 📚 Common Tasks

### Data Management
```bash
# Download Constitution PDFs
python src/data_processor.py --download

# Process and create embeddings
python src/data_processor.py --process

# Rebuild vector store
python -c "from src.rag_pipeline import ConstitutionRAG; from config.config import Config; rag = ConstitutionRAG(Config()); rag.initialize(force_rebuild=True)"
```

### Testing
```bash
pytest                             # Run all tests
pytest tests/test_api.py -v      # API tests with verbose output
pytest --cov                      # With coverage report
```

### Environment
```bash
python validate_env.py            # Check configuration
python validate_env.py --create-env  # Create .env file
```

## 🔧 Configuration Quick Edit

Edit `.env` file:
```env
GEMINI_API_KEY=your_key_here      # Required for full functionality
LLM_TYPE=gemini                   # Options: gemini, local, openai
TEMPERATURE=0.1                   # 0.0 (strict) to 2.0 (creative)
TOP_K_RETRIEVAL=5                 # Number of sources to retrieve
```

## 💡 Example Queries

### English
- "What are the fundamental rights?"
- "Explain Article 27"
- "What does the Constitution say about freedom of speech?"
- "How can the Constitution be amended?"

### Bangla
- "মৌলিক অধিকার কি?"
- "অনুচ্ছেদ ২৭ ব্যাখ্যা করুন"
- "সংবিধানে বাক স্বাধীনতা সম্পর্কে কি বলা আছে?"
- "সংবিধান কিভাবে সংশোধন করা যায়?"

## 🌐 API Endpoints

### Core Endpoints
```
GET  /                    # API info
GET  /health              # Health check
GET  /stats               # System statistics
POST /query               # Ask question
GET  /history?limit=10    # Get history
DELETE /history           # Clear history
POST /initialize          # Reinitialize system
```

### Example cURL
```bash
# Query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Article 27?", "use_llm": true}'

# Health
curl http://localhost:8000/health

# Stats
curl http://localhost:8000/stats
```

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| API key error | Edit `.env` and add valid `GEMINI_API_KEY` |
| No data files | Run `python src/data_processor.py --download --process` |
| Import errors | Run `pip install -r requirements.txt` |
| Port in use | Change port: `python api.py --port 8080` |
| Slow responses | Use `--no-llm` flag or set `use_llm: false` |
| Memory issues | Use Gemini API instead of local models |

## 📊 System Requirements

### Minimum
- Python 3.10+
- 4GB RAM
- 2GB disk space
- Internet connection (for Gemini API)

### Recommended
- Python 3.11+
- 8GB RAM
- 5GB disk space
- Stable internet connection

## 🔗 Useful URLs

When servers are running:
- API Docs: http://localhost:8000/docs
- API Alternative Docs: http://localhost:8000/redoc
- Streamlit UI: http://localhost:8501
- Health Check: http://localhost:8000/health

## 📞 Support

- Report bugs: https://github.com/Mehedihasan444/law-chatbot/issues
- Discussions: https://github.com/Mehedihasan444/law-chatbot/discussions
- Documentation: README.md

## ⚡ Performance Tips

1. **For fastest responses**: Use CLI with `--no-llm`
2. **For best quality**: Use API with `use_llm: true` and Gemini
3. **For offline use**: Set `LLM_TYPE=local` (requires more RAM)
4. **For production**: Use Docker deployment with proper resources

## 🔒 Security Notes

- Keep `.env` file secret (never commit to git)
- Use environment-specific configurations
- Enable rate limiting in production
- Consider API authentication for public deployments
- Regularly update dependencies

---

**Last Updated**: 2025-10-03
**Version**: 1.0.0
