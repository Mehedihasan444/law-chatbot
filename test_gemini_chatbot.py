"""
Simple test of Gemini API integration in the chatbot
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config import Config
from src.chatbot import ConstitutionChatbot

print("Testing Gemini API Integration")
print("="*50)

# Initialize chatbot
config = Config()
print(f"Model: {config.LLM_MODEL}")
print(f"API Key: {config.GEMINI_API_KEY[:20]}...")
print()

chatbot = ConstitutionChatbot(config)

if chatbot.is_ready():
    print("Chatbot initialized successfully!")
    print()
    
    # Test query
    question = "What is Article 27 about?"
    print(f"Question: {question}")
    print()
    
    result = chatbot.process_query(question, use_llm=True)
    
    print("Answer:")
    print(result['answer'])
    print()
    print(f"Sources: {result['num_sources']}")
    print(f"Language: {result['language']}")
    print(f"Processing time: {result['processing_time']:.2f}s")
else:
    print("ERROR: Chatbot not ready")
