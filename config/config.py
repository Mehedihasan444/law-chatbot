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
    CPU_LLM_MODEL = os.getenv("CPU_LLM_MODEL", "google/flan-t5-xl")
    VECTOR_STORE_TYPE = os.getenv("VECTOR_STORE_TYPE", "faiss")
    
    # Text Processing (Optimized for flan-t5-xl)
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "768"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.2"))
    TOP_K_RETRIEVAL = int(os.getenv("TOP_K_RETRIEVAL", "3"))
    
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
    SYSTEM_PROMPT = """You are a knowledgeable legal assistant specializing in the Bangladesh Constitution. Your task is to provide clear, comprehensive, and educational answers about constitutional provisions.

Guidelines:
1. Provide complete, well-structured explanations in paragraph form
2. Start with a direct answer to the question
3. Include relevant article numbers and citations
4. Explain the significance and practical implications
5. Use clear, accessible language for general users
6. Always end with the legal disclaimer

Response Structure:
- Direct answer paragraph
- Detailed explanation with context
- Article citations
- Legal disclaimer"""

    USER_PROMPT_TEMPLATE = """Constitutional Information:
{context}

User Question: {question}

Instructions: Based on the constitutional provisions above, provide a comprehensive answer that:
1. Directly answers the user's question in clear language
2. Explains the constitutional provisions in context
3. Includes specific article references
4. Explains why these provisions matter
5. Uses paragraph format, not bullet points

Provide a detailed, educational response:"""

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