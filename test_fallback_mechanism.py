"""
Test Fallback Mechanism for Bangladesh Constitution Chatbot
This script tests the fallback behavior under different failure scenarios.
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "src"))

from dotenv import load_dotenv
load_dotenv()

# Suppress warnings
import warnings
warnings.filterwarnings("ignore")
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"

from config.config import Config
from services.llm_service import LLMService

def test_fallback_scenarios():
    """Test different fallback scenarios"""
    print("🧪 Testing Fallback Mechanisms")
    print("=" * 50)
    
    config = Config()
    
    # Test 1: Normal operation
    print("\n1️⃣ TEST: Normal Gemini API operation")
    try:
        llm_service = LLMService(config=config)
        model_info = llm_service.get_model_info()
        print(f"   Model Type: {model_info['llm_type']}")
        print(f"   Is Loaded: {model_info['is_loaded']}")
        print(f"   Connectivity: {model_info['connectivity_status']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Missing API key
    print("\n2️⃣ TEST: Missing API Key")
    try:
        # Temporarily remove API key
        original_key = config.GEMINI_API_KEY
        config.GEMINI_API_KEY = None
        
        llm_service = LLMService(config=config)
        model_info = llm_service.get_model_info()
        print(f"   Model Type: {model_info['llm_type']}")
        print(f"   Is Loaded: {model_info['is_loaded']}")
        print(f"   Expected: Should fallback to local model")
        
        # Restore API key
        config.GEMINI_API_KEY = original_key
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Force local model with safety checks
    print("\n3️⃣ TEST: Force Local Model (with memory safety)")
    try:
        import psutil
        import gc
        
        # Check available memory
        memory = psutil.virtual_memory()
        available_gb = memory.available / (1024**3)
        print(f"   Available RAM: {available_gb:.1f} GB")
        
        if available_gb < 4:
            print("   ⚠️  Warning: Low memory detected, using base model")
            config.CPU_LLM_MODEL = "google/flan-t5-base"
        
        config.LLM_TYPE = "local"
        
        # Force garbage collection before loading
        gc.collect()
        
        llm_service = LLMService(config=config)
        model_info = llm_service.get_model_info()
        print(f"   Model Type: {model_info['llm_type']}")
        print(f"   Is Loaded: {model_info['is_loaded']}")
        print(f"   Expected: Should use local FLAN-T5 model")
        
        # Test connectivity if loaded
        if model_info['is_loaded']:
            connectivity = model_info.get('connectivity_status', {})
            print(f"   Connectivity Test: {connectivity.get('status', 'unknown')}")
        
    except ImportError:
        print("   ⚠️  psutil not available, skipping memory check")
        try:
            config.LLM_TYPE = "local"
            config.CPU_LLM_MODEL = "google/flan-t5-base"  # Use safer base model
            llm_service = LLMService(config=config)
            model_info = llm_service.get_model_info()
            print(f"   Model Type: {model_info['llm_type']}")
            print(f"   Is Loaded: {model_info['is_loaded']}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print(f"   💡 This might be a memory issue - try using google/flan-t5-base instead")
    
    # Test 4: Test simple response generation (retrieval-only)
    print("\n4️⃣ TEST: Simple Response Generation")
    try:
        from rag_pipeline import ConstitutionRAG
        
        config.LLM_TYPE = "gemini"  # Reset
        rag = ConstitutionRAG(config)
        
        # Initialize the system
        if rag.initialize():
            # Test simple response (without LLM)
            test_query = "What is Article 27?"
            relevant_docs = rag.retrieve_relevant_chunks(test_query)
            context = rag.format_context(relevant_docs)
            
            # Force simple response generation
            simple_response = rag.generate_response_simple(test_query, context)
            print(f"   Simple Response Generated: {len(simple_response)} characters")
            print(f"   Response Preview: {simple_response[:100]}...")
        else:
            print("   ❌ Failed to initialize RAG system")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Fallback mechanism test completed")

def test_network_simulation():
    """Simulate network failure scenarios"""
    print("\n🌐 Network Failure Simulation")
    print("=" * 30)
    
    # This would require actually disconnecting or using a mock
    # For now, just show what would happen
    print("💡 To test network failures:")
    print("   1. Disconnect internet")
    print("   2. Run: python test_fallback_mechanism.py")
    print("   3. Expected: Should fallback to local model")
    print("   4. If no local model: Should use simple responses")

if __name__ == "__main__":
    test_fallback_scenarios()
    test_network_simulation()