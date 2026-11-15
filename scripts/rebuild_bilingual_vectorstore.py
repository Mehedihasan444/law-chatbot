"""
Rebuild Vector Store with Bilingual Constitution Data
This script rebuilds the FAISS vector store with both English and Bengali chunks
"""
import sys
import os
from pathlib import Path

# Add project root to path
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
    from rag_pipeline import ConstitutionRAG
    
    print("🏛️ Rebuilding Vector Store with Bilingual Constitution Data")
    print("=" * 60)
    
    # Initialize configuration
    config = Config()
    
    # Initialize RAG system
    print("\n1. Initializing RAG system...")
    rag = ConstitutionRAG(config)
    
    # Force rebuild the vector store
    print("\n2. Rebuilding vector store with bilingual data...")
    success = rag.initialize(force_rebuild=True)
    
    if success:
        print("✅ Vector store rebuilt successfully!")
        
        # Get stats
        stats = rag.get_stats()
        print(f"\n📊 Vector Store Statistics:")
        print(f"   Vector store size: {stats.get('vector_store_size', 'Unknown')}")
        print(f"   Embeddings loaded: {stats.get('embeddings_loaded', False)}")
        print(f"   Retriever ready: {stats.get('retriever_ready', False)}")
        
        # Test with both languages
        print(f"\n3. Testing bilingual functionality...")
        
        # Test English query
        print("\n🇺🇸 Testing English Query:")
        en_query = "What does Article 27 say about equality?"
        en_result = rag.query(en_query, use_llm=False)
        print(f"   Query: {en_query}")
        print(f"   Sources found: {en_result['num_sources']}")
        print(f"   Answer preview: {en_result['answer'][:150]}...")
        
        # Test Bengali query
        print("\n🇧🇩 Testing Bengali Query:")
        bn_query = "সংবিধানে মৌলিক অধিকারগুলো কী কী?"
        bn_result = rag.query(bn_query, use_llm=False)
        print(f"   Query: {bn_query}")
        print(f"   Sources found: {bn_result['num_sources']}")
        print(f"   Answer preview: {bn_result['answer'][:150]}...")
        
        # Check language distribution in sources
        print(f"\n4. Analyzing language distribution...")
        
        # Get all documents to check language distribution
        import json
        chunks_file = config.PROCESSED_DATA_DIR + "/all_chunks.json"
        with open(chunks_file, 'r', encoding='utf-8') as f:
            all_chunks = json.load(f)
        
        lang_counts = {}
        for chunk in all_chunks:
            lang = chunk.get('metadata', {}).get('language', 'unknown')
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
        
        print("   Language distribution in vector store:")
        for lang, count in lang_counts.items():
            lang_name = "English" if lang == "en" else "Bengali" if lang == "bn" else lang
            percentage = (count / len(all_chunks)) * 100
            print(f"   📊 {lang_name}: {count} chunks ({percentage:.1f}%)")
        
        print(f"\n🎉 Bilingual vector store setup completed successfully!")
        print(f"   Total documents: {len(all_chunks)}")
        print(f"   Languages supported: English, Bengali")
        
    else:
        print("❌ Failed to rebuild vector store")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)