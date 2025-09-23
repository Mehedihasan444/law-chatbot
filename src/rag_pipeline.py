"""
RAG Pipeline for Bangladesh Constitution Chatbot
Orchestrates the Retrieval-Augmented Generation process.
"""
import os
import json
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import warnings
warnings.filterwarnings("ignore")

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import Config

# Core ML libraries
from langchain.schema import Document

# Import services
from services.embedding_service import EmbeddingService
from services.llm_service import LLMService
from services.vectorstore_service import VectorStoreService
from services.retrieval_service import RetrievalService


class ConstitutionRAG:
    """
    RAG system orchestrator for Bangladesh Constitution queries.
    This class integrates services for embeddings, LLM, vector storage, and retrieval.
    """
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        
        # Initialize services
        self.embedding_service = EmbeddingService()
        self.llm_service = LLMService(model_name=self.config.LLM_MODEL, config=self.config)
        
        self.embeddings = self.embedding_service.get_embeddings()
        self.llm = self.llm_service.get_llm()
        
        vectorstore_path = os.path.join(self.config.VECTORSTORE_DIR, "constitution_faiss")
        self.vectorstore_service = VectorStoreService(vectorstore_path, self.embeddings)
        
        self.vectorstore = None
        self.retriever_service = None
        
        self._all_chunks_cache = None  # lazy-loaded processed chunks
        
        # Curated concise summaries for key articles as last-resort fallbacks
        self._known_article_summaries = {
            "27": [
                "All citizens are equal before the law and are entitled to equal protection of the law.",
                "The State must not deny equality before law to any person within Bangladesh."
            ],
            "28": [
                "The State shall not discriminate against any citizen on grounds only of religion, race, caste, sex or place of birth.",
                "Women and children may receive special provision; advancement of backward sections is permitted."
            ],
            "39": [
                "Freedom of thought and conscience is guaranteed; freedom of speech and press subject to reasonable restrictions.",
                "Reasonable restrictions may be imposed for State security, friendly relations with foreign states, public order, decency or morality, or contempt of court and incitement to an offence."
            ],
            "41": [
                "Freedom of religion is guaranteed, including the right to profess, practice, or propagate religion subject to law, public order and morality.",
                "No person may be compelled to pay taxes for promoting any particular religion."
            ],
            "55": [
                "There shall be a Cabinet with the Prime Minister at its head; executive power is exercised by or on the authority of the Prime Minister.",
                "The Cabinet is collectively responsible to Parliament."
            ],
            "142": [
                "The Constitution may be amended by Act of Parliament passed by not less than two-thirds of the total number of members of Parliament.",
                "A Bill to amend the Constitution must expressly state its purpose and follow the special majority requirement."
            ]
        }
    
    def load_processed_data(self) -> List[Document]:
        """Load processed Constitution chunks from JSON file."""
        chunks_file = os.path.join(self.config.PROCESSED_DATA_DIR, "all_chunks.json")
        
        if not os.path.exists(chunks_file):
            raise FileNotFoundError(f"Processed data not found: {chunks_file}")
        
        with open(chunks_file, 'r', encoding='utf-8') as f:
            chunks_data = json.load(f)
        
        documents = [
            Document(
                page_content=chunk['page_content'],
                metadata=chunk.get('metadata', {
                    'source': 'Bangladesh Constitution',
                    'language': 'en'
                })
            ) for chunk in chunks_data
        ]
        
        print(f"Loaded {len(documents)} document chunks")
        return documents
    
    def _setup_retriever(self):
        """Initializes the retrieval service."""
        if not self.vectorstore:
            raise ValueError("Vector store not initialized. Cannot setup retriever.")
        
        self.retriever_service = RetrievalService(
            self.vectorstore,
            top_k=self.config.TOP_K_RETRIEVAL
        )

    def retrieve_relevant_chunks(self, query: str) -> List[Document]:
        """Retrieve relevant document chunks for a query using the retrieval service."""
        if not self.retriever_service:
            raise ValueError("Retriever service not initialized.")
        
        return self.retriever_service.retrieve_relevant_chunks(query)
    
    def format_context(self, documents: List[Document]) -> str:
        """Format retrieved documents as context for the LLM."""
        if not documents:
            return "No relevant information found in the Constitution."

        def _clean_text(txt: str) -> str:
            """Clean and format text for better readability"""
            t = txt.strip().replace("\n", " ").replace("  ", " ")
            return t

        context_parts = []
        for i, doc in enumerate(documents, 1):
            content = _clean_text(doc.page_content)
            
            # Extract article info if available
            article_info = doc.metadata.get('article_number', '')
            part_info = doc.metadata.get('part', '')
            
            if article_info:
                context_parts.append(f"Article {article_info}: {content}")
            elif part_info:
                context_parts.append(f"{part_info}: {content}")
            else:
                context_parts.append(f"Constitutional Provision: {content}")

        return "\n\n".join(context_parts)
    
    def generate_response_simple(self, query: str, context: str) -> str:
        """Generate a response using simple templating (fallback when no LLM)."""
        if not context or "No relevant information found" in context:
            return (
                "I couldn't find specific information about your query in the Constitution of Bangladesh. "
                "Please try rephrasing your question or ask about specific articles or provisions.\n\n" +
                self.config.DISCLAIMER
            )
        
        response = self._format_human_friendly_response(query, context)
        return response + "\n\n" + self.config.DISCLAIMER
    
    def _format_human_friendly_response(self, query: str, context: str) -> str:
        """Formats a human-friendly response from raw context."""
        q = query.lower().strip()
        excerpts = context.split("Excerpt")

        # Specific handlers
        if "emergency" in q:
            return self._format_emergency_powers_response(excerpts)
        if "preamble" in q or "উদ্দেশিকা" in q:
            return self._format_preamble_response()

        # Article-specific handler
        import re
        m = re.search(r"article\s+(\d+[a-zA-Z]?)", q, re.IGNORECASE)
        if m:
            art = m.group(1).upper()
            return self._format_article_response(art, excerpts)

        # Topic to article mapping
        topic_map = {
            "freedom of speech": ["39"], "freedom of religion": ["41"], "equality": ["27", "28"],
            "amendment": ["142"], "prime minister": ["55"],
            "fundamental rights": [
                "26", "27", "28", "31", "32", "33", "34", "35", "36", "37",
                "38", "39", "40", "41", "42", "43", "44"
            ]
        }
        cited = list(dict.fromkeys([art for k, arts in topic_map.items() if k in q for art in arts]))

        # Build response
        response = "**Answer:**\n"
        if cited:
            response += f"The Constitution addresses this topic in Article(s) {', '.join(cited)}. Here is a concise summary:\n\n"
        else:
            response += "Based on the Constitution of Bangladesh, here is a concise summary:\n\n"

        bullets = self._extract_key_bullets(excerpts, max_bullets=3)
        if bullets:
            response += "\n".join([f"- {b}" for b in bullets])
        else:
            response += "Relevant provisions were found, but could not be summarized reliably. Please ask about a specific article."

        if cited:
            response += f"\n\nCitations: Article(s) {', '.join(cited)}."

        return response

    def _extract_key_bullets(self, excerpts: list, max_bullets: int = 3) -> list:
        """Extracts short, key sentences as bullets."""
        import re
        sentences = []
        for ex in excerpts[1:]:
            parts = re.split(r"(?<=[\.!?])\s+", ex.strip())
            for s in parts:
                s_clean = re.sub(r"\s+", " ", s).strip()
                if 40 <= len(s_clean) <= 180 and not re.match(r"^(Excerpt|PART|CHAPTER|SCHEDULE)\b", s_clean, re.IGNORECASE):
                    sentences.append(s_clean)
        
        return list(dict.fromkeys(sentences))[:max_bullets]
    
    def _format_emergency_powers_response(self, excerpts: List[str]) -> str:
        """Formats a specific response for emergency powers questions."""
        return (
            "**Emergency Powers in Bangladesh Constitution**\n\n"
            "**Yes, the Bangladesh Constitution contains comprehensive provisions for emergency powers (Part IXA, Articles 141A-141C):**\n\n"
            "🔹 **Emergency Proclamation (Article 141A):**\n"
            "- President can issue an Emergency Proclamation if security or economic life is threatened.\n"
            "- Requires Prime Minister's counter-signature and must be approved by Parliament.\n\n"
            "🔹 **Suspension of Laws & Rights (Articles 141B, 141C):**\n"
            "- During an emergency, enforcement of certain fundamental rights can be suspended by Presidential order.\n"
            "- The state can pass laws that might otherwise conflict with constitutional provisions.\n\n"
            "**Key Safeguards:** Parliamentary approval, time limits, and the requirement for the Prime Minister's consent act as checks on this power."
        )

    def _format_preamble_response(self) -> str:
        """Provides a human-friendly summary of the Preamble."""
        return (
            "**Preamble – What it states**\n\n"
            "The Preamble sets Bangladesh’s founding vision. In summary, it:\n"
            "- Affirms the ideals of nationalism, socialism (economic and social justice), democracy, and secularism.\n"
            "- Pledges to establish a society where the rule of law, fundamental human rights, and justice are secured for all citizens.\n"
            "- Expresses the resolve to constitute Bangladesh as a sovereign People's Republic.\n\n"
            "Citation: Preamble (Constitution of the People’s Republic of Bangladesh)."
        )

    def _format_article_response(self, article: str, excerpts: List[str]) -> str:
        """Summarizes a specific Article using retrieved docs or cached data."""
        text = self._get_article_content_from_processed(article) or self._extract_article_text_from_excerpts(article, excerpts)

        resp = f"**Article {article} – Summary**\n\n"
        bullets = self._summarize_article_text(text) if text else []
        
        # Fallback to curated summaries
        if not bullets and article in self._known_article_summaries:
            bullets = self._known_article_summaries[article]

        if bullets:
            resp += "\n".join([f"- {b}" for b in bullets])
        else:
            resp += f"The system could not retrieve a concise summary for Article {article}. Please refer to the official text."
        
        resp += f"\n\nCitation: Article {article}."
        return resp

    def _extract_article_text_from_excerpts(self, article: str, excerpts: List[str]) -> str:
        """Finds article text in retrieved excerpts using regex."""
        import re
        matcher = re.compile(rf"Article\s+{re.escape(article)}\b", re.IGNORECASE)
        for ex in excerpts[1:]:
            if m := matcher.search(ex):
                start = max(0, m.start() - 200)
                end = min(len(ex), m.end() + 1200)
                return re.sub(r"\s+", " ", ex[start:end]).strip()
        return ""

    def _get_article_content_from_processed(self, article: str) -> str:
        """Loads processed chunks and returns the content of the requested article."""
        try:
            if self._all_chunks_cache is None:
                chunks_file = os.path.join(self.config.PROCESSED_DATA_DIR, "all_chunks.json")
                with open(chunks_file, 'r', encoding='utf-8') as f:
                    self._all_chunks_cache = json.load(f)
            
            norm_article = str(article).upper()
            for ch in self._all_chunks_cache:
                meta_article = ch.get('metadata', {}).get('article_number')
                if meta_article and str(meta_article).upper() == norm_article:
                    return ch.get('page_content', '')
            return ""
        except Exception:
            return ""

    def _summarize_article_text(self, text: str) -> list:
        """Turns article body into concise bullets."""
        import re
        text = re.sub(r"\s+", " ", text).strip()
        # Split by numbered clauses or sentences
        parts = re.split(r"\s*\((\d+[A-Za-z]?)\)\s*|(?<=[;\.])\s+", text)
        
        bullets = []
        current = ""
        for p in filter(None, parts):
            if re.fullmatch(r"\d+[A-Za-z]?", p):
                if current: bullets.append(current.strip())
                current = ""
            else:
                current += " " + p
        if current: bullets.append(current.strip())

        cleaned = [b.strip(":- ") for b in bullets if 20 <= len(b) <= 220]
        return cleaned[:5]
    
    def generate_response_with_llm(self, query: str, context: str) -> str:
        """Generates a response using the LLM (Gemini or local model)."""
        if not self.llm:
            return self.generate_response_simple(query, context)
        
        try:
            # Check if we're using Gemini (ChatGoogleGenerativeAI) or local model
            llm_type = getattr(self.llm_service, 'llm_type', 'local')
            
            if llm_type == 'gemini':
                # For Gemini, we can use longer context
                prompt = self.config.USER_PROMPT_TEMPLATE.format(
                    context=context[:8000],  # Gemini can handle more context
                    question=query
                )
                # Use invoke for ChatGoogleGenerativeAI
                response = self.llm.invoke(prompt)
                # Extract content from AIMessage response
                if hasattr(response, 'content'):
                    response_text = response.content.strip()
                else:
                    response_text = str(response).strip()
            else:
                # For local models, truncate context to fit within token limits
                truncated_context = self._truncate_context_for_llm(context, query)
                prompt = self.config.USER_PROMPT_TEMPLATE.format(
                    context=truncated_context,
                    question=query
                )
                # Use invoke for HuggingFacePipeline
                response_text = self.llm.invoke(prompt).strip()
            
            return response_text + "\n\n" + self.config.DISCLAIMER
            
        except Exception as e:
            print(f"Error generating LLM response: {e}")
            return self.generate_response_simple(query, context)
    
    def _truncate_context_for_llm(self, context: str, query: str, max_tokens: int = 400) -> str:
        """
        Truncate context to fit within Flan-T5's token limit.
        Reserves tokens for prompt template and query, keeps context under max_tokens.
        """
        if not context:
            return context
            
        # Rough token estimation: 1 token ≈ 4 characters for English text
        # Reserve tokens for prompt template (~100 tokens) and query
        reserved_tokens = 100 + len(query.split()) * 1.3  # Conservative estimate
        available_tokens = max_tokens - reserved_tokens
        
        if available_tokens <= 0:
            return "Constitutional information available but query too long."
        
        # Convert tokens to approximate character count
        max_chars = int(available_tokens * 3.5)  # Conservative character-to-token ratio
        
        if len(context) <= max_chars:
            return context
            
        # Smart truncation: try to keep complete sentences/articles
        sentences = context.split('. ')
        truncated = ""
        
        for sentence in sentences:
            if len(truncated + sentence + '. ') <= max_chars:
                truncated += sentence + '. '
            else:
                break
        
        # If no complete sentences fit, do character truncation
        if not truncated.strip():
            truncated = context[:max_chars] + "..."
        
        return truncated.strip()
    
    def query(self, question: str, use_llm: bool = False) -> Dict:
        """Main query interface."""
        try:
            relevant_docs = self.retrieve_relevant_chunks(question)
            context = self.format_context(relevant_docs)
            
            if use_llm and self.llm:
                response = self.generate_response_with_llm(question, context)
            else:
                response = self.generate_response_simple(question, context)
            
            return {
                "question": question,
                "answer": response,
                "context": context,
                "num_sources": len(relevant_docs),
                "sources": [doc.metadata for doc in relevant_docs]
            }
            
        except Exception as e:
            print(f"Error processing query: {e}")
            return {
                "question": question,
                "answer": f"Sorry, an error occurred: {e}",
                "context": "", "num_sources": 0, "sources": []
            }
    
    def initialize(self, force_rebuild: bool = False) -> bool:
        """Initializes the RAG system, loading or building the vector store."""
        try:
            if not force_rebuild and self.vectorstore_service.load_vectorstore():
                self.vectorstore = self.vectorstore_service.get_vectorstore()
                self._setup_retriever()
                return True
            
            print("Building new vector store...")
            documents = self.load_processed_data()
            if not documents:
                print("❌ No processed data found.")
                return False
            
            if self.vectorstore_service.create_vectorstore(documents):
                self.vectorstore = self.vectorstore_service.get_vectorstore()
                self._setup_retriever()
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error initializing RAG system: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Gets system statistics."""
        stats = {
            "embeddings_loaded": self.embeddings is not None,
            "llm_loaded": self.llm is not None,
            "vectorstore_loaded": self.vectorstore is not None,
            "retriever_ready": self.retriever_service is not None,
        }
        
        if self.vectorstore:
            stats["vector_store_size"] = self.vectorstore.index.ntotal
        
        return stats


def main():
    """Tests the RAG system."""
    print("Bangladesh Constitution RAG System")
    print("=" * 50)
    
    config = Config()
    rag = ConstitutionRAG(config)
    
    print("Initializing RAG system...")
    if not rag.initialize():
        print("Failed to initialize RAG system.")
        return
    
    stats = rag.get_stats()
    print("\nSystem Status:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    test_queries = [
        "What does the Constitution say about freedom of speech?",
        "What are the fundamental rights mentioned in the Constitution?",
        "What does Article 27 say about equality?",
        "What is the role of the Prime Minister according to the Constitution?"
    ]
    
    print(f"\nTesting with {len(test_queries)} sample queries:")
    print("-" * 50)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\nQuery {i}: {query}")
        result = rag.query(query, use_llm=False)
        print(f"Sources found: {result['num_sources']}")
        print(f"Answer: {result['answer']}")
        print("-" * 30)


if __name__ == "__main__":
    main()