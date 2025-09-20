"""
Embedding Service
"""
from langchain_huggingface import HuggingFaceEmbeddings

class EmbeddingService:
    """Handles the loading of the sentence transformer model for embeddings."""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.embeddings = self._load_embedding_model()

    def _load_embedding_model(self):
        """Initializes and returns a CPU-friendly embedding model."""
        print(f"Loading embedding model: {self.model_name}...")
        try:
            return HuggingFaceEmbeddings(
                model_name=self.model_name,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
        except Exception as e:
            print(f"Error loading embedding model: {e}")
            raise

    def get_embeddings(self):
        """Returns the loaded embedding model."""
        return self.embeddings
