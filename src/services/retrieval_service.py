"""
Retrieval Service
"""
from typing import List
from langchain.schema import Document
from langchain_community.vectorstores import FAISS

class RetrievalService:
    """Handles document retrieval from the vector store."""

    def __init__(self, vectorstore: FAISS, top_k: int = 5):
        if not vectorstore:
            raise ValueError("Vector store must be initialized before the retrieval service.")
        self.retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": top_k}
        )
        print(f"Retriever setup with top-k: {top_k}")

    def retrieve_relevant_chunks(self, query: str) -> List[Document]:
        """Retrieves relevant document chunks for a given query."""
        try:
            return self.retriever.get_relevant_documents(query)
        except Exception as e:
            print(f"Error retrieving documents: {e}")
            return []
