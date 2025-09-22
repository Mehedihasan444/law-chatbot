"""
Retrieval Service
"""
from typing import List
from langchain.schema import Document
from langchain_community.vectorstores import FAISS

class RetrievalService:
    """Handles document retrieval from the vector store."""

    def __init__(self, vectorstore: FAISS, top_k: int = 3):
        if not vectorstore:
            raise ValueError("Vector store must be initialized before the retrieval service.")
        # Use MMR for better diversity and reduce top_k to minimize context size
        self.retriever = vectorstore.as_retriever(
            search_type="mmr",  # Maximum Marginal Relevance for diverse results
            search_kwargs={
                "k": top_k,
                "fetch_k": top_k * 2,  # Fetch more, then rank for diversity
                "lambda_mult": 0.7  # Balance between relevance and diversity
            }
        )
        print(f"Retriever setup with MMR, top-k: {top_k}")

    def retrieve_relevant_chunks(self, query: str) -> List[Document]:
        """Retrieves relevant document chunks for a given query."""
        try:
            documents = self.retriever.invoke(query)
            # Additional filtering to ensure we get the most relevant chunks
            if len(documents) > 3:
                documents = documents[:3]  # Hard limit for context size
            return documents
        except Exception as e:
            print(f"Error retrieving documents: {e}")
            return []
