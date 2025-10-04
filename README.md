# Bangladesh Constitution Chatbot 🏛️

A comprehensive law-based chatbot for Bangladesh using RAG (Retrieval-Augmented Generation) with the Constitution of the People's Republic of Bangladesh as the primary dataset. Built with FastAPI, Streamlit, and Google Gemini API.

## ✨ Features

- **🎯 High Accuracy**: Uses RAG with Google Gemini API for superior response quality
- **🌐 Bilingual Support**: Full English and Bangla language support with auto-detection
- **🏛️ Constitutional Focus**: Specialized in Constitution-based queries for maximum accuracy
- **📚 Citation Support**: Provides article references and legal disclaimers
- **🔍 Hybrid Search**: Combines semantic and keyword search for better retrieval
- **🚀 Multiple Interfaces**: REST API, Web UI (Streamlit), and CLI
- **🔄 Smart Fallback**: **NEW!** Automatic fallback to local FLAN-T5 model when Gemini API fails (network issues, timeouts, rate limits)
- **⚡ Zero Downtime**: Persistent fallback state ensures continuous operation even with API unavailability
- **🐳 Docker Support**: Easy deployment with Docker and docker-compose
- **🔒 Production-Ready**: Error handling, logging, rate limiting, and health checks

## 📁 Project Structure

```
law chatbot/
├── api.py                  # FastAPI REST API server
├── cli.py                  # Command-line interface
├── validate_env.py         # Environment validation utility
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose setup
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create from .env.example)
│
├── src/                    # Source code
│   ├── chatbot.py          # Main chatbot logic
│   ├── rag_pipeline.py     # RAG implementation
│   ├── data_processor.py   # Data extraction and preprocessing
│   ├── streamlit_app.py    # Streamlit web interface
│   └── services/           # Service modules
│       ├── embedding_service.py
│       ├── llm_service.py
│       ├── retrieval_service.py
│       └── vectorstore_service.py
│
├── config/                 # Configuration files
│   └── config.py           # Main configuration
│
├── data/                   # Dataset storage
│   ├── raw/               # Original Constitution PDFs
│   └── processed/         # Processed and chunked data
│
├── vectorstore/           # Vector database storage
│   └── constitution_faiss/
│
└── tests/                 # Test files
    ├── test_api.py
    └── test_*.py
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Git
- Google Gemini API key (free from [Google AI Studio](https://aistudio.google.com/app/apikey))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Mehedihasan444/law-chatbot.git
   cd law-chatbot
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy example environment file
   cp .env.example .env
   
   # Edit .env and add your API key
   # Get free API key: https://aistudio.google.com/app/apikey
   ```

5. **Validate configuration**
   ```bash
   python validate_env.py --auto-fix
   ```

6. **Process Constitution data** (first time only)
   ```bash
   # Download Constitution PDFs
   python src/data_processor.py --download
   
   # Process and create embeddings
   python src/data_processor.py --process
   ```

## 💻 Usage

### Option 1: Command Line Interface (CLI)

The easiest way to interact with the chatbot locally:

```bash
# Interactive mode
python cli.py

# Single query mode
python cli.py -q "What are the fundamental rights?"

# Bengali query
python cli.py -q "মৌলিক অধিকার কি?"

# Without LLM (faster)
python cli.py --no-llm

# With debug logging
python cli.py --debug
```

**CLI Commands:**
- `query <question>` - Ask a question
- `history` - Show conversation history
- `stats` - Display system statistics
- `clear` - Clear history
- `help` - Show help
- `exit` / `quit` - Exit

### Option 2: REST API

Start the FastAPI server for programmatic access:

```bash
# Start API server
python api.py

# With custom host/port
python api.py --host 0.0.0.0 --port 8000

# With auto-reload (development)
python api.py --reload
```

Access the API at `http://localhost:8000`

**API Documentation:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

**Example API Calls:**

