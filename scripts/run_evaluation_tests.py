"""
Run Comprehensive Evaluation Tests for Paper Metrics
=====================================================
This script runs the chatbot on test queries and saves results to JSON
for use in paper metrics generation.

Usage:
    python run_evaluation_tests.py --output test_results.json
    python run_evaluation_tests.py --num-queries 1000 --output test_results.json
"""

import json
import argparse
import sys
import os
import time
import warnings
from pathlib import Path
from datetime import datetime

# Suppress warnings
warnings.filterwarnings("ignore")
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "src"))

try:
    from config.config import Config
    from src.chatbot import ConstitutionChatbot
    CHATBOT_AVAILABLE = True
except ImportError as e:
    print(f"❌ Cannot import chatbot modules: {e}")
    CHATBOT_AVAILABLE = False


class EvaluationTestRunner:
    """Run evaluation tests and save results"""
    
    def __init__(self):
        self.config = Config()
        self.chatbot = ConstitutionChatbot(self.config) if CHATBOT_AVAILABLE else None
        self.results = []
        
    def get_test_queries(self):
        """Get comprehensive test query set"""
        return [
            # Pure Bengali queries (in-scope)
            {"query": "সংবিধানের ২৭ অনুচ্ছেদে কী বলা হয়েছে?", "actual_language": "bengali", "actual_scope": "in-scope"},
            {"query": "বাংলাদেশের সংবিধানে মৌলিক অধিকার কী?", "actual_language": "bengali", "actual_scope": "in-scope"},
            {"query": "সংসদ কীভাবে গঠিত হয়?", "actual_language": "bengali", "actual_scope": "in-scope"},
            {"query": "রাষ্ট্রপতির ক্ষমতা কী?", "actual_language": "bengali", "actual_scope": "in-scope"},
            {"query": "প্রধানমন্ত্রীর দায়িত্ব কী?", "actual_language": "bengali", "actual_scope": "in-scope"},
            {"query": "সংবিধান সংশোধনের পদ্ধতি কী?", "actual_language": "bengali", "actual_scope": "in-scope"},
            {"query": "মৌলিক অধিকার কতটি?", "actual_language": "bengali", "actual_scope": "in-scope"},
            {"query": "জাতীয় পতাকার বিবরণ কী?", "actual_language": "bengali", "actual_scope": "in-scope"},
            {"query": "রাষ্ট্রভাষা কী?", "actual_language": "bengali", "actual_scope": "in-scope"},
            {"query": "বিচার বিভাগের স্বাধীনতা কী?", "actual_language": "bengali", "actual_scope": "in-scope"},
            
            # Pure English queries (in-scope)
            {"query": "What does Article 27 say about equality?", "actual_language": "english", "actual_scope": "in-scope"},
            {"query": "What are the fundamental rights in Bangladesh Constitution?", "actual_language": "english", "actual_scope": "in-scope"},
            {"query": "How is the Parliament formed?", "actual_language": "english", "actual_scope": "in-scope"},
            {"query": "What are the powers of the President?", "actual_language": "english", "actual_scope": "in-scope"},
            {"query": "What are the duties of the Prime Minister?", "actual_language": "english", "actual_scope": "in-scope"},
            {"query": "How can the Constitution be amended?", "actual_language": "english", "actual_scope": "in-scope"},
            {"query": "How many fundamental rights are there?", "actual_language": "english", "actual_scope": "in-scope"},
            {"query": "What is the state language of Bangladesh?", "actual_language": "english", "actual_scope": "in-scope"},
            {"query": "What does the Constitution say about judicial independence?", "actual_language": "english", "actual_scope": "in-scope"},
            {"query": "What are the national symbols?", "actual_language": "english", "actual_scope": "in-scope"},
            
            # Mixed language queries
            {"query": "Article ১০ এর মূল বিষয় কি?", "actual_language": "mixed", "actual_scope": "in-scope"},
            {"query": "What is মৌলিক অধিকার in Constitution?", "actual_language": "mixed", "actual_scope": "in-scope"},
            {"query": "সংবিধানে Parliament এর ক্ষমতা কী?", "actual_language": "mixed", "actual_scope": "in-scope"},
            {"query": "Amendment করার procedure কী?", "actual_language": "mixed", "actual_scope": "in-scope"},
            
            # Out-of-scope legal queries
            {"query": "দেওয়ানী আদালতের এখতিয়ার কী?", "actual_language": "bengali", "actual_scope": "out-of-scope"},
            {"query": "ফৌজদারি মামলার পদ্ধতি কী?", "actual_language": "bengali", "actual_scope": "out-of-scope"},
            {"query": "What is the procedure for civil lawsuits?", "actual_language": "english", "actual_scope": "out-of-scope"},
            {"query": "How to file a criminal case?", "actual_language": "english", "actual_scope": "out-of-scope"},
            {"query": "কোম্পানি আইন কী?", "actual_language": "bengali", "actual_scope": "out-of-scope"},
            {"query": "What is the contract act?", "actual_language": "english", "actual_scope": "out-of-scope"},
            
            # Out-of-scope general queries
            {"query": "আজকের আবহাওয়া কেমন?", "actual_language": "bengali", "actual_scope": "out-of-scope"},
            {"query": "What is the capital of France?", "actual_language": "english", "actual_scope": "out-of-scope"},
            {"query": "বাংলাদেশের জনসংখ্যা কত?", "actual_language": "bengali", "actual_scope": "out-of-scope"},
            {"query": "What is machine learning?", "actual_language": "english", "actual_scope": "out-of-scope"},
        ]
    
    def run_test(self, test_case):
        """Run a single test case"""
        query = test_case["query"]
        
        start_time = time.time()
        result = self.chatbot.process_query(query, use_llm=True)
        end_time = time.time()
        
        # Extract metrics
        return {
            "query": query,
            "actual_language": test_case["actual_language"],
            "predicted_language": result.get("language", "unknown"),
            "actual_scope": test_case["actual_scope"],
            "predicted_scope": "in-scope" if result.get("num_sources", 0) > 0 else "out-of-scope",
            "latency": end_time - start_time,
            "mode": result.get("mode", "gemini"),
            "num_sources": result.get("num_sources", 0),
            "answer_length": len(result.get("answer", "")),
            "timestamp": datetime.now().isoformat()
        }
    
    def run_all_tests(self, num_queries=None):
        """Run all test cases"""
        test_queries = self.get_test_queries()
        
        if num_queries:
            # Repeat queries to reach desired count
            import random
            while len(test_queries) < num_queries:
                test_queries.extend(random.sample(self.get_test_queries(), 
                                                 min(len(self.get_test_queries()), num_queries - len(test_queries))))
            test_queries = test_queries[:num_queries]
        
        print(f"\n🧪 Running {len(test_queries)} test queries...")
        print("=" * 60)
        
        results = []
        for i, test_case in enumerate(test_queries, 1):
            try:
                print(f"\r[{i}/{len(test_queries)}] Testing: {test_case['query'][:50]}...", end="", flush=True)
                result = self.run_test(test_case)
                results.append(result)
            except Exception as e:
                print(f"\n❌ Error on query {i}: {e}")
                continue
        
        print("\n\n✅ Tests completed!")
        return results
    
    def save_results(self, results, output_path):
        """Save results to JSON file"""
        output_data = {
            "metadata": {
                "total_queries": len(results),
                "test_date": datetime.now().isoformat(),
                "chatbot_version": "1.0",
                "language_distribution": self._calculate_distribution(results, "actual_language"),
                "scope_distribution": self._calculate_distribution(results, "actual_scope")
            },
            "queries": results
        }
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Results saved to {output_file.absolute()}")
        return str(output_file.absolute())
    
    def _calculate_distribution(self, results, field):
        """Calculate distribution of a field"""
        from collections import Counter
        values = [r.get(field, "unknown") for r in results]
        counts = Counter(values)
        total = len(values)
        return {k: {"count": v, "percentage": v/total*100} for k, v in counts.items()}


