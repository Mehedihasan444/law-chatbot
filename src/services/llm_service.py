"""
LLM Service
"""
import os
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from langchain_huggingface import HuggingFacePipeline

class LLMService:
    """Handles the loading and configuration of the Language Model."""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or os.getenv("CPU_LLM_MODEL", "google/flan-t5-base")
        self.llm = self._setup_llm()

    def _setup_llm(self):
        """Initializes a CPU-friendly seq2seq LLM (FLAN-T5)."""
        print(f"Loading language model: {self.model_name}...")
        try:
            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)

            pipe = pipeline(
                "text2text-generation",
                model=model,
                tokenizer=tokenizer,
                max_new_tokens=1024,  # Increased for more comprehensive answers
                temperature=0.3,      # Slightly higher for more varied, thoughtful responses
                do_sample=True,
                top_p=0.9,           # More focused sampling for coherent responses
                top_k=40,            # Reduced for better quality control
                repetition_penalty=1.15,  # Higher penalty to avoid repetition
                length_penalty=1.2,  # Encourage longer, more detailed responses
                early_stopping=False # Allow full development of thoughts
            )
            return HuggingFacePipeline(pipeline=pipe)
        except Exception as e:
            print(f"Error loading language model: {e}")
            print("Warning: LLM setup failed. Falling back to retrieval-only mode.")
            return None

    def get_llm(self):
        """Returns the loaded language model pipeline."""
        return self.llm
