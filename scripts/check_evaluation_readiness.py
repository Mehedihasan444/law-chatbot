"""
Pre-flight check script to verify system is ready for paper evaluation
Run this before executing run_paper_evaluation.py
"""

import os
import sys
from pathlib import Path

# Ensure project root is on the path (this file lives in scripts/)
sys.path.insert(0, str(Path(__file__).parent.parent))


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80)


def check_dependencies():
    """Check if all required packages are installed"""
    print_header("CHECKING DEPENDENCIES")
    
    required_packages = {
        'langchain': 'LangChain framework',
        'google.generativeai': 'Google Gemini API',
        'faiss': 'FAISS vector store',
        'sentence_transformers': 'Sentence transformers',
        'streamlit': 'Streamlit UI',
        'fastapi': 'FastAPI server',
        'sklearn': 'Scikit-learn (evaluation)',
        'matplotlib': 'Matplotlib (plotting)',
        'seaborn': 'Seaborn (visualization)',
        'pandas': 'Pandas (data handling)',
        'numpy': 'NumPy (numerical)',
    }
    
    missing = []
    installed = []
    
    for package, description in required_packages.items():
        try:
            __import__(package)
            installed.append(f"✅ {package:25s} - {description}")
        except ImportError:
            missing.append(f"❌ {package:25s} - {description}")
    
    for pkg in installed:
        print(pkg)
    
    if missing:
        print("\n⚠️  MISSING PACKAGES:")
        for pkg in missing:
            print(pkg)
        print("\nInstall missing packages:")
        print("  pip install scikit-learn matplotlib seaborn pandas numpy")
        return False
    
    print("\n✅ All required packages installed")
    return True


def check_environment():
    """Check environment variables"""
    print_header("CHECKING ENVIRONMENT VARIABLES")
    
    env_file = Path('.env')
    
    if not env_file.exists():
        print("❌ .env file not found")
        print("   Create .env file with required variables")
        return False
    
    print("✅ .env file exists")
    
    # Load and check critical variables
    from dotenv import load_dotenv
    load_dotenv()
    
    critical_vars = {
        'GEMINI_API_KEY': 'Google Gemini API key',
        'LLM_TYPE': 'LLM type (should be "gemini")',
    }
    
    optional_vars = {
        'OPENAI_API_KEY': 'OpenAI API key (optional)',
        'PINECONE_API_KEY': 'Pinecone API key (optional)',
    }
    
    missing_critical = []
    
    for var, description in critical_vars.items():
        value = os.getenv(var)
        if value:
            masked_value = f"{value[:10]}..." if len(value) > 10 else "***"
            print(f"✅ {var:20s} = {masked_value}")
        else:
            print(f"❌ {var:20s} - MISSING ({description})")
            missing_critical.append(var)
    
    print("\nOptional variables:")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            masked_value = f"{value[:10]}..." if len(value) > 10 else "***"
            print(f"ℹ️  {var:20s} = {masked_value}")
        else:
            print(f"⚪ {var:20s} - Not set ({description})")
    
    if missing_critical:
        print(f"\n❌ Missing critical environment variables: {', '.join(missing_critical)}")
        return False
    
    print("\n✅ All critical environment variables set")
    return True


def check_data_files():
    """Check if required data files exist"""
    print_header("CHECKING DATA FILES")
    
    required_files = {
        'config/config.py': 'Configuration file',
        'src/chatbot.py': 'Main chatbot module',
        'src/rag_pipeline.py': 'RAG pipeline',
        'src/services/embedding_service.py': 'Embedding service',
        'src/services/llm_service.py': 'LLM service',
        'src/services/vectorstore_service.py': 'Vectorstore service',
    }
    
    optional_files = {
        'vectorstore/constitution_faiss/index.faiss': 'FAISS vector index',
        'data/processed/all_chunks.json': 'Processed chunks',
    }
    
    missing_critical = []
    
    for file_path, description in required_files.items():
        if Path(file_path).exists():
            print(f"✅ {file_path:45s} - {description}")
        else:
            print(f"❌ {file_path:45s} - MISSING ({description})")
            missing_critical.append(file_path)
    
    print("\nOptional files:")
    for file_path, description in optional_files.items():
        if Path(file_path).exists():
            print(f"✅ {file_path:45s} - {description}")
        else:
            print(f"⚪ {file_path:45s} - Not found ({description})")
    
    if missing_critical:
        print(f"\n❌ Missing critical files")
        return False
    
    print("\n✅ All critical files present")
    return True


