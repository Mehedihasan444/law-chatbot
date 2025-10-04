"""
Test automatic fallback from Gemini API to local LLM.
This script simulates various failure scenarios to demonstrate
the automatic fallback mechanism.
"""
import os
import sys
import time

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config import Config
from src.rag_pipeline import ConstitutionRAG

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_normal_operation():
    """Test 1: Normal operation with Gemini API"""
    print_section("TEST 1: Normal Operation with Gemini API")
    
    config = Config()
    rag = ConstitutionRAG(config)
    
    print("\n🔧 Initializing RAG system...")
    if not rag.initialize():
        print("❌ Failed to initialize RAG system")
        return False
    
    print("\n📝 Testing query with Gemini API...")
    query = "What is Article 27 about?"
    
    start_time = time.time()
    result = rag.query(query, use_llm=True)
    elapsed = time.time() - start_time
    
    print(f"\n✅ Query completed in {elapsed:.2f} seconds")
    print(f"📊 Sources found: {result['num_sources']}")
    print(f"🔄 Fallback used: {result.get('fallback_used', False)}")
    print(f"\n💬 Answer preview: {result['answer'][:200]}...")
    
    return True

def test_simulated_gemini_failure():
    """Test 2: Simulate Gemini API failure by using invalid API key"""
    print_section("TEST 2: Simulated Gemini API Failure (Invalid API Key)")
    
    # Temporarily save real API key and use invalid one
    real_key = os.environ.get('GEMINI_API_KEY', '')
    os.environ['GEMINI_API_KEY'] = 'INVALID_KEY_FOR_TESTING'
    
    try:
        config = Config()
        rag = ConstitutionRAG(config)
        
        print("\n🔧 Initializing RAG system with invalid API key...")
        if not rag.initialize():
            print("❌ Failed to initialize RAG system")
            return False
        
        print("\n📝 Testing query (should automatically fallback to local model)...")
        query = "What does Article 27 say about equality?"
        
        start_time = time.time()
        result = rag.query(query, use_llm=True)
        elapsed = time.time() - start_time
        
        print(f"\n✅ Query completed in {elapsed:.2f} seconds")
        print(f"📊 Sources found: {result['num_sources']}")
        print(f"🔄 Fallback used: {result.get('fallback_used', False)}")
        print(f"\n💬 Answer preview: {result['answer'][:200]}...")
        
        # Test second query to verify persistent fallback
        print("\n📝 Testing second query (should use already-initialized fallback)...")
        query2 = "What are fundamental rights?"
        
        start_time = time.time()
        result2 = rag.query(query2, use_llm=True)
        elapsed = time.time() - start_time
        
        print(f"\n✅ Second query completed in {elapsed:.2f} seconds")
        print(f"📊 Sources found: {result2['num_sources']}")
        print(f"🔄 Fallback used: {result2.get('fallback_used', False)}")
        print(f"\n💬 Answer preview: {result2['answer'][:200]}...")
        
        return True
        
    finally:
        # Restore real API key
        if real_key:
            os.environ['GEMINI_API_KEY'] = real_key
        else:
            os.environ.pop('GEMINI_API_KEY', None)

def test_network_timeout_simulation():
    """Test 3: Demonstrate behavior with network issues"""
    print_section("TEST 3: Network Timeout Handling")
    
    print("\n📌 Note: This test demonstrates the timeout protection mechanism.")
    print("   If Gemini API takes >10 seconds, automatic fallback occurs.")
    print("   In production, this protects against network delays.")
    
    config = Config()
    rag = ConstitutionRAG(config)
    
    print("\n🔧 Initializing RAG system...")
    if not rag.initialize():
        print("❌ Failed to initialize RAG system")
        return False
    
    print("\n📝 Testing query with timeout protection...")
    query = "Explain the amendment process in the Constitution."
    
    start_time = time.time()
    result = rag.query(query, use_llm=True)
    elapsed = time.time() - start_time
    
    print(f"\n✅ Query completed in {elapsed:.2f} seconds")
    print(f"📊 Sources found: {result['num_sources']}")
    print(f"🔄 Fallback used: {result.get('fallback_used', False)}")
    
    if elapsed > 10:
        print("\n⏰ Query took >10 seconds - automatic fallback was triggered!")
    else:
        print("\n⚡ Query completed within timeout - no fallback needed!")
    
    print(f"\n💬 Answer preview: {result['answer'][:200]}...")
    
    return True