def main():
    parser = argparse.ArgumentParser(
        description='Run evaluation tests for paper metrics'
    )
    parser.add_argument('--output', default='test_results.json',
                       help='Output JSON file path')
    parser.add_argument('--num-queries', type=int, default=None,
                       help='Number of queries to test (default: all)')
    
    args = parser.parse_args()
    
    if not CHATBOT_AVAILABLE:
        print("❌ Chatbot modules not available")
        print("   Please install required dependencies")
        sys.exit(1)
    
    print("🏛️ Bangladesh Constitution Chatbot - Evaluation Test Runner")
    print("=" * 60)
    
    runner = EvaluationTestRunner()
    
    if not runner.chatbot or not runner.chatbot.is_ready():
        print("❌ Chatbot not ready")
        sys.exit(1)
    
    # Run tests
    results = runner.run_all_tests(args.num_queries)
    
    # Save results
    output_path = runner.save_results(results, args.output)
    
    # Summary statistics
    print("\n📊 Test Summary:")
    print(f"   Total queries: {len(results)}")
    
    # Language detection accuracy
    lang_correct = sum(1 for r in results if r['actual_language'] == r['predicted_language'])
    lang_accuracy = lang_correct / len(results) * 100 if results else 0
    print(f"   Language detection accuracy: {lang_accuracy:.1f}%")
    
    # Scope validation accuracy
    scope_correct = sum(1 for r in results if r['actual_scope'] == r['predicted_scope'])
    scope_accuracy = scope_correct / len(results) * 100 if results else 0
    print(f"   Scope validation accuracy: {scope_accuracy:.1f}%")
    
    # Latency stats
    latencies = [r['latency'] for r in results]
    print(f"   Mean latency: {sum(latencies)/len(latencies):.2f}s")
    
    print(f"\n✅ Use this file with: python generate_paper_metrics.py --test-results {output_path}")


if __name__ == '__main__':
    main()
