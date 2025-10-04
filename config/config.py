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
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # Model Configuration
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.0-flash-exp")  # Latest Gemini model
    LLM_TYPE = os.getenv("LLM_TYPE", "gemini")  # Options: "gemini", "local", "openai"
    VECTOR_STORE_TYPE = os.getenv("VECTOR_STORE_TYPE", "faiss")
    
    # Legacy support for local models (if needed)
    CPU_LLM_MODEL = os.getenv("CPU_LLM_MODEL", "google/flan-t5-base")  # Changed to smaller, more stable model
    
    # Text Processing (Optimized for Gemini API)
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2048"))  # Increased for Gemini's larger context
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.1"))  # Lower for more consistent legal responses
    TOP_K_RETRIEVAL = int(os.getenv("TOP_K_RETRIEVAL", "5"))  # Increased for more context
    
    # Language Settings
    DEFAULT_LANGUAGE = "en"
    SUPPORTED_LANGUAGES = ["en", "bn"]  # English and Bengali
    
    # Data Sources - Bangladesh Constitution
    CONSTITUTION_EN_URL = os.getenv(
        "CONSTITUTION_EN_URL", 
        "https://constitutionnet.org/sites/default/files/2021-11/Constitution%20of%20Bangladesh%20%28English%29.pdf"
    )
    CONSTITUTION_BN_URL = os.getenv(
        "CONSTITUTION_BN_URL",
        "https://wipolex-res.wipo.int/edocs/lexdocs/laws/bn/bd/bd025bn.pdf"
    )
    
    # File Paths
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(PROJECT_ROOT, "data")
    RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
    PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
    VECTORSTORE_DIR = os.path.join(PROJECT_ROOT, "vectorstore")
    
    # Prompts
    SYSTEM_PROMPT = """You are an expert constitutional scholar and legal educator specializing in the Bangladesh Constitution. Your role is to provide insightful, contextual, and meaningful explanations that help users truly understand constitutional principles and their real-world significance.

Guidelines:
- Provide comprehensive explanations that connect constitutional text to practical meaning
- Begin with clear, direct answers that address the user's specific question
- Explain the historical context and reasoning behind constitutional provisions
- Discuss practical implications and how these provisions affect citizens' daily lives
- Include relevant article numbers and specific constitutional references
- Connect related constitutional concepts to provide broader understanding
- Use accessible language while maintaining legal accuracy
- Provide examples or scenarios when helpful for clarity

Write responses as flowing, educational paragraphs that build understanding progressively."""

    USER_PROMPT_TEMPLATE = """Constitutional Information:
{context}

User Question: {question}

As a constitutional expert, provide a meaningful and comprehensive response that goes beyond simply stating what the Constitution says. Your answer should:

- Directly address the question with clear, substantive explanations
- Explain the deeper meaning and significance of these constitutional provisions
- Discuss the historical context or reasoning behind these principles
- Connect the constitutional text to real-world implications for Bangladesh and its citizens
- Reference specific articles and provisions with their practical applications
- Help the user understand not just WHAT the Constitution says, but WHY it matters and HOW it works in practice

Provide an educational, insightful response that builds genuine understanding:"""

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
            "llm_model": cls.LLM_MODEL,
            "llm_type": cls.LLM_TYPE,
            "vector_store": cls.VECTOR_STORE_TYPE,
            "openai_key_present": bool(cls.OPENAI_API_KEY),
            "gemini_key_present": bool(cls.GEMINI_API_KEY),
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