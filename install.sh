#!/bin/bash
# Installation script for Bangladesh Constitution Chatbot
# Works on Linux, Mac, and Git Bash on Windows

set -e  # Exit on error

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║     🏛️  BANGLADESH CONSTITUTION CHATBOT                         ║"
echo "║     Installation Script                                          ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "🔍 Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
required_version="3.10"

if ! python -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
    echo "❌ Error: Python 3.10 or higher is required"
    echo "   Current version: $python_version"
    echo "   Please install Python 3.10+ from https://www.python.org/"
    exit 1
fi
echo "✅ Python version: $python_version"

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python -m venv venv
    echo "✅ Virtual environment created"
else
    echo "ℹ️  Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "🔧 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi
echo "✅ Virtual environment activated"

# Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."
python -m pip install --upgrade pip --quiet
echo "✅ pip upgraded"

# Install dependencies
echo ""
echo "📚 Installing dependencies..."
echo "   This may take several minutes..."
pip install -r requirements.txt --quiet
echo "✅ Dependencies installed"

# Create .env file
echo ""
echo "🔐 Setting up environment variables..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Created .env file from .env.example"
        echo ""
        echo "⚠️  IMPORTANT: Edit .env and add your Gemini API key"
        echo "   Get a free key from: https://aistudio.google.com/app/apikey"
    else
        cat > .env << 'EOF'
# Google Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# LLM Configuration
LLM_TYPE=gemini
LLM_MODEL=gemini-1.5-flash

# Embedding Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Text Processing
CHUNK_SIZE=512
CHUNK_OVERLAP=50
MAX_TOKENS=2048
TEMPERATURE=0.1
TOP_K_RETRIEVAL=5

# Vector Store
VECTOR_STORE_TYPE=faiss
EOF
        echo "✅ Created .env file with defaults"
        echo "⚠️  IMPORTANT: Edit .env and add your Gemini API key"
    fi
else
    echo "ℹ️  .env file already exists"
fi

# Create necessary directories
echo ""
echo "📁 Creating directories..."
mkdir -p data/raw data/processed vectorstore logs
echo "✅ Directories created"

# Validate environment
echo ""
echo "🔍 Validating configuration..."
python validate_env.py || true

# Ask about data download
echo ""
read -p "📥 Do you want to download and process Constitution data now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "📥 Downloading Constitution PDFs..."
    python src/data_processor.py --download || echo "⚠️  Download failed - you can retry later"
    
    echo ""
    echo "⚙️  Processing data and creating embeddings..."
    python src/data_processor.py --process || echo "⚠️  Processing failed - you can retry later"
fi

# Installation complete
echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║     ✅ INSTALLATION COMPLETE!                                    ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
echo "🎯 Next Steps:"
echo ""
echo "1. Edit .env file and add your Gemini API key"
echo "   Get free key: https://aistudio.google.com/app/apikey"
echo ""
echo "2. Choose how to run:"
echo "   • CLI:       python cli.py"
echo "   • API:       python api.py"
echo "   • Web:       streamlit run src/streamlit_app.py"
echo "   • Docker:    docker-compose up -d"
echo ""
echo "3. Read documentation:"
echo "   • README.md - Complete guide"
echo "   • docs/QUICK_START.md - Quick reference"
echo ""
echo "📚 For help: python cli.py --help"
echo "🌐 API docs: http://localhost:8000/docs (after starting API)"
echo ""
echo "Happy chatting! 🎉"
