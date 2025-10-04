"""
Quick Fallback Test for Bangladesh Constitution Chatbot
Run this to test if fallbacks are working in the live system
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
from chatbot import ConstitutionChatbot

def test_live_fallback():
    """Test fallback in actual chatbot instance"""
    print("🧪 Testing Live Fallback Mechanism")
    print("=" * 40)
    
    try:
        config = Config()
        chatbot = ConstitutionChatbot(config)
        
        if not chatbot.is_ready():
            print("❌ Chatbot not ready")
            return
        
        # Test normal query
        print("\n1️⃣ Testing normal query...")
        result1 = chatbot.process_query("What is Article 27?", use_llm=True)
        print(f"   Response length: {len(result1['answer'])}")
        print(f"   Sources found: {result1['num_sources']}")
        print(f"   Fallback used: {result1.get('fallback_used', 'Unknown')}")
        
        # Test with LLM disabled
        print("\n2️⃣ Testing with LLM disabled...")
        result2 = chatbot.process_query("What is Article 27?", use_llm=False)
        print(f"   Response length: {len(result2['answer'])}")
        print(f"   Sources found: {result2['num_sources']}")
        print(f"   Fallback used: {result2.get('fallback_used', 'Unknown')}")
        
        # Test system status
        print("\n3️⃣ System status check...")
        if hasattr(chatbot, 'rag_system') and chatbot.rag_system:
            if hasattr(chatbot.rag_system, 'llm_service'):
                model_info = chatbot.rag_system.llm_service.get_model_info()
                print(f"   LLM Type: {model_info.get('llm_type', 'Unknown')}")
                print(f"   LLM Loaded: {model_info.get('is_loaded', False)}")
                
                connectivity = model_info.get('connectivity_status', {})
                print(f"   Connectivity: {connectivity.get('status', 'Unknown')}")
        
        print(f"\n✅ Test completed successfully")
        print(f"💡 Both queries should work, with fallback mechanisms as needed")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_live_fallback()