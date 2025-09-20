"""
Configuration management for Bangladesh Constitution Chatbot
"""
import os
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the chatbot"""
    
    # API Keys (Optional - only needed if using API-based models)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Model Configuration (CPU-friendly local models)
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    CPU_LLM_MODEL = os.getenv("CPU_LLM_MODEL", "google/flan-t5-base")
    VECTOR_STORE_TYPE = os.getenv("VECTOR_STORE_TYPE", "faiss")
    
    # Text Processing (Adjusted for CPU-friendly models)
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "400"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.1"))
    TOP_K_RETRIEVAL = int(os.getenv("TOP_K_RETRIEVAL", "5"))
    
    # Language Settings
    DEFAULT_LANGUAGE = "en"
    SUPPORTED_LANGUAGES = ["en"]
    
    # Data Sources - Bangladesh Constitution
    CONSTITUTION_EN_URL = os.getenv(
        "CONSTITUTION_EN_URL", 
        "https://constitutionnet.org/sites/default/files/2021-11/Constitution%20of%20Bangladesh%20%28English%29.pdf"
    )
    
    # File Paths
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(PROJECT_ROOT, "data")
    RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
    PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
    VECTORSTORE_DIR = os.path.join(PROJECT_ROOT, "vectorstore")
    
    # Prompts
    SYSTEM_PROMPT = """You are a legal assistant for the Bangladesh Constitution. Answer questions based only on the provided constitutional text.

Rules:
1. Use only the provided constitutional excerpts
2. Include article citations (e.g., "Article 27")
3. If information is not in the provided text, say so clearly
4. Keep answers concise and factual
5. Add disclaimer about legal advice

Format: Direct answer + article citation + legal disclaimer."""

    USER_PROMPT_TEMPLATE = """Context from Bangladesh Constitution:
{context}

Question: {question}

Based on the constitutional text above, provide a clear answer with article numbers. If the information is not sufficient, say so.

Answer:"""

    DISCLAIMER = """
⚠️ **Important Disclaimer**: This information is based on the Constitution of the People's Republic of Bangladesh and is for educational purposes only. This does not constitute legal advice. For legal matters, please consult qualified legal professionals.
"""

    # Text chunking patterns for Bangladesh Constitution
    ARTICLE_PATTERNS = [
        r"ARTICLE\s+\d+[A-Z]?",
        r"PART\s+[IVXLC]+",
        r"CHAPTER\s+[IVXLC]+",
        r"SCHEDULE\s+(FIRST|SECOND|THIRD|FOURTH|FIFTH|SIXTH|SEVENTH)"
    ]

    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Validate configuration and return status"""
        status = {
            "embedding_model": cls.EMBEDDING_MODEL,
            "cpu_llm_model": cls.CPU_LLM_MODEL,
            "vector_store": cls.VECTOR_STORE_TYPE,
            "openai_key_present": bool(cls.OPENAI_API_KEY),
            "data_dirs_exist": all([
                os.path.exists(cls.DATA_DIR),
                os.path.exists(cls.RAW_DATA_DIR),
                os.path.exists(cls.PROCESSED_DATA_DIR),
                os.path.exists(cls.VECTORSTORE_DIR)
            ]),
            "language": cls.DEFAULT_LANGUAGE,
            "chunk_size": cls.CHUNK_SIZE,
            "max_tokens": cls.MAX_TOKENS
        }
        return status

    @classmethod
    def get_supported_languages(cls) -> List[str]:
        """Get list of supported languages"""
        return cls.SUPPORTED_LANGUAGES

    @classmethod
    def is_language_supported(cls, language: str) -> bool:
        """Check if language is supported"""
        return language in cls.SUPPORTED_LANGUAGES