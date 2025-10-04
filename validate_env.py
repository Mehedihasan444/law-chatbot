"""
Environment Validator for Bangladesh Constitution Chatbot
Validates .env configuration and provides helpful error messages
"""
import os
from pathlib import Path
from typing import Dict, List, Tuple
from dotenv import load_dotenv

class EnvironmentValidator:
    """Validates environment configuration"""
    
    def __init__(self, env_file: str = ".env"):
        self.env_file = env_file
        self.errors = []
        self.warnings = []
        self.info = []
        
    def validate(self) -> Tuple[bool, Dict]:
        """
        Validate environment configuration
        Returns: (is_valid, report)
        """
        # Check if .env file exists
        if not os.path.exists(self.env_file):
            self.warnings.append(f"⚠️ .env file not found at {self.env_file}")
            self.info.append("💡 Copy .env.example to .env and configure it")
            
            # Try to load from environment variables anyway
            load_dotenv()
        else:
            # Load .env file
            load_dotenv(self.env_file)
            self.info.append(f"✅ Loaded .env file from {self.env_file}")
        
        # Validate API keys
        self._validate_api_keys()
        
        # Validate model configuration
        self._validate_model_config()
        
        # Validate paths
        self._validate_paths()
        
        # Validate numeric settings
        self._validate_numeric_settings()
        
        # Generate report
        report = {
            "is_valid": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info,
            "can_run": self._can_run()
        }
        
        return len(self.errors) == 0, report
    
    def _validate_api_keys(self):
        """Validate API keys"""
        gemini_key = os.getenv("GEMINI_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        
        if not gemini_key and not openai_key:
            self.warnings.append("⚠️ No API keys found (GEMINI_API_KEY or OPENAI_API_KEY)")
            self.info.append("💡 The system will run with local models only (limited functionality)")
            self.info.append("💡 Get a free Gemini API key: https://aistudio.google.com/app/apikey")
        elif gemini_key:
            if gemini_key.startswith("your_") or len(gemini_key) < 20:
                self.warnings.append("⚠️ GEMINI_API_KEY appears to be a placeholder")
                self.info.append("💡 Replace with your actual API key from https://aistudio.google.com/app/apikey")
            else:
                self.info.append("✅ GEMINI_API_KEY is configured")
        elif openai_key:
            if openai_key.startswith("your_") or openai_key.startswith("sk-proj-"):
                self.warnings.append("⚠️ OPENAI_API_KEY may be invalid")
            else:
                self.info.append("✅ OPENAI_API_KEY is configured")
    
    def _validate_model_config(self):
        """Validate model configuration"""
        llm_type = os.getenv("LLM_TYPE", "gemini")
        llm_model = os.getenv("LLM_MODEL", "gemini-1.5-flash")
        embedding_model = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        
        # Validate LLM type
        valid_llm_types = ["gemini", "local", "openai"]
        if llm_type not in valid_llm_types:
            self.errors.append(f"❌ Invalid LLM_TYPE: {llm_type}. Must be one of: {valid_llm_types}")
        else:
            self.info.append(f"✅ LLM_TYPE: {llm_type}")
        
        # Validate model names
        if llm_type == "gemini" and not llm_model.startswith("gemini"):
            self.warnings.append(f"⚠️ LLM_MODEL '{llm_model}' doesn't match LLM_TYPE 'gemini'")
        
        self.info.append(f"✅ LLM_MODEL: {llm_model}")
        self.info.append(f"✅ EMBEDDING_MODEL: {embedding_model}")
    
    def _validate_paths(self):
        """Validate paths and directories"""
        # These will be created automatically if they don't exist
        required_dirs = ["data", "data/raw", "data/processed", "vectorstore", "config"]
        
        for dir_name in required_dirs:
            if not os.path.exists(dir_name):
                self.info.append(f"📁 Directory '{dir_name}' will be created automatically")
    
    def _validate_numeric_settings(self):
        """Validate numeric settings"""
        numeric_settings = {
            "CHUNK_SIZE": (100, 2000, 512),
            "CHUNK_OVERLAP": (0, 500, 50),
            "MAX_TOKENS": (256, 8192, 2048),
            "TEMPERATURE": (0.0, 2.0, 0.1),
            "TOP_K_RETRIEVAL": (1, 20, 5)
        }
        
        for setting, (min_val, max_val, default_val) in numeric_settings.items():
            value = os.getenv(setting)
            if value:
                try:
                    if setting == "TEMPERATURE":
                        num_value = float(value)
                    else:
                        num_value = int(value)
                    
                    if not (min_val <= num_value <= max_val):
                        self.warnings.append(
                            f"⚠️ {setting}={num_value} is outside recommended range [{min_val}, {max_val}]"
                        )
                    else:
                        self.info.append(f"✅ {setting}: {num_value}")
                except ValueError:
                    self.errors.append(f"❌ Invalid {setting}: {value} (must be a number)")
            else:
                self.info.append(f"ℹ️ {setting}: using default ({default_val})")
    
    def _can_run(self) -> bool:
        """Check if system can run with current configuration"""
        # System can run even without API keys (with local models)
        # Only fatal errors prevent running
        return len(self.errors) == 0
    
    def print_report(self, report: Dict):
        """Print validation report"""
        print("\n" + "=" * 70)
        print("🔍 ENVIRONMENT VALIDATION REPORT")
        print("=" * 70)
        
        if report["errors"]:
            print("\n❌ ERRORS (must be fixed):")
            for error in report["errors"]:
                print(f"  {error}")
        
        if report["warnings"]:
            print("\n⚠️ WARNINGS (should be addressed):")
            for warning in report["warnings"]:
                print(f"  {warning}")
        
        if report["info"]:
            print("\nℹ️ INFORMATION:")
            for info in report["info"]:
                print(f"  {info}")
        
        print("\n" + "-" * 70)
        if report["can_run"]:
            print("✅ System can run with current configuration")
        else:
            print("❌ System cannot run - please fix errors above")
        print("=" * 70 + "\n")
    
    def create_env_file_if_missing(self):
        """Create .env file from .env.example if it doesn't exist"""
        if os.path.exists(self.env_file):
            return False
        
        example_file = ".env.example"
        if not os.path.exists(example_file):
            # Create a basic .env.example
            example_content = """# Google Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# LLM Configuration
LLM_TYPE=gemini
LLM_MODEL=gemini-1.5-flash

# Embedding Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Text Processing
CHUNK_SIZE=512
CHUNK_OVERLAP=50
MAX_TOKENS=2048
TEMPERATURE=0.1
TOP_K_RETRIEVAL=5

# Vector Store
VECTOR_STORE_TYPE=faiss

# Optional: OpenAI API (if you want to use OpenAI instead)
# OPENAI_API_KEY=your_openai_key_here
# LLM_TYPE=openai
# LLM_MODEL=gpt-3.5-turbo
"""
            with open(example_file, 'w') as f:
                f.write(example_content)
        
        # Copy .env.example to .env
        with open(example_file, 'r') as f:
            content = f.read()
        
        with open(self.env_file, 'w') as f:
            f.write(content)
        
        print(f"✅ Created {self.env_file} from {example_file}")
        print(f"⚠️ Please edit {self.env_file} and add your API keys")
        return True


def validate_environment(auto_fix: bool = False) -> bool:
    """
    Validate environment and optionally auto-fix issues
    Returns True if environment is valid or can run
    """
    validator = EnvironmentValidator()
    
    # Create .env file if missing
    if auto_fix:
        validator.create_env_file_if_missing()
    
    # Validate
    is_valid, report = validator.validate()
    
    # Print report
    validator.print_report(report)
    
    return report["can_run"]


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate environment configuration")
    parser.add_argument("--auto-fix", action="store_true", 
                       help="Automatically create .env file if missing")
    parser.add_argument("--create-env", action="store_true",
                       help="Create .env file from .env.example")
    
    args = parser.parse_args()
    
    if args.create_env:
        validator = EnvironmentValidator()
        validator.create_env_file_if_missing()
    
    can_run = validate_environment(auto_fix=args.auto_fix)
    
    exit(0 if can_run else 1)
