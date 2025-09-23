"""
Main Chatbot Logic for Bangladesh Constitution Chatbot
Handles conversation flow, language detection, and response generation
"""
import os
import sys
import re
import warnings
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Suppress warnings
warnings.filterwarnings("ignore")
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import Config
from src.rag_pipeline import ConstitutionRAG

try:
    from langdetect import detect
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    print("⚠️ langdetect not available - language detection disabled")


class ConstitutionChatbot:
    """Main chatbot class for Bangladesh Constitution queries"""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.rag_system = None
        self.conversation_history = []
        self.session_stats = {
            "queries_processed": 0,
            "session_start": datetime.now(),
            "languages_detected": set()
        }
        
        # Initialize RAG system
        self._initialize_rag()
    
    def _initialize_rag(self):
        """Initialize the RAG system"""
        try:
            print("🏛️ Initializing Bangladesh Constitution Chatbot...")
            self.rag_system = ConstitutionRAG(self.config)
            
            if not self.rag_system.initialize():
                raise Exception("Failed to initialize RAG system")
            
            print("✅ Chatbot initialized successfully!")
            
        except Exception as e:
            print(f"❌ Error initializing chatbot: {e}")
            self.rag_system = None
    
    def detect_language(self, text: str) -> str:
        """Detect language of input text"""
        if not LANGDETECT_AVAILABLE:
            # Fallback: check for Bengali characters
            if re.search(r'[\u0980-\u09FF]', text):
                return 'bn'
            return 'en'
        
        try:
            detected = detect(text)
            if detected in ['bn', 'hi']:  # Bengali or Hindi (sometimes Bengali is misidentified)
                return 'bn'
            elif detected == 'en':
                return 'en'
            else:
                # Fallback: check for Bengali characters
                if re.search(r'[\u0980-\u09FF]', text):
                    return 'bn'
                return 'en'
        except:
            # Default fallback
            if re.search(r'[\u0980-\u09FF]', text):
                return 'bn'
            return 'en'
    
    def is_constitutional_query(self, query: str) -> bool:
        """Check if query is related to Constitution"""
        # Keywords that indicate constitutional queries
        constitutional_keywords = [
            'constitution', 'constitutional', 'article', 'amendment', 'fundamental rights',
            'freedom', 'equality', 'parliament', 'prime minister', 'president', 'court',
            'law', 'legal', 'rights', 'duties', 'government', 'state', 'citizen',
            # Bengali keywords
            'সংবিধান', 'অনুচ্ছেদ', 'ধারা', 'মৌলিক অধিকার', 'স্বাধীনতা', 'সমতা',
            'সংসদ', 'প্রধানমন্ত্রী', 'রাষ্ট্রপতি', 'আদালত', 'আইন', 'অধিকার', 'কর্তব্য'
        ]
        
        query_lower = query.lower()
        return any(keyword.lower() in query_lower for keyword in constitutional_keywords)
    
    def preprocess_query(self, query: str) -> str:
        """Clean and preprocess user query"""
        # Remove extra whitespace
        query = re.sub(r'\s+', ' ', query.strip())
        
        # Remove common prefixes/suffixes that don't add value
        prefixes_to_remove = [
            'please tell me', 'can you tell me', 'i want to know',
            'what is', 'please explain', 'আমি জানতে চাই', 'দয়া করে বলুন'
        ]
        
        for prefix in prefixes_to_remove:
            if query.lower().startswith(prefix.lower()):
                query = query[len(prefix):].strip()
        
        return query
    
    def format_response(self, result: Dict, language: str = 'en') -> str:
        """Format the response based on language and add metadata"""
        if not result or not result.get('answer'):
            if language == 'bn':
                return "দুঃখিত, আমি আপনার প্রশ্নের উত্তর দিতে পারিনি। অনুগ্রহ করে প্রশ্নটি অন্যভাবে করুন।"
            else:
                return "Sorry, I couldn't answer your question. Please try rephrasing it."
        
        answer = result['answer']
        num_sources = result.get('num_sources', 0)
        
        # Add source information
        if num_sources > 0:
            if language == 'bn':
                source_info = f"\n\n📚 **সূত্র:** {num_sources}টি সাংবিধানিক অনুচ্ছেদ থেকে তথ্য সংগ্রহ করা হয়েছে।"
            else:
                source_info = f"\n\n📚 **Sources:** Information gathered from {num_sources} constitutional provisions."
        else:
            source_info = ""
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        formatted_response = f"{answer}{source_info}\n\n🕐 Generated at: {timestamp}"
        return formatted_response
    
    def handle_out_of_scope_query(self, query: str, language: str = 'en') -> str:
        """Handle queries outside Constitution scope"""
        if language == 'bn':
            return """🚫 **ক্ষমা চাই!** 

আমি শুধুমাত্র বাংলাদেশের সংবিধান সম্পর্কে প্রশ্নের উত্তর দিতে পারি। আপনার প্রশ্নটি সংবিধানের বাইরের বিষয় বলে মনে হচ্ছে।

**আমি যেসব বিষয়ে সাহায্য করতে পারি:**
- মৌলিক অধিকার সম্পর্কে
- সরকারি কাঠামো ও ক্ষমতা বিভাজন
- সাংবিধানিক সংশোধনী
- নির্দিষ্ট অনুচ্ছেদের ব্যাখ্যা

অনুগ্রহ করে সংবিধান সম্পর্কিত প্রশ্ন করুন।""" + "\n\n" + self.config.DISCLAIMER
        else:
            return """🚫 **Sorry!** 

I can only answer questions about the Constitution of the People's Republic of Bangladesh. Your query appears to be outside my scope.

**I can help you with:**
- Fundamental rights and freedoms
- Government structure and separation of powers  
- Constitutional amendments
- Specific article interpretations
- Legal provisions and procedures

Please ask questions related to the Constitution of Bangladesh.""" + "\n\n" + self.config.DISCLAIMER
    
    def process_query(self, query: str, use_llm: bool = False) -> Dict:
        """Main query processing pipeline"""
        try:
            # Update stats
            self.session_stats["queries_processed"] += 1
            
            # Preprocess query
            processed_query = self.preprocess_query(query)
            
            # Detect language
            language = self.detect_language(processed_query)
            self.session_stats["languages_detected"].add(language)
            
            # Check if query is constitutional
            if not self.is_constitutional_query(processed_query):
                response = self.handle_out_of_scope_query(processed_query, language)
                result = {
                    "question": query,
                    "answer": response,
                    "language": language,
                    "scope": "out_of_scope",
                    "num_sources": 0,
                    "processing_time": 0
                }
            else:
                # Process with RAG system
                start_time = datetime.now()
                
                if not self.rag_system:
                    raise Exception("RAG system not initialized")
                
                rag_result = self.rag_system.query(processed_query, use_llm=use_llm)
                
                processing_time = (datetime.now() - start_time).total_seconds()
                
                # Format response
                formatted_answer = self.format_response(rag_result, language)
                
                result = {
                    "question": query,
                    "answer": formatted_answer,
                    "language": language,
                    "scope": "constitutional",
                    "num_sources": rag_result.get("num_sources", 0),
                    "context": rag_result.get("context", ""),
                    "sources": rag_result.get("sources", []),
                    "processing_time": processing_time
                }
            
            # Add to conversation history
            self.conversation_history.append({
                "timestamp": datetime.now(),
                "query": query,
                "response": result["answer"],
                "language": language,
                "sources": result.get("num_sources", 0)
            })
            
            return result
            
        except Exception as e:
            print(f"❌ Error processing query: {e}")
            return {
                "question": query,
                "answer": f"Sorry, I encountered an error: {str(e)}",
                "language": "en",
                "scope": "error",
                "num_sources": 0,
                "processing_time": 0
            }
    
    def get_conversation_history(self, limit: int = 10) -> List[Dict]:
        """Get recent conversation history"""
        return self.conversation_history[-limit:] if limit else self.conversation_history
    
    def clear_conversation_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        print("🗑️ Conversation history cleared")
    
    def get_session_stats(self) -> Dict:
        """Get session statistics"""
        current_time = datetime.now()
        session_duration = current_time - self.session_stats["session_start"]
        
        stats = {
            **self.session_stats,
            "session_duration_minutes": round(session_duration.total_seconds() / 60, 1),
            "average_query_time": None,
            "system_status": "active" if self.rag_system else "error"
        }
        
        if self.rag_system:
            rag_stats = self.rag_system.get_stats()
            stats.update(rag_stats)
        
        return stats
    
    def is_ready(self) -> bool:
        """Check if chatbot is ready to process queries"""
        return self.rag_system is not None and self.rag_system.retriever_service is not None


