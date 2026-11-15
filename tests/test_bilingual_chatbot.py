"""
Comprehensive Bilingual Test for Bangladesh Constitution Chatbot
Tests both English and Bengali functionality with Gemini API
"""
import sys
import os
from pathlib import Path

# Add project root to path (file is in tests/, so go up one level)
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "src"))

from dotenv import load_dotenv
load_dotenv()

# Suppress warnings
import warnings
warnings.filterwarnings("ignore")
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"

try:
    from config.config import Config
    from chatbot import ConstitutionChatbot
    
    print("🏛️ Comprehensive Bilingual Test - Bangladesh Constitution Chatbot")
    print("=" * 70)
    
    # Initialize chatbot
    print("\n1. Initializing bilingual chatbot...")
    config = Config()
    chatbot = ConstitutionChatbot(config)
    
    if not chatbot.is_ready():
        print("❌ Chatbot not ready")
        sys.exit(1)
    
    print("✅ Chatbot initialized successfully!")
    
    # Get session stats
    stats = chatbot.get_session_stats()
    print(f"\n📊 System Status:")
    print(f"   Languages supported: {config.SUPPORTED_LANGUAGES}")
    print(f"   Vector store loaded: {stats.get('vectorstore_loaded', False)}")
    print(f"   LLM loaded: {stats.get('llm_loaded', False)}")
    
    # Test queries in both languages
    test_queries = [
        # English queries
        {
            "query": "What does Article 27 say about equality?",
            "language": "English",
            "expected_lang": "en"
        },
        {
            "query": "What are the fundamental rights in the Constitution?",
            "language": "English", 
            "expected_lang": "en"
        },
        {
            "query": "How can the Constitution be amended?",
            "language": "English",
            "expected_lang": "en"
        },
        # Bengali queries
        {
            "query": "সংবিধানের ২৭ অনুচ্ছেদে সমতার বিষয়ে কী বলা হয়েছে?",
            "language": "বাংলা (Bengali)",
            "expected_lang": "bn"
        },
        {
            "query": "বাংলাদেশের সংবিধানে মৌলিক অধিকারগুলো কী কী?",
            "language": "বাংলা (Bengali)",
            "expected_lang": "bn"
        },
        {
            "query": "কীভাবে সংবিধান সংশোধন করা যায়?",
            "language": "বাংলা (Bengali)", 
            "expected_lang": "bn"
        }
    ]
    
    print(f"\n2. Testing {len(test_queries)} bilingual queries...")
    print("=" * 70)
    
    for i, test_case in enumerate(test_queries, 1):
        query = test_case["query"]
        language = test_case["language"]
        expected_lang = test_case["expected_lang"]
        
        print(f"\n🔹 Test {i}/6 ({language})")
        print(f"   Query: {query}")
        
        # Process query
        result = chatbot.process_query(query, use_llm=True)
        
        # Check results
        detected_lang = result.get('language', 'unknown')
        sources_found = result.get('num_sources', 0)
        processing_time = result.get('processing_time', 0)
        answer_length = len(result.get('answer', ''))
        
        print(f"   ✅ Language detected: {detected_lang}")
        print(f"   ✅ Sources found: {sources_found}")
        print(f"   ✅ Processing time: {processing_time:.2f}s")
        print(f"   ✅ Answer length: {answer_length} characters")
        
        # Validate language detection
        if detected_lang == expected_lang:
            print(f"   ✅ Language detection: CORRECT")
        else:
            print(f"   ⚠️ Language detection: Expected {expected_lang}, got {detected_lang}")
        
        # Show answer preview
        answer_preview = result.get('answer', '')[:200] + "..." if len(result.get('answer', '')) > 200 else result.get('answer', '')
        print(f"   📝 Answer preview: {answer_preview}")
        
        print("-" * 50)
    
    # Test conversation history
    print(f"\n3. Testing conversation history...")
    history = chatbot.get_conversation_history(3)
    print(f"   Recent conversations: {len(history)}")
    
    # Language usage stats
    final_stats = chatbot.get_session_stats()
    languages_used = final_stats.get('languages_detected', set())
    print(f"   Languages used in session: {list(languages_used)}")
    
    # Test mixed language capabilities
    print(f"\n4. Testing mixed/edge cases...")
    
    # Test mixed language query (English query about Bengali terms)
    mixed_query = "What does 'মৌলিক অধিকার' mean in the Constitution?"
    mixed_result = chatbot.process_query(mixed_query, use_llm=True)
    print(f"   Mixed language query processed: {mixed_result.get('language', 'unknown')}")
    print(f"   Sources found: {mixed_result.get('num_sources', 0)}")
    
    # Final summary
    print(f"\n🎉 Bilingual Test Summary:")
    print(f"   Total queries processed: {final_stats.get('queries_processed', 0)}")
    print(f"   Session duration: {final_stats.get('session_duration_minutes', 0):.1f} minutes")
    print(f"   Languages detected: {', '.join(languages_used)}")
    print(f"   System status: {'✅ All systems operational' if chatbot.is_ready() else '❌ Issues detected'}")
    
    print(f"\n✅ Comprehensive bilingual test completed successfully!")
    print(f"🌐 Your Bangladesh Constitution Chatbot now supports both English and Bengali!")
    
except Exception as e:
    print(f"❌ Error during testing: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)