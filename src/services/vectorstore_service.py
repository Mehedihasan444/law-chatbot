"""
Vectorstore Service
"""
import os
from typing import List
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

class VectorStoreService:
    """Manages the FAISS vector store."""

    def __init__(self, vectorstore_path: str, embeddings: HuggingFaceEmbeddings):
        self.vectorstore_path = vectorstore_path
        self.embeddings = embeddings
        self.vectorstore = None

    def create_vectorstore(self, documents: List[Document]) -> bool:
        """Creates and saves a FAISS vector store from documents."""
        try:
            print("Creating vector store...")
            self.vectorstore = FAISS.from_documents(
                documents=documents,
                embedding=self.embeddings
            )
            self.vectorstore.save_local(self.vectorstore_path)
            print(f"Vector store created and saved to {self.vectorstore_path}")
            return True
        except Exception as e:
            print(f"Error creating vector store: {e}")
            return False

    def load_vectorstore(self) -> bool:
        """Loads an existing FAISS vector store from disk."""
        if not os.path.exists(self.vectorstore_path):
            return False
        try:
            self.vectorstore = FAISS.load_local(
                self.vectorstore_path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            print(f"Vector store loaded from {self.vectorstore_path}")
            return True
        except Exception as e:
            print(f"Error loading vector store: {e}")
            return False

    def get_vectorstore(self):
        """Returns the loaded vector store."""
        return self.vectorstore
