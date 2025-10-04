"""
Simple Demo: Automatic Fallback in Action
This script demonstrates the automatic fallback feature with visual feedback.
"""
import os
import sys
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config import Config
from src.rag_pipeline import ConstitutionRAG

def print_header(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")

def simulate_network_failure():
    """Simulates network failure by using invalid API key"""
    print_header("DEMO: Automatic Fallback in Action")
    
    print("This demo simulates a Gemini API failure and shows how the system")
    print("automatically falls back to the local FLAN-T5 model.\n")
    
    # Save real API key
    real_key = os.environ.get('GEMINI_API_KEY', '')
    os.environ['GEMINI_API_KEY'] = 'SIMULATED_FAILURE_KEY'
    
    try:
        print("Step 1: Initialize chatbot with 'broken' API key")
        print("-" * 70)
        config = Config()
        rag = ConstitutionRAG(config)
        
        if not rag.initialize():
            print("ERROR: Failed to initialize RAG system")
            return
        
        print("\nStep 2: Ask first question")
        print("-" * 70)
        print("Question: 'What is Article 27 about?'\n")
        
        print("Expected behavior:")
        print("  1. Try Gemini API")
        print("  2. Timeout after 10 seconds")
        print("  3. Automatically switch to local model")
        print("  4. Return answer from local model\n")
        
        input("Press Enter to continue...")
        
        start = time.time()
        result = rag.query('What is Article 27 about?', use_llm=True)
        elapsed = time.time() - start
        
        print(f"\nCompleted in {elapsed:.2f} seconds")
        print(f"Sources: {result['num_sources']}")
        print(f"\nAnswer (first 200 chars):\n{result['answer'][:200]}...\n")
        
        print("\nStep 3: Ask second question")
        print("-" * 70)
        print("Question: 'What are fundamental rights?'\n")
        
        print("Expected behavior:")
        print("  1. Skip Gemini (already marked as failed)")
        print("  2. Use local model directly")
        print("  3. Fast response (model already loaded)\n")
        
        input("Press Enter to continue...")
        
        start = time.time()
        result2 = rag.query('What are fundamental rights?', use_llm=True)
        elapsed = time.time() - start
        
        print(f"\nCompleted in {elapsed:.2f} seconds")
        print(f"Sources: {result2['num_sources']}")
        print(f"\nAnswer (first 200 chars):\n{result2['answer'][:200]}...\n")
        
        print_header("Demo Complete!")
        print("\nKey Observations:")
        print("  1. First query: Gemini timeout (~10s) + Local model init (~25s) = ~35s")
        print("  2. Second query: Local model only = <1s (much faster!)")
        print("  3. No manual intervention needed - fully automatic")
        print("  4. System remains operational despite API failure")
        print("\nThis ensures ZERO DOWNTIME in production! ")
        
    finally:
        # Restore real API key
        if real_key:
            os.environ['GEMINI_API_KEY'] = real_key
        else:
            os.environ.pop('GEMINI_API_KEY', None)

def test_with_working_api():
    """Tests with working Gemini API"""
    print_header("BONUS: Test with Working Gemini API")
    
    print("Now let's test with a working Gemini API key to see the difference.\n")
    
    # Check if we have a real API key
    if not os.environ.get('GEMINI_API_KEY'):
        print("No GEMINI_API_KEY found. Skipping this test.")
        return
    
    print("Question: 'What is Article 27 about?'\n")
    print("Expected behavior:")
    print("  1. Use Gemini API successfully")
    print("  2. Return high-quality AI-generated response")
    print("  3. Complete in ~5-10 seconds\n")
    
    response = input("Run this test? (y/n): ")
    if response.lower() != 'y':
        print("Skipped.")
        return
    
    config = Config()
    rag = ConstitutionRAG(config)
    
    if not rag.initialize():
        print("ERROR: Failed to initialize RAG system")
        return
    
    start = time.time()
    result = rag.query('What is Article 27 about?', use_llm=True)
    elapsed = time.time() - start
    
    print(f"\nCompleted in {elapsed:.2f} seconds")
    print(f"Sources: {result['num_sources']}")
    print(f"\nAnswer (first 300 chars):\n{result['answer'][:300]}...\n")
    
    print("Notice the difference:")
    print("  - Gemini: Faster initial response, more detailed answer")
    print("  - Local: Slower first time, but works offline and is free!")

if __name__ == "__main__":
    try:
        simulate_network_failure()
        print("\n" + "=" * 70 + "\n")
        test_with_working_api()
        print("\n" + "=" * 70 + "\n")
    except KeyboardInterrupt:
        print("\n\nDemo cancelled by user.")
    except Exception as e:
        print(f"\n\nERROR: {e}")
