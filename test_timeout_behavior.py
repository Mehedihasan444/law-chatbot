"""
Test Timeout and Fallback Behavior
This tests if the new timeout mechanism works properly
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

def test_timeout_behavior():
    """Test if timeout works properly"""
    print("⏰ Testing Timeout and Fallback Behavior")
    print("=" * 50)
    
    config = Config()
    
    print("\n1️⃣ Testing with current network conditions...")
    try:
        import time
        start_time = time.time()
        
        llm_service = LLMService(config=config)
        
        initialization_time = time.time() - start_time
        print(f"   Initialization took: {initialization_time:.2f} seconds")
        
        if initialization_time > 15:
            print("   ❌ Initialization took too long - timeout may not be working")
        elif initialization_time < 10:
            print("   ✅ Quick initialization - likely successful connection")
        else:
            print("   ⚠️  Moderate time - may have used fallback")
        
        # Check model info
        model_info = llm_service.get_model_info()
        print(f"   Final Model Type: {model_info.get('llm_type', 'Unknown')}")
        print(f"   LLM Loaded: {model_info.get('is_loaded', False)}")
        
        connectivity = model_info.get('connectivity_status', {})
        print(f"   Connectivity Status: {connectivity.get('status', 'Unknown')}")
        
        if connectivity.get('status') == 'network_error':
            print("   🔄 Network error detected - fallback should have activated")
        elif connectivity.get('status') == 'success':
            print("   ✅ Connection successful")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n2️⃣ Testing with forced local model...")
    try:
        config.LLM_TYPE = "local"
        config.CPU_LLM_MODEL = "google/flan-t5-base"  # Use smaller model
        
        start_time = time.time()
        llm_service_local = LLMService(config=config)
        local_time = time.time() - start_time
        
        print(f"   Local model initialization: {local_time:.2f} seconds")
        
        model_info = llm_service_local.get_model_info()
        print(f"   Local Model Loaded: {model_info.get('is_loaded', False)}")
        
    except Exception as e:
        print(f"   ❌ Local model error: {e}")
    
    print(f"\n💡 Expected Behavior:")
    print(f"   • With good internet: <5 seconds, Gemini active")
    print(f"   • With poor internet: 8-15 seconds, fallback to local")
    print(f"   • Offline: 8-15 seconds, local model only")
    print(f"   • No models: <3 seconds, simple responses only")

if __name__ == "__main__":
    test_timeout_behavior()