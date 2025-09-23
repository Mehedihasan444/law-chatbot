"""
Test script for Gemini API integration
Run this to verify that the Gemini API is working correctly
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config import Config
from src.services.llm_service import LLMService

def test_gemini_integration():
    """Test the Gemini API integration"""
    print("🧪 Testing Gemini API Integration")
    print("=" * 50)
    
    # Check if API key is set
    config = Config()
    if not config.GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY not found in environment variables")
        print("Please set your Gemini API key in the .env file")
        return False
    
    print(f"✅ Gemini API key found")
    print(f"📝 Model: {config.LLM_MODEL}")
    print(f"🔧 LLM Type: {config.LLM_TYPE}")
    
    # Initialize LLM service
    try:
        print("\n🚀 Initializing LLM service...")
        llm_service = LLMService(config=config)
        model_info = llm_service.get_model_info()
        
        print(f"📊 Model Info:")
        for key, value in model_info.items():
            print(f"  {key}: {value}")
        
        if not llm_service.get_llm():
            print("❌ Failed to load LLM")
            return False
            
        print("✅ LLM service initialized successfully")
        
        # Test a simple query
        print("\n🤔 Testing with a simple query...")
        llm = llm_service.get_llm()
        
        test_prompt = """
        Constitutional Information:
        Article 27: All citizens are equal before law and are entitled to equal protection of law.
        
        User Question: What does Article 27 say about equality?
        
        Please provide a clear and accurate answer based on the constitutional information provided.
        """
        
        response = llm.invoke(test_prompt)
        
        # Extract response content
        if hasattr(response, 'content'):
            response_text = response.content
        else:
            response_text = str(response)
            
        print(f"🤖 LLM Response:")
        print(f"{response_text}")
        
        print("\n✅ Gemini API integration test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    success = test_gemini_integration()
    if success:
        print("\n🎉 All tests passed! Your Gemini API integration is working correctly.")
        print("You can now run the chatbot with: streamlit run src/streamlit_app.py")
    else:
        print("\n💡 Setup Tips:")
        print("1. Make sure you have a valid Gemini API key from https://aistudio.google.com/app/apikey")
        print("2. Add it to your .env file as GEMINI_API_KEY=your_key_here")
        print("3. Install required packages: pip install -r requirements.txt")