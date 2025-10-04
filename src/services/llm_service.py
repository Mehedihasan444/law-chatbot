"""
LLM Service - Updated to support Google Gemini API
"""
import os
import sys
import logging
from typing import Optional, Any
import warnings
warnings.filterwarnings("ignore")

# Suppress Google API warnings
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"
logging.getLogger("google").setLevel(logging.ERROR)

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.config import Config

try:
    import google.generativeai as genai
    from langchain_google_genai import ChatGoogleGenerativeAI
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️ google-generativeai not available - Gemini API disabled")

# Fallback to local model if needed
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
    from langchain_huggingface import HuggingFacePipeline
    LOCAL_MODEL_AVAILABLE = True
except ImportError:
    LOCAL_MODEL_AVAILABLE = False
    print("⚠️ transformers not available - Local models disabled")


class LLMService:
    """Handles the loading and configuration of the Language Model."""
    
    def __init__(self, model_name: str = None, config: Config = None):
        self.config = config or Config()
        self.model_name = model_name or self.config.LLM_MODEL
        self.llm_type = self.config.LLM_TYPE
        self.llm = self._setup_llm()

    def _setup_llm(self):
        """Initializes the appropriate LLM based on configuration."""
        print(f"🔧 Initializing LLM service (type: {self.llm_type})")
        
        if self.llm_type == "gemini" and GEMINI_AVAILABLE:
            llm = self._setup_gemini_llm()
            if llm is not None:
                return llm
            else:
                print("⚠️ Gemini initialization failed, trying fallback options...")
                
        if self.llm_type == "local" and LOCAL_MODEL_AVAILABLE:
            return self._setup_local_llm()
        
        # Fallback logic
        print(f"⚠️ Primary LLM ({self.llm_type}) not available. Trying fallback options...")
        
        # Try fallback options in order of preference
        if GEMINI_AVAILABLE and self.config.GEMINI_API_KEY and self.llm_type != "gemini":
            print("🔄 Falling back to Gemini API...")
            llm = self._setup_gemini_llm()
            if llm is not None:
                self.llm_type = "gemini"  # Update the type
                return llm
                
        if LOCAL_MODEL_AVAILABLE:
            print("🔄 Falling back to local model...")
            llm = self._setup_local_llm()
            if llm is not None:
                self.llm_type = "local"  # Update the type
                return llm
        
        print("❌ No LLM available. Running in retrieval-only mode.")
        print("💡 Install required packages or check API keys for full functionality")
        return None

    def _setup_gemini_llm(self):
        """Initializes Google Gemini API with connectivity check."""
        if not self.config.GEMINI_API_KEY:
            print("❌ Error: GEMINI_API_KEY not found in environment variables")
            return None
        
        # Quick connectivity pre-check
        print("🔍 Checking network connectivity...")
        if not self._quick_connectivity_check():
            print("❌ Network connectivity issues detected, skipping Gemini initialization")
            return None
            
        try:
            print(f"Loading Gemini model: {self.model_name}...")
            
            # Configure the API key
            genai.configure(api_key=self.config.GEMINI_API_KEY)
            
            # Initialize the LangChain wrapper for Gemini with reasonable timeout settings
            llm = ChatGoogleGenerativeAI(
                model=self.model_name,
                google_api_key=self.config.GEMINI_API_KEY,
                temperature=self.config.TEMPERATURE,
                max_output_tokens=self.config.MAX_TOKENS,
                convert_system_message_to_human=True,
                # Reasonable timeout settings
                request_timeout=30,      # 30 seconds timeout
                max_retries=2,           # 2 retries
                transport="rest",        # Use REST for better timeout control
            )
            
            # Test connectivity with timeout using threading
            print("🔍 Testing Gemini API connectivity...")
            import threading
            import time
            
            test_result = {"success": False, "error": None}
            
            def test_connectivity():
                try:
                    test_response = llm.invoke("Test")
                    test_result["success"] = True
                except Exception as e:
                    test_result["error"] = str(e)
            
            # Start test in separate thread
            test_thread = threading.Thread(target=test_connectivity)
            test_thread.daemon = True  # Dies when main thread dies
            test_thread.start()
            
            # Wait for max 15 seconds for test
            test_thread.join(timeout=15)
            
            if test_thread.is_alive():
                print("❌ Connectivity test timed out (>15 seconds)")
                print("🌐 This indicates network connectivity issues")
                raise TimeoutError("Gemini API connectivity test timed out")
            elif test_result["success"]:
                print("✅ Gemini LLM loaded and tested successfully!")
                return llm
            else:
                error_msg = str(test_result['error'])
                if any(keyword in error_msg for keyword in ['failed to connect', '503', 'tcp handshaker', 'UNKNOWN', 'UNAVAILABLE']):
                    print("🌐 Network connectivity issue detected during test")
                raise Exception(f"Connectivity test failed: {error_msg}")
                
        except Exception as e:
            print(f"❌ Error loading Gemini model: {e}")
            print("🔄 Will attempt fallback to local model...")
            return None

    def _setup_local_llm(self):
        """Initializes a CPU-friendly seq2seq LLM (FLAN-T5) as fallback."""
        # Try different model sizes in order of preference
        model_candidates = [
            ("google/flan-t5-base", "FLAN-T5-Base (770M params)"),
            ("google/flan-t5-large", "FLAN-T5-Large (3B params)"),
            ("google/flan-t5-xl", "FLAN-T5-XL (11B params)")
        ]
        
        for model_name, description in model_candidates:
            print(f"🔄 Attempting to load {description}...")
            try:
                # Set low memory usage options
                import torch
                
                # Check available memory (basic check)
                if torch.cuda.is_available():
                    device = "cuda"
                    print("   Using GPU acceleration")
                else:
                    device = "cpu"
                    print("   Using CPU (may be slow for large models)")
                
                print(f"   Loading tokenizer for {model_name}...")
                tokenizer = AutoTokenizer.from_pretrained(
                    model_name,
                    cache_dir=".cache/huggingface"
                )
                
                print(f"   Loading model for {model_name}...")
                model = AutoModelForSeq2SeqLM.from_pretrained(
                    model_name,
                    torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                    device_map="auto" if device == "cuda" else None,
                    cache_dir=".cache/huggingface",
                    low_cpu_mem_usage=True
                )
                
                print(f"   Creating pipeline...")
                pipe = pipeline(
                    "text2text-generation",
                    model=model,
                    tokenizer=tokenizer,
                    device=0 if device == "cuda" else -1,
                    max_new_tokens=min(512, self.config.MAX_TOKENS),  # Reduced for stability
                    temperature=self.config.TEMPERATURE,
                    do_sample=True,
                    top_p=0.9,
                    top_k=40,
                    repetition_penalty=1.1,
                    length_penalty=1.0,
                    early_stopping=True
                    # Note: return_full_text is not applicable for text2text-generation
                )
                
                print(f"✅ Successfully loaded {description}")
                return HuggingFacePipeline(pipeline=pipe)
                
            except Exception as e:
                print(f"❌ Failed to load {description}: {str(e)[:100]}...")
                if "out of memory" in str(e).lower() or "segmentation fault" in str(e).lower():
                    print("   💡 Memory issue detected, trying smaller model...")
                    continue
                elif "not found" in str(e).lower():
                    print("   💡 Model not found, trying alternative...")
                    continue
                else:
                    print("   💡 Unknown error, trying next option...")
                    continue
        
        print("❌ All local model candidates failed")
        return None

    def get_llm(self):
        """Returns the loaded language model pipeline."""
        return self.llm
    
    def test_connectivity(self):
        """Test if the current LLM is working properly."""
        if not self.llm:
            return {"status": "no_llm", "message": "No LLM loaded"}
        
        try:
            if self.llm_type == "gemini":
                response = self.llm.invoke("Test connectivity")
                return {"status": "success", "message": "Gemini API working", "type": "gemini"}
            else:
                # For local models, use a shorter test prompt to avoid memory issues
                response = self.llm.invoke("Test")
                return {"status": "success", "message": "Local model working", "type": "local"}
        except Exception as e:
            error_msg = str(e)
            if "DNS resolution failed" in error_msg or "UNAVAILABLE" in error_msg:
                return {"status": "network_error", "message": "Network connectivity issue", "error": error_msg}
            elif "out of memory" in error_msg.lower() or "segmentation fault" in error_msg.lower():
                return {"status": "memory_error", "message": "Memory issue with local model", "error": error_msg}
            else:
                return {"status": "error", "message": "LLM test failed", "error": error_msg}
    
    def get_model_info(self):
        """Returns information about the currently loaded model."""
        connectivity = self.test_connectivity()
        return {
            "model_name": self.model_name,
            "llm_type": self.llm_type,
            "is_loaded": self.llm is not None,
            "gemini_available": GEMINI_AVAILABLE,
            "local_model_available": LOCAL_MODEL_AVAILABLE,
            "connectivity_status": connectivity
        }

    def _quick_connectivity_check(self):
        """Quick connectivity check to avoid hanging"""
        try:
            import socket
            # Try to connect to Google DNS with very short timeout
            socket.setdefaulttimeout(2)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
            return True
        except Exception:
            return False