```bash
# Health check
curl http://localhost:8000/health

# Query the Constitution
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the fundamental rights?",
    "use_llm": true
  }'

# Get statistics
curl http://localhost:8000/stats

# Get conversation history
curl http://localhost:8000/history?limit=10
```

**Python Client Example:**

```python
import requests

# Make a query
response = requests.post(
    "http://localhost:8000/query",
    json={
        "question": "What is Article 27?",
        "use_llm": True
    }
)

result = response.json()
print(result['answer'])
print(f"Sources: {result['num_sources']}")
```

### Option 3: Web Interface (Streamlit)

Launch the interactive web interface:

```bash
streamlit run src/streamlit_app.py
```

Access at `http://localhost:8501`

**Features:**
- 🎨 Beautiful, user-friendly interface
- 🌐 Language auto-detection
- 📊 Real-time statistics
- 📜 Conversation history
- 🔄 LLM toggle for response generation

### Option 4: Docker Deployment

Deploy with Docker for production:

```bash
# Build and run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Services:**
- API: `http://localhost:8000`
- Streamlit: `http://localhost:8501`

## 🔧 Configuration

All configuration is done through environment variables in the `.env` file:

```env
# Google Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# LLM Configuration
LLM_TYPE=gemini              # Options: gemini, local, openai
LLM_MODEL=gemini-1.5-flash   # Gemini model name

# Embedding Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Text Processing
CHUNK_SIZE=512               # Size of text chunks
CHUNK_OVERLAP=50             # Overlap between chunks
MAX_TOKENS=2048              # Maximum tokens for LLM
TEMPERATURE=0.1              # LLM temperature (0.0-2.0)
TOP_K_RETRIEVAL=5            # Number of documents to retrieve

# Vector Store
VECTOR_STORE_TYPE=faiss      # Vector database type
```

**Validation:**
```bash
# Validate your configuration
python validate_env.py

# Auto-create .env file
python validate_env.py --create-env
```

## 📚 Data Sources

