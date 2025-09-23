"""
Test script to verify Gemini API integ    print(f"✅ Model Name: {model_info['model_name']}")
    print(f"✅ Model Type: {model_info.get('llm_type', 'gemini')}")
    print(f"✅ Model Ready: {model_info['is_loaded']}")
    print(f"✅ Gemini Available: {model_info['gemini_available']}")on with the Bangladesh Constitution Chatbot
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Set environment variables from .env file if not already set
from dotenv import load_dotenv
load_dotenv()

try:
    # Import project modules
    sys.path.append(str(project_root / "src"))
    sys.path.append(str(project_root))
    
    from config.config import Config
    from services.llm_service import LLMService
    from rag_pipeline import ConstitutionRAG
    from chatbot import ConstitutionChatbot
    
    print("🏛️ Testing Bangladesh Constitution Chatbot with Gemini API")
    print("=" * 60)
    
    # Test configuration
    print("\n1. Testing Configuration...")
    config = Config()
    validation = config.validate_config()
    
    print(f"✅ LLM Model: {validation['llm_model']}")
    print(f"✅ LLM Type: {validation['llm_type']}")
    print(f"✅ Gemini API Key Present: {validation['gemini_key_present']}")
    print(f"✅ Embedding Model: {validation['embedding_model']}")
    
    # Test LLM Service
    print("\n2. Testing LLM Service...")
    llm_service = LLMService()
    model_info = llm_service.get_model_info()
    
    print(f"✅ Model Name: {model_info['model_name']}")
    print(f"✅ LLM Type: {model_info['llm_type']}")
    print(f"✅ Model Ready: {model_info['is_loaded']}")
    print(f"✅ Gemini Available: {model_info['gemini_available']}")
    
    if llm_service.get_llm() is not None:
        print("✅ LLM Service initialized successfully!")
        
        # Test a simple query
        print("\n3. Testing Simple LLM Query...")
        try:
            llm = llm_service.get_llm()
            test_response = llm.invoke("What is the capital of Bangladesh?")
            print(f"✅ Test Response: {test_response.content[:100]}...")
        except Exception as e:
            print(f"❌ LLM Test Error: {e}")
    else:
        print("❌ LLM Service not ready")
        sys.exit(1)
    
    # Test if processed data exists
    print("\n4. Checking Processed Data...")
    processed_file = config.PROCESSED_DATA_DIR + "/all_chunks.json"
    if os.path.exists(processed_file):
        print("✅ Processed Constitution data found")
        
        # Try to initialize full RAG pipeline
        print("\n5. Testing RAG Pipeline...")
        try:
            rag = ConstitutionRAG(config)
            if rag.initialize():
                print("✅ RAG Pipeline initialized successfully!")
                
                # Test a constitutional query
                print("\n6. Testing Constitutional Query...")
                test_query = "What does Article 27 say about equality?"
                result = rag.query(test_query, use_llm=True)
                
                print(f"✅ Query: {result['question']}")
                print(f"✅ Sources Found: {result['num_sources']}")
                print(f"✅ Answer Preview: {result['answer'][:200]}...")
                
                # Test chatbot
                print("\n7. Testing Full Chatbot...")
                chatbot = ConstitutionChatbot(config)
                if chatbot.is_ready():
                    print("✅ Chatbot initialized successfully!")
                    
                    bot_result = chatbot.process_query(test_query, use_llm=True)
                    print(f"✅ Chatbot Response Length: {len(bot_result['answer'])} characters")
                    print(f"✅ Language Detected: {bot_result['language']}")
                    print(f"✅ Processing Time: {bot_result['processing_time']:.2f}s")
                else:
                    print("❌ Chatbot not ready")
            else:
                print("❌ RAG Pipeline initialization failed")
        except Exception as e:
            print(f"❌ RAG Pipeline Error: {e}")
    else:
        print("⚠️ Processed data not found. Please run data processing first:")
        print("   python src/data_processor.py --download --process")
        
        # Test without RAG
        print("\n5. Testing LLM without RAG...")
        try:
            llm = llm_service.get_llm()
            simple_query = "Explain the concept of equality in constitutional law."
            response = llm.invoke(simple_query)
            print(f"✅ Simple LLM Response: {response.content[:150]}...")
        except Exception as e:
            print(f"❌ Simple LLM Error: {e}")
    
    print(f"\n🎉 Integration test completed!")
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Please make sure all dependencies are installed:")
    print("pip install google-generativeai langchain-google-genai")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)