@echo off
REM Installation script for Bangladesh Constitution Chatbot (Windows)

echo ================================================================
echo.
echo      Bangladesh Constitution Chatbot - Installation
echo.
echo ================================================================
echo.

REM Check Python
echo Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)

python -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.10 or higher is required
    python --version
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PY_VERSION=%%i
echo Python version: %PY_VERSION%
echo.

REM Create virtual environment
echo Creating virtual environment...
if not exist venv (
    python -m venv venv
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip --quiet
echo pip upgraded
echo.

REM Install dependencies
echo Installing dependencies...
echo This may take several minutes...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo WARNING: Some dependencies failed to install
    echo You may need to install them manually
) else (
    echo Dependencies installed successfully
)
echo.

REM Create .env file
echo Setting up environment variables...
if not exist .env (
    if exist .env.example (
        copy .env.example .env >nul
        echo Created .env file from .env.example
    ) else (
        (
            echo # Google Gemini API Configuration
            echo GEMINI_API_KEY=your_gemini_api_key_here
            echo.
            echo # LLM Configuration
            echo LLM_TYPE=gemini
            echo LLM_MODEL=gemini-1.5-flash
            echo.
            echo # Embedding Model
            echo EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
            echo.
            echo # Text Processing
            echo CHUNK_SIZE=512
            echo CHUNK_OVERLAP=50
            echo MAX_TOKENS=2048
            echo TEMPERATURE=0.1
            echo TOP_K_RETRIEVAL=5
            echo.
            echo # Vector Store
            echo VECTOR_STORE_TYPE=faiss
        ) > .env
        echo Created .env file with defaults
    )
    echo.
    echo IMPORTANT: Edit .env and add your Gemini API key
    echo Get a free key from: https://aistudio.google.com/app/apikey
) else (
    echo .env file already exists
)
echo.

REM Create directories
echo Creating directories...
if not exist data\raw mkdir data\raw
if not exist data\processed mkdir data\processed
if not exist vectorstore mkdir vectorstore
if not exist logs mkdir logs
echo Directories created
echo.

REM Validate environment
echo Validating configuration...
python validate_env.py
echo.

REM Ask about data download
set /p DOWNLOAD="Do you want to download and process Constitution data now? (y/n): "
if /i "%DOWNLOAD%"=="y" (
    echo.
    echo Downloading Constitution PDFs...
    python src\data_processor.py --download
    
    echo.
    echo Processing data and creating embeddings...
    python src\data_processor.py --process
)

REM Installation complete
echo.
echo ================================================================
echo.
echo      INSTALLATION COMPLETE!
echo.
echo ================================================================
echo.
echo Next Steps:
echo.
echo 1. Edit .env file and add your Gemini API key
echo    Get free key: https://aistudio.google.com/app/apikey
echo.
echo 2. Choose how to run:
echo    * CLI:       python cli.py
echo    * API:       python api.py
echo    * Web:       streamlit run src\streamlit_app.py
echo    * Docker:    docker-compose up -d
echo.
echo 3. Read documentation:
echo    * README.md - Complete guide
echo    * docs/QUICK_START.md - Quick reference
echo.
echo For help: python cli.py --help
echo API docs: http://localhost:8000/docs (after starting API)
echo.
echo Happy chatting!
echo.
pause