- **English Constitution**: [WIPO - Bangladesh Constitution (EN)](https://wipolex-res.wipo.int/edocs/lexdocs/laws/en/bd/bd025en.pdf)
- **Bangla Constitution**: [WIPO - Bangladesh Constitution (BN)](https://wipolex-res.wipo.int/edocs/lexdocs/laws/bn/bd/bd025bn.pdf)
- **Official Portal**: [Ministry of Law, Bangladesh](http://bdlaws.minlaw.gov.bd/act-details-367.html)

**Constitution Version:** Constitution of Bangladesh (1972) with 17th Amendment (2018)

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run API tests only
pytest test_api.py -v

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test class
pytest test_api.py::TestQueryEndpoint -v
```

## 🐳 Docker Deployment

### Quick Start with Docker

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f api
docker-compose logs -f streamlit

# Restart a service
docker-compose restart api

# Stop all services
docker-compose down
```

### Building Custom Image

```bash
# Build image
docker build -t law-chatbot:latest .

# Run API only
docker run -p 8000:8000 \
  -e GEMINI_API_KEY=your_key \
  -v $(pwd)/data:/app/data \
  law-chatbot:latest

# Run Streamlit only
docker run -p 8501:8501 \
  -e GEMINI_API_KEY=your_key \
  law-chatbot:latest \
  streamlit run src/streamlit_app.py
```

### Production Deployment

For production, customize `docker-compose.yml`:

```yaml
services:
  api:
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    restart: always
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

## 🔍 Troubleshooting

### Common Issues and Solutions

#### 1. **"GEMINI_API_KEY not found"**
```bash
# Solution: Add API key to .env file
echo "GEMINI_API_KEY=your_actual_key" >> .env
python validate_env.py
```

#### 2. **"Failed to connect to Gemini API"**
- Check internet connection
- Verify API key is valid
- **System automatically falls back to local FLAN-T5 model** ✅
- No manual intervention needed!

#### 3. **"No processed data found"**
```bash
# Solution: Process the Constitution data
python src/data_processor.py --download
python src/data_processor.py --process
```

#### 4. **"Vector store not found"**
```bash
# Solution: Rebuild vector store
python -c "from src.rag_pipeline import ConstitutionRAG; from config.config import Config; rag = ConstitutionRAG(Config()); rag.initialize(force_rebuild=True)"
```

#### 5. **Slow API responses**
- Try disabling LLM: `use_llm: false` in API calls
- Use CLI with `--no-llm` flag
- Check network connectivity to Gemini API

#### 6. **Memory issues with local models**
- Local models require 4-8GB RAM
- Consider using Gemini API instead
- Reduce `MAX_TOKENS` in `.env`

## 🔄 Automatic Fallback Feature

**NEW!** The chatbot now features intelligent automatic fallback that ensures **zero downtime** even when Gemini API is unavailable.

### How It Works

```
Gemini API Available    ➔  Use Gemini (fast, high-quality)
     ↓ (fails)
Network Issue/Timeout   ➔  Auto-switch to Local Model
     ↓
Local FLAN-T5 Active    ➔  Continue serving requests
```

### Triggers Automatic Fallback

The system automatically switches to local model when:
- ⏰ **Timeout**: Gemini API takes >10 seconds
- 🌐 **Network Issues**: Connection failures, DNS errors
- 🔑 **API Errors**: Invalid key, rate limits (429), service unavailable (503)
- 💥 **Server Errors**: 500 errors, quota exceeded

### Fallback Performance

| Model | First Query | Subsequent Queries | Quality |
|-------|-------------|-------------------|---------|
| **Gemini API** | 5-10s | 5-10s | ⭐⭐⭐⭐⭐ |
| **Local FLAN-T5** (First) | 30-35s | 0.2-0.5s | ⭐⭐⭐⭐ |

### Testing Fallback

```bash
# Run comprehensive fallback tests
python test_auto_fallback.py

# Quick fallback test
python test_quick_fallback.py

# Manual test with invalid API key
export GEMINI_API_KEY="INVALID_KEY"
python cli.py
# System will automatically use local model
```

### Console Feedback

When fallback occurs, you'll see:
```
🌐 Attempting Gemini API call...
⏰ Gemini API call timed out (>10 seconds)
🔄 Automatically falling back to local model...
✅ Successfully switched to local model!
🏠 All subsequent queries will use local model
```

### Persistent Fallback

Once Gemini fails:
- ✅ System remembers the failure
- ✅ All future queries use local model directly
- ✅ No repeated Gemini retry attempts (saves time)
- ✅ Restart application to re-enable Gemini

**📚 Documentation:**
- Full details: [AUTOMATIC_FALLBACK.md](AUTOMATIC_FALLBACK.md)
- Implementation summary: [FALLBACK_SUMMARY.md](FALLBACK_SUMMARY.md)

### Getting Help

- 📖 Check [API Documentation](http://localhost:8000/docs) when server is running
- 🐛 Report issues on [GitHub Issues](https://github.com/Mehedihasan444/law-chatbot/issues)
- 💬 Join discussions on [GitHub Discussions](https://github.com/Mehedihasan444/law-chatbot/discussions)

## 🎯 Accuracy & Limitations

### Accuracy
- Based on Constitution of Bangladesh (1972) with 17th Amendment (2018)
- Designed for 95%+ accuracy on constitutional queries
- Includes proper citations and article references
- Provides legal disclaimers with all responses

### Limitations
- **Not Legal Advice**: This is an educational tool, not a substitute for legal counsel
- **Constitutional Scope**: Limited to Constitution-based queries only
- **Historical Context**: May not reflect very recent amendments or interpretations
- **Language Nuances**: Translation accuracy may vary for complex legal terms

### When to Consult a Lawyer
- For legal advice on specific situations
- For court proceedings or legal documentation
- For interpretation of recent amendments
- For matters requiring official legal opinion

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Types of Contributions

1. **Bug Reports**: Found a bug? [Open an issue](https://github.com/Mehedihasan444/law-chatbot/issues)
2. **Feature Requests**: Have an idea? Share it in [Discussions](https://github.com/Mehedihasan444/law-chatbot/discussions)
3. **Code Contributions**: Submit a pull request
4. **Documentation**: Improve docs, add examples
5. **Testing**: Add test cases, report edge cases

### Development Setup

```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/law-chatbot.git
cd law-chatbot

# Create a branch
git checkout -b feature/your-feature-name

# Make changes and test
pytest
python validate_env.py

# Commit and push
git commit -m "Add: your feature description"
git push origin feature/your-feature-name

# Open a Pull Request
```

### Code Guidelines

- Follow PEP 8 style guide
- Add docstrings to functions
- Write tests for new features
- Update documentation
- Ensure bilingual support (EN/BN)
- Maintain legal accuracy and citations

## 📋 API Reference

### Endpoints

#### `GET /` - Root
Returns API information and available endpoints.

#### `GET /health` - Health Check
Check system health and readiness.

**Response:**
```json
{
  "status": "healthy",
  "chatbot_ready": true,
  "timestamp": "2025-10-03T10:30:00",
  "version": "1.0.0",
  "system_info": {
    "queries_processed": 42,
    "system_status": "active"
  }
}
```

#### `POST /query` - Query Constitution
Ask questions about the Bangladesh Constitution.

**Request Body:**
```json
{
  "question": "What are the fundamental rights?",
  "use_llm": true,
  "language": "en"
}
```

**Response:**
```json
{
  "success": true,
  "question": "What are the fundamental rights?",
  "answer": "The Constitution guarantees several fundamental rights...",
  "language": "en",
  "scope": "constitutional",
  "num_sources": 5,
  "processing_time": 1.23,
  "timestamp": "2025-10-03T10:30:00",
  "sources": [...]
}
```

#### `GET /stats` - System Statistics
Get chatbot system statistics.

#### `GET /history?limit=10` - Conversation History
Retrieve recent conversation history.

#### `DELETE /history` - Clear History
Clear all conversation history.

#### `POST /initialize?force_rebuild=false` - Initialize/Reinitialize
Initialize or rebuild the chatbot system.

### Rate Limiting

Current implementation does not enforce rate limits, but recommended for production:
- 100 requests per minute per IP
- 1000 requests per day per API key (if using authentication)

## 🔒 Security & Privacy

### Data Privacy
- No conversation data is stored permanently
- Session data cleared on server restart
- No personal information is collected

### API Security
- CORS enabled for all origins (configure for production)
- Input validation on all endpoints
- Request size limits enforced
- No sensitive data in logs

### Production Recommendations
1. Use environment-specific `.env` files
2. Implement API key authentication
3. Enable rate limiting
4. Use HTTPS/TLS encryption
5. Configure specific CORS origins
6. Regular security audits
7. Monitor API usage

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Constitution text sourced from [WIPO](https://www.wipo.int/)
- Built with [LangChain](https://www.langchain.com/)
- Powered by [Google Gemini API](https://ai.google.dev/)
- Vector search by [FAISS](https://github.com/facebookresearch/faiss)
- Web UI with [Streamlit](https://streamlit.io/)

## 📞 Contact

- **Author**: Mehedi Hasan
- **GitHub**: [@Mehedihasan444](https://github.com/Mehedihasan444)
- **Repository**: [law-chatbot](https://github.com/Mehedihasan444/law-chatbot)

## ⚖️ Legal Compliance

This chatbot complies with:
- Bangladesh ICT Act 2006
- Constitutional provisions on digital information
- Educational and informational use guidelines

**Disclaimer**: This is an educational tool. For legal matters, consult qualified legal professionals licensed to practice in Bangladesh.

---

<div align="center">

**🏛️ Bangladesh Constitution Chatbot v1.0**

Made with ❤️ for legal education and accessibility

[🌟 Star this repo](https://github.com/Mehedihasan444/law-chatbot) | [🐛 Report Bug](https://github.com/Mehedihasan444/law-chatbot/issues) | [💡 Request Feature](https://github.com/Mehedihasan444/law-chatbot/issues)

</div>