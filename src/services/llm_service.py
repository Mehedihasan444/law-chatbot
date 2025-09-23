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
        if self.llm_type == "gemini" and GEMINI_AVAILABLE:
            return self._setup_gemini_llm()
        elif self.llm_type == "local" and LOCAL_MODEL_AVAILABLE:
            return self._setup_local_llm()
        else:
            print(f"Warning: {self.llm_type} LLM not available. Trying fallback options...")
            
            # Try fallback options
            if GEMINI_AVAILABLE and self.config.GEMINI_API_KEY:
                print("Falling back to Gemini API...")
                return self._setup_gemini_llm()
            elif LOCAL_MODEL_AVAILABLE:
                print("Falling back to local model...")
                return self._setup_local_llm()
            else:
                print("Warning: No LLM available. Running in retrieval-only mode.")
                return None

    def _setup_gemini_llm(self):
        """Initializes Google Gemini API."""
        if not self.config.GEMINI_API_KEY:
            print("❌ Error: GEMINI_API_KEY not found in environment variables")
            return None
            
        try:
            print(f"Loading Gemini model: {self.model_name}...")
            
            # Configure the API key
            genai.configure(api_key=self.config.GEMINI_API_KEY)
            
            # Initialize the LangChain wrapper for Gemini
            llm = ChatGoogleGenerativeAI(
                model=self.model_name,
                google_api_key=self.config.GEMINI_API_KEY,
                temperature=self.config.TEMPERATURE,
                max_output_tokens=self.config.MAX_TOKENS,
                convert_system_message_to_human=True  # For better system prompt handling
            )
            
            print("✅ Gemini LLM loaded successfully!")
            return llm
            
        except Exception as e:
            print(f"❌ Error loading Gemini model: {e}")
            return None

    def _setup_local_llm(self):
        """Initializes a CPU-friendly seq2seq LLM (FLAN-T5) as fallback."""
        model_name = self.config.CPU_LLM_MODEL
        print(f"Loading local language model: {model_name}...")
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

            pipe = pipeline(
                "text2text-generation",
                model=model,
                tokenizer=tokenizer,
                max_new_tokens=min(1024, self.config.MAX_TOKENS),
                temperature=self.config.TEMPERATURE,
                do_sample=True,
                top_p=0.9,
                top_k=40,
                repetition_penalty=1.15,
                length_penalty=1.2,
                early_stopping=False
            )
            return HuggingFacePipeline(pipeline=pipe)
        except Exception as e:
            print(f"❌ Error loading local language model: {e}")
            return None

    def get_llm(self):
        """Returns the loaded language model pipeline."""
        return self.llm
    
    def get_model_info(self):
        """Returns information about the currently loaded model."""
        return {
            "model_name": self.model_name,
            "llm_type": self.llm_type,
            "is_loaded": self.llm is not None,
            "gemini_available": GEMINI_AVAILABLE,
            "local_model_available": LOCAL_MODEL_AVAILABLE
        }
