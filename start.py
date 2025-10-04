"""
Startup Script for Bangladesh Constitution Chatbot
Handles initialization, validation, and service startup
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path

def print_banner():
    """Print startup banner"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║     🏛️  BANGLADESH CONSTITUTION CHATBOT                         ║
║     Starting up...                                               ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
""")

def check_python_version():
    """Check if Python version is adequate"""
    import sys
    if sys.version_info < (3, 10):
        print("❌ Error: Python 3.10 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import streamlit
        import langchain
        print("✅ Core dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("   Run: pip install -r requirements.txt")
        return False

def validate_environment():
    """Validate environment configuration"""
    print("\n🔍 Validating environment...")
    try:
        result = subprocess.run(
            [sys.executable, "validate_env.py"],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Environment validation failed: {e}")
        return False

def check_data_files():
    """Check if data files exist"""
    data_dir = Path("data/processed")
    if not data_dir.exists() or not list(data_dir.glob("*.json")):
        print("⚠️ Processed data files not found")
        print("   Run data processing:")
        print("   1. python src/data_processor.py --download")
        print("   2. python src/data_processor.py --process")
        return False
    print("✅ Data files found")
    return True

def check_vectorstore():
    """Check if vector store exists"""
    vectorstore_dir = Path("vectorstore/constitution_faiss")
    if not vectorstore_dir.exists() or not list(vectorstore_dir.glob("*")):
        print("⚠️ Vector store not found - will be created on first run")
        return False
    print("✅ Vector store found")
    return True

def start_api_server(host="0.0.0.0", port=8000, reload=False):
    """Start FastAPI server"""
    print(f"\n🚀 Starting API server on {host}:{port}")
    try:
        cmd = [sys.executable, "api.py", "--host", host, "--port", str(port)]
        if reload:
            cmd.append("--reload")
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 API server stopped")
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")

def start_streamlit(port=8501):
    """Start Streamlit app"""
    print(f"\n🎨 Starting Streamlit app on port {port}")
    try:
        cmd = [
            sys.executable, "-m", "streamlit", "run",
            "src/streamlit_app.py",
            "--server.port", str(port),
            "--server.address", "0.0.0.0"
        ]
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 Streamlit app stopped")
    except Exception as e:
        print(f"❌ Failed to start Streamlit: {e}")

def start_cli():
    """Start CLI interface"""
    print("\n💬 Starting CLI interface")
    try:
        subprocess.run([sys.executable, "cli.py"])
    except KeyboardInterrupt:
        print("\n👋 CLI stopped")
    except Exception as e:
        print(f"❌ Failed to start CLI: {e}")

def setup_project():
    """Set up the project for first time"""
    print("\n🔧 Setting up project...")
    
    # Create .env if it doesn't exist
    if not os.path.exists(".env"):
        print("Creating .env file...")
        subprocess.run([sys.executable, "validate_env.py", "--create-env"])
    
    # Install dependencies if needed
    try:
        import fastapi
    except ImportError:
        print("Installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Download and process data if needed
    if not check_data_files():
        response = input("Download and process Constitution data? (y/n): ")
        if response.lower() == 'y':
            print("Downloading data...")
            subprocess.run([sys.executable, "src/data_processor.py", "--download"])
            print("Processing data...")
            subprocess.run([sys.executable, "src/data_processor.py", "--process"])
    
    print("✅ Setup complete!")

def main():
    """Main startup function"""
    parser = argparse.ArgumentParser(description="Bangladesh Constitution Chatbot Startup")
    parser.add_argument("mode", choices=["api", "streamlit", "cli", "setup", "check"],
                       help="Mode to run: api, streamlit, cli, setup, or check")
    parser.add_argument("--host", default="0.0.0.0", help="Host for API server")
    parser.add_argument("--port", type=int, default=8000, help="Port for API server")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    parser.add_argument("--skip-checks", action="store_true", help="Skip validation checks")
    
    args = parser.parse_args()
    
    print_banner()
    
    # Run checks unless skipped
    if not args.skip_checks and args.mode != "setup":
        print("🔍 Running system checks...\n")
        
        if not check_python_version():
            return 1
        
        if not check_dependencies():
            return 1
        
        if args.mode != "check":
            validate_environment()
            check_data_files()
            check_vectorstore()
    
    # Execute requested mode
    if args.mode == "api":
        start_api_server(args.host, args.port, args.reload)
    elif args.mode == "streamlit":
        start_streamlit(args.port if args.port != 8000 else 8501)
    elif args.mode == "cli":
        start_cli()
    elif args.mode == "setup":
        setup_project()
    elif args.mode == "check":
        print("\n✅ All checks completed")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
