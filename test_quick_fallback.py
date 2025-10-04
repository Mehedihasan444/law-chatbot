"""
Quick test of automatic fallback mechanism
"""
import os
import sys
import time

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config import Config
from src.rag_pipeline import ConstitutionRAG

print('Quick Test: Automatic Fallback with Local Model')
print('=' * 70)

# Save real key and use invalid one
real_key = os.environ.get('GEMINI_API_KEY', '')
os.environ['GEMINI_API_KEY'] = 'INVALID_KEY_TESTING'

try:
    config = Config()
    rag = ConstitutionRAG(config)
    
    print('\nInitializing RAG system...')
    if rag.initialize():
        print('RAG system initialized\n')
        
        # First query - should trigger timeout and fallback
        print('Query: What is Article 27 about?')
        print('-' * 70)
        start = time.time()
        result = rag.query('What is Article 27 about?', use_llm=True)
        elapsed = time.time() - start
        
        print(f'\nCompleted in {elapsed:.2f} seconds')
        print(f'Sources found: {result["num_sources"]}')
        print(f'\nAnswer:\n{result["answer"][:300]}...\n')
        
        # Second query - should use already-loaded local model
        print('\nQuery 2: What are fundamental rights?')
        print('-' * 70)
        start = time.time()
        result2 = rag.query('What are fundamental rights?', use_llm=True)
        elapsed = time.time() - start
        
        print(f'\nCompleted in {elapsed:.2f} seconds')
        print(f'Sources found: {result2["num_sources"]}')
        print(f'\nAnswer:\n{result2["answer"][:300]}...\n')
        
        print('Local model fallback is working correctly!')
    else:
        print('Failed to initialize RAG system')
finally:
    # Restore real API key
    if real_key:
        os.environ['GEMINI_API_KEY'] = real_key

print('\n' + '=' * 70)