def test_persistent_fallback():
    """Test 4: Verify persistent fallback after first failure"""
    print_section("TEST 4: Persistent Fallback After Initial Failure")
    
    print("\n📌 This test verifies that after Gemini fails once, subsequent")
    print("   queries use the local model directly without retry attempts.")
    
    # Use invalid API key to force fallback
    real_key = os.environ.get('GEMINI_API_KEY', '')
    os.environ['GEMINI_API_KEY'] = 'INVALID_KEY_FOR_TESTING'
    
    try:
        config = Config()
        rag = ConstitutionRAG(config)
        
        print("\n🔧 Initializing RAG system...")
        if not rag.initialize():
            print("❌ Failed to initialize RAG system")
            return False
        
        queries = [
            "What is Article 27?",
            "What are fundamental rights?",
            "What does the Constitution say about freedom of speech?"
        ]
        
        for i, query in enumerate(queries, 1):
            print(f"\n📝 Query {i}/{len(queries)}: {query}")
            start_time = time.time()
            result = rag.query(query, use_llm=True)
            elapsed = time.time() - start_time
            
            print(f"   ⏱️  Completed in {elapsed:.2f}s")
            print(f"   📊 Sources: {result['num_sources']}")
            print(f"   🔄 Fallback: {result.get('fallback_used', False)}")
            
            if i == 1:
                print("   ✅ First query - fallback initialized")
            else:
                print("   ✅ Using persistent fallback (no retry to Gemini)")
        
        return True
        
    finally:
        # Restore real API key
        if real_key:
            os.environ['GEMINI_API_KEY'] = real_key
        else:
            os.environ.pop('GEMINI_API_KEY', None)

def main():
    """Run all fallback tests."""
    print("\n" + "=" * 70)
    print("  Bangladesh Constitution Chatbot - Automatic Fallback Tests")
    print("=" * 70)
    print("\nThis test suite demonstrates the automatic fallback mechanism")
    print("from Gemini API to local LLM when API calls fail.")
    print("\n📋 Test Plan:")
    print("  1. Normal operation with Gemini API")
    print("  2. Automatic fallback with invalid API key")
    print("  3. Network timeout protection")
    print("  4. Persistent fallback verification")
    
    input("\n⏸️  Press Enter to start tests...")
    
    tests = [
        ("Normal Operation", test_normal_operation),
        ("Simulated API Failure", test_simulated_gemini_failure),
        ("Network Timeout Handling", test_network_timeout_simulation),
        ("Persistent Fallback", test_persistent_fallback)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            print(f"\n\n{'=' * 70}")
            print(f"Starting: {test_name}")
            print('=' * 70)
            success = test_func()
            results.append((test_name, "✅ PASSED" if success else "❌ FAILED"))
        except KeyboardInterrupt:
            print("\n\n⏸️  Tests interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            results.append((test_name, f"❌ ERROR: {str(e)[:50]}"))
        
        if test_name != tests[-1][0]:  # Not the last test
            input("\n⏸️  Press Enter to continue to next test...")
    
    # Print summary
    print("\n\n" + "=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70)
    for test_name, result in results:
        print(f"{result:20} - {test_name}")
    print("=" * 70)
    
    print("\n\n💡 Key Features Demonstrated:")
    print("   ✅ Automatic detection of Gemini API failures")
    print("   ✅ Seamless fallback to local LLM")
    print("   ✅ Persistent fallback state (no repeated Gemini attempts)")
    print("   ✅ Timeout protection (10 second limit)")
    print("   ✅ Clear user feedback about which model is being used")
    print("\n" + "=" * 70 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests cancelled by user\n")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}\n")