def check_chatbot():
    """Check if chatbot can initialize"""
    print_header("TESTING CHATBOT INITIALIZATION")
    
    try:
        from config.config import Config
        from src.chatbot import ConstitutionChatbot
        
        print("Loading configuration...")
        config = Config()
        print("✅ Configuration loaded")
        
        print("\nInitializing chatbot...")
        chatbot = ConstitutionChatbot(config)
        print("✅ Chatbot initialized")
        
        if chatbot.is_ready():
            print("✅ Chatbot is ready")
            
            # Test basic functionality
            print("\nTesting language detection...")
            lang_en = chatbot.detect_language("What is Article 7?")
            lang_bn = chatbot.detect_language("সংবিধান কি?")
            print(f"  English detection: {lang_en}")
            print(f"  Bengali detection: {lang_bn}")
            
            if lang_en == 'en' and lang_bn == 'bn':
                print("✅ Language detection working")
            else:
                print("⚠️  Language detection may have issues")
            
            print("\nTesting scope validation...")
            in_scope = chatbot.is_constitutional_query("What are fundamental rights?")
            out_scope = chatbot.is_constitutional_query("What is the weather?")
            print(f"  Constitutional query: {in_scope}")
            print(f"  Non-constitutional query: {out_scope}")
            
            if in_scope and not out_scope:
                print("✅ Scope validation working")
            else:
                print("⚠️  Scope validation may have issues")
            
            return True
        else:
            print("⚠️  Chatbot initialized but not fully ready")
            print("   This may be normal if vectorstore is not built")
            return True
            
    except Exception as e:
        print(f"❌ Error initializing chatbot: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def check_evaluation_files():
    """Check if evaluation system files exist"""
    print_header("CHECKING EVALUATION SYSTEM FILES")
    
    eval_files = {
        'paper_evaluation_system.py': 'Core evaluation system',
        'run_paper_evaluation.py': 'Evaluation runner with test data',
        'PAPER_EVALUATION_GUIDE.md': 'Usage guide',
        'REVIEWER_COMMENTS_RESPONSE.md': 'Reviewer response guide',
    }
    
    all_present = True
    
    for file_path, description in eval_files.items():
        if Path(file_path).exists():
            print(f"✅ {file_path:40s} - {description}")
        else:
            print(f"❌ {file_path:40s} - MISSING ({description})")
            all_present = False
    
    if all_present:
        print("\n✅ All evaluation system files present")
    else:
        print("\n❌ Some evaluation files missing")
    
    return all_present


def check_output_directory():
    """Check/create output directory"""
    print_header("CHECKING OUTPUT DIRECTORY")
    
    output_dir = Path('paper/paper_evaluation_results')
    
    if output_dir.exists():
        print(f"⚠️  Output directory already exists: {output_dir}")
        print("   Previous results will be overwritten")
        
        # Count existing files
        figures = list((output_dir / 'figures').glob('*')) if (output_dir / 'figures').exists() else []
        tables = list((output_dir / 'tables').glob('*')) if (output_dir / 'tables').exists() else []
        data = list((output_dir / 'data').glob('*')) if (output_dir / 'data').exists() else []
        
        if figures or tables or data:
            print(f"\n   Existing files:")
            print(f"     Figures: {len(figures)}")
            print(f"     Tables: {len(tables)}")
            print(f"     Data files: {len(data)}")
    else:
        print(f"✅ Output directory will be created: {output_dir}")
    
    return True


def main():
    """Run all checks"""
    print("="*80)
    print("  PAPER EVALUATION SYSTEM - PRE-FLIGHT CHECK")
    print("  Bangladesh Constitution Chatbot")
    print("="*80)
    
    checks = [
        ("Dependencies", check_dependencies),
        ("Environment", check_environment),
        ("Data Files", check_data_files),
        ("Evaluation Files", check_evaluation_files),
        ("Output Directory", check_output_directory),
        ("Chatbot", check_chatbot),
    ]
    
    results = {}
    
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"\n❌ Error during {check_name} check: {str(e)}")
            results[check_name] = False
    
    # Summary
    print_header("SUMMARY")
    
    all_passed = True
    for check_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status:10s} - {check_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*80)
    if all_passed:
        print("✅ ALL CHECKS PASSED - READY TO RUN EVALUATION")
        print("="*80)
        print("\nNext step:")
        print("  python run_paper_evaluation.py")
    else:
        print("❌ SOME CHECKS FAILED - FIX ISSUES BEFORE RUNNING")
        print("="*80)
        print("\nResolve the issues above, then run this script again.")
    print("="*80)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