def main():
    """Test the chatbot"""
    print("🏛️ Bangladesh Constitution Chatbot - Interactive Test")
    print("=" * 60)
    
    # Initialize chatbot
    chatbot = ConstitutionChatbot()
    
    if not chatbot.is_ready():
        print("❌ Chatbot not ready. Please check initialization.")
        return
    
    # Show system stats
    stats = chatbot.get_session_stats()
    print("\n📊 System Status:")
    for key, value in stats.items():
        if key not in ['session_start', 'languages_detected']:
            print(f"  {key}: {value}")
    
    print("\n🎯 Interactive Mode - Type 'quit' to exit, 'history' to see conversation")
    print("-" * 60)
    
    while True:
        try:
            query = input("\n💬 Your question: ").strip()
            
            if not query:
                continue
            
            if query.lower() == 'quit':
                break
            
            if query.lower() == 'history':
                history = chatbot.get_conversation_history(5)
                print(f"\n📜 Last {len(history)} conversations:")
                for i, conv in enumerate(history, 1):
                    print(f"{i}. Q: {conv['query'][:50]}...")
                    print(f"   A: {conv['response'][:100]}...")
                    print(f"   Sources: {conv['sources']}, Lang: {conv['language']}")
                continue
            
            if query.lower() == 'stats':
                current_stats = chatbot.get_session_stats()
                print(f"\n📊 Session Statistics:")
                for key, value in current_stats.items():
                    print(f"  {key}: {value}")
                continue
            
            # Process query
            print("\n🤔 Processing...")
            result = chatbot.process_query(query, use_llm=False)
            
            print(f"\n🏛️ **Answer** (Language: {result['language']}, Sources: {result['num_sources']}):")
            print(result['answer'])
            
            print(f"\n⏱️ Processing time: {result['processing_time']:.2f}s")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n👋 Goodbye! Thank you for using the Bangladesh Constitution Chatbot.")
    
    # Final stats
    final_stats = chatbot.get_session_stats()
    print(f"\n📊 Final Session Stats:")
    print(f"  Queries processed: {final_stats['queries_processed']}")
    print(f"  Session duration: {final_stats['session_duration_minutes']} minutes")
    print(f"  Languages used: {', '.join(final_stats['languages_detected'])}")


if __name__ == "__main__":
    main()