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
                max_new_tokens=768,
                temperature=0.2,
                do_sample=True,
                top_p=0.95,
                top_k=50,
                repetition_penalty=1.1,
                length_penalty=1.0
            )
            return HuggingFacePipeline(pipeline=pipe)
        except Exception as e:
            print(f"Error loading language model: {e}")
            print("Warning: LLM setup failed. Falling back to retrieval-only mode.")
            return None

    def get_llm(self):
        """Returns the loaded language model pipeline."""
        return self.llm
