"""
Evaluate different chunk sizes to justify the choice of 200-600 tokens.
This will generate ACTUAL metrics from your Constitution data.
"""

import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
import faiss
from rank_bm25 import BM25Okapi
import re

class ChunkSizeEvaluator:
    """Evaluate retrieval performance across different chunk sizes"""
    
    def __init__(self, constitution_path='data/processed/constitution_en_raw.txt'):
        self.constitution_text = self._load_constitution(constitution_path)
        self.model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        
        # Test queries with known ground truth articles
        self.test_queries = [
            {"query": "What are the fundamental rights?", "relevant_articles": ["26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44"]},
            {"query": "What is the role of the Prime Minister?", "relevant_articles": ["55", "56", "57", "58"]},
            {"query": "How are judges appointed?", "relevant_articles": ["95", "96", "98"]},
            {"query": "What is the state religion?", "relevant_articles": ["2A"]},
            {"query": "What are the directive principles?", "relevant_articles": ["8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "25"]},
            {"query": "How can the constitution be amended?", "relevant_articles": ["142"]},
            {"query": "What is the national anthem?", "relevant_articles": ["4"]},
            {"query": "What are women's rights in parliament?", "relevant_articles": ["65"]},
            {"query": "What is the emergency provision?", "relevant_articles": ["141A", "141B", "141C"]},
            {"query": "What is the electoral system?", "relevant_articles": ["118", "119", "120", "121"]},
            # Add more queries for better coverage
            {"query": "What is equality before law?", "relevant_articles": ["27"]},
            {"query": "Freedom of assembly", "relevant_articles": ["37"]},
            {"query": "Freedom of speech", "relevant_articles": ["39"]},
            {"query": "Right to property", "relevant_articles": ["42"]},
            {"query": "What is the Supreme Court?", "relevant_articles": ["94", "95", "96", "97", "98", "99", "100", "101", "102", "103", "104", "105", "106", "107", "108", "109", "110", "111", "112", "113"]},
            {"query": "What are the duties of the President?", "relevant_articles": ["48", "49", "50", "51", "52", "53", "54", "55", "56", "57", "58"]},
            {"query": "Local government system", "relevant_articles": ["59", "60"]},
            {"query": "What is the Comptroller and Auditor General?", "relevant_articles": ["127", "128"]},
            {"query": "Defense of Bangladesh", "relevant_articles": ["61", "62", "63", "64"]},
            {"query": "Public service commission", "relevant_articles": ["137", "138", "139", "140"]},
        ]
    
    def _load_constitution(self, path):
        """Load constitution text"""
        path = Path(path)
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            print(f"⚠️ File not found: {path}")
            print("Using sample text for demonstration")
            return "Article 1. This is sample text. " * 100
    
    def create_chunks(self, min_tokens: int, max_tokens: int, overlap: int = 50) -> List[Dict]:
        """
        Create chunks from constitution text
        
        Args:
            min_tokens: Minimum chunk size in tokens
            max_tokens: Maximum chunk size in tokens
            overlap: Number of overlapping tokens
        
        Returns:
            List of chunk dictionaries with text and metadata
        """
        # Simple tokenization (split by whitespace)
        words = self.constitution_text.split()
        
        chunks = []
        i = 0
        chunk_id = 0
        
        while i < len(words):
            # Determine chunk size (between min and max)
            chunk_size = min(max_tokens, len(words) - i)
            if chunk_size < min_tokens and i + chunk_size < len(words):
                chunk_size = min_tokens
            
            # Extract chunk
            chunk_words = words[i:i + chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            # Try to extract article number if present
            article_match = re.search(r'Article\s+(\d+[A-Z]*)', chunk_text, re.IGNORECASE)
            article_num = article_match.group(1) if article_match else None
            
            chunks.append({
                'id': chunk_id,
                'text': chunk_text,
                'start_token': i,
                'end_token': i + chunk_size,
                'size': chunk_size,
                'article': article_num
            })
            
            chunk_id += 1
            i += (chunk_size - overlap)  # Move forward with overlap
        
        return chunks
    
    def build_retrieval_system(self, chunks: List[Dict]) -> Tuple[faiss.IndexFlatL2, BM25Okapi, np.ndarray]:
        """Build FAISS and BM25 indexes"""
        # Create embeddings
        texts = [chunk['text'] for chunk in chunks]
        embeddings = self.model.encode(texts, show_progress_bar=False)
        
        # Build FAISS index
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings.astype('float32'))
        
        # Build BM25 index
        tokenized_corpus = [text.lower().split() for text in texts]
        bm25 = BM25Okapi(tokenized_corpus)
        
        return index, bm25, embeddings
    
    def evaluate_retrieval(self, chunks: List[Dict], k: int = 5) -> Dict:
        """
        Evaluate retrieval accuracy for this chunk configuration
        
        Args:
            chunks: List of document chunks
            k: Number of top results to retrieve
        
        Returns:
            Dictionary with accuracy metrics
        """
        # Build retrieval system
        faiss_index, bm25, embeddings = self.build_retrieval_system(chunks)
        
        # Evaluate on test queries
        total_queries = len(self.test_queries)
        recall_at_k = []
        mrr_scores = []
        
        for test_case in self.test_queries:
            query = test_case['query']
            relevant_articles = set(test_case['relevant_articles'])
            
            # Encode query
            query_embedding = self.model.encode([query])[0]
            
            # Semantic search (FAISS)
            distances, indices = faiss_index.search(
                query_embedding.reshape(1, -1).astype('float32'), k
            )
            
            # Get retrieved chunks
            retrieved_chunks = [chunks[idx] for idx in indices[0]]
            retrieved_articles = set([
                chunk['article'] for chunk in retrieved_chunks 
                if chunk['article'] is not None
            ])
            
            # Calculate recall@k
            if len(relevant_articles) > 0:
                overlap = len(retrieved_articles & relevant_articles)
                recall = overlap / len(relevant_articles)
                recall_at_k.append(recall)
                
                # Calculate MRR (Mean Reciprocal Rank)
                for rank, chunk in enumerate(retrieved_chunks, 1):
                    if chunk['article'] in relevant_articles:
                        mrr_scores.append(1.0 / rank)
                        break
                else:
                    mrr_scores.append(0.0)
        
        # Calculate average chunk size
        avg_chunk_size = np.mean([chunk['size'] for chunk in chunks])
        total_chunks = len(chunks)
        
        # Calculate context completeness score
        # (based on average tokens per article - higher is better)
        article_coverage = {}
        for chunk in chunks:
            if chunk['article']:
                if chunk['article'] not in article_coverage:
                    article_coverage[chunk['article']] = []
                article_coverage[chunk['article']].append(chunk['size'])
        
        avg_tokens_per_article = np.mean([
            sum(sizes) for sizes in article_coverage.values()
        ]) if article_coverage else 0
        
        # Normalize context completeness (0-100 scale)
        # Assuming 300-800 tokens is ideal for full article context
        context_completeness = min(100, (avg_tokens_per_article / 600) * 100)
        
        # Computational cost (inversely proportional to chunk size)
        # More chunks = higher cost
        computational_cost = (total_chunks / avg_chunk_size) * 100
        
        return {
            'retrieval_accuracy': np.mean(recall_at_k) * 100 if recall_at_k else 0,
            'mean_reciprocal_rank': np.mean(mrr_scores) if mrr_scores else 0,
            'recall_at_k': recall_at_k,
            'avg_chunk_size': avg_chunk_size,
            'total_chunks': total_chunks,
            'context_completeness': context_completeness,
            'computational_cost_index': computational_cost,
            'articles_covered': len(article_coverage)
        }
    
    def run_comparison(self) -> Dict:
        """Compare different chunk size configurations"""
        
        configs = [
            {'name': '100-300', 'min': 100, 'max': 300, 'overlap': 30},
            {'name': '200-600', 'min': 200, 'max': 600, 'overlap': 50},
            {'name': '400-1000', 'min': 400, 'max': 1000, 'overlap': 80},
            {'name': '300-500', 'min': 300, 'max': 500, 'overlap': 50},  # Alternative
        ]
        
        results = {}
        
        print("=" * 70)
        print("CHUNK SIZE EVALUATION - EMPIRICAL ANALYSIS")
        print("=" * 70)
        print(f"\nTest Queries: {len(self.test_queries)}")
        print(f"Constitution Length: {len(self.constitution_text.split())} words\n")
        
        for config in configs:
            print(f"\n{'='*70}")
            print(f"Testing Configuration: {config['name']} tokens")
            print(f"Min: {config['min']}, Max: {config['max']}, Overlap: {config['overlap']}")
            print('='*70)
            
            # Create chunks
            chunks = self.create_chunks(
                min_tokens=config['min'],
                max_tokens=config['max'],
                overlap=config['overlap']
            )
            
            # Evaluate
            metrics = self.evaluate_retrieval(chunks, k=5)
            
            # Store results
            results[config['name']] = {
                'config': config,
                'metrics': metrics,
                'chunks_sample': chunks[:3]  # Store sample chunks
            }
            
            # Print results
            print(f"\n📊 Results:")
            print(f"  Total Chunks Created: {metrics['total_chunks']}")
            print(f"  Average Chunk Size: {metrics['avg_chunk_size']:.1f} tokens")
            print(f"  Articles Covered: {metrics['articles_covered']}")
            print(f"  Retrieval Accuracy (Recall@5): {metrics['retrieval_accuracy']:.1f}%")
            print(f"  Mean Reciprocal Rank: {metrics['mean_reciprocal_rank']:.3f}")
            print(f"  Context Completeness: {metrics['context_completeness']:.1f}/100")
            print(f"  Computational Cost Index: {metrics['computational_cost_index']:.1f}")
        
        return results
    
    def generate_table(self, results: Dict):
        """Generate comparison table for paper"""
        
        print("\n" + "="*70)
        print("SUMMARY TABLE (for Paper)")
        print("="*70)
        print("\n| Chunk Size | Retrieval Accuracy | Context Completeness | Computational Cost |")
        print("|------------|-------------------|---------------------|-------------------|")
        
        for config_name, data in results.items():
            metrics = data['metrics']
            accuracy = f"{metrics['retrieval_accuracy']:.1f}%"
            
            # Categorize context completeness
            if metrics['context_completeness'] > 70:
                completeness = "High"
            elif metrics['context_completeness'] > 40:
                completeness = "Medium"
            else:
                completeness = "Low"
            
            # Categorize computational cost
            if metrics['computational_cost_index'] > 80:
                cost = "High"
            elif metrics['computational_cost_index'] > 40:
                cost = "Medium"
            else:
                cost = "Low"
            
            # Bold the best accuracy
            if config_name == max(results.keys(), 
                                  key=lambda k: results[k]['metrics']['retrieval_accuracy']):
                accuracy = f"**{accuracy}**"
                completeness = f"**{completeness}**"
                cost = f"**Optimal**" if cost == "Medium" else cost
            
            print(f"| {config_name:10} | {accuracy:17} | {completeness:19} | {cost:17} |")
        
        print("\n")
    
    def save_results(self, results: Dict, output_path='paper_metrics/chunk_size_analysis.json'):
        """Save results to JSON file"""
        output_path = Path(output_path)
        output_path.parent.mkdir(exist_ok=True)
        
        # Prepare serializable results
        serializable_results = {}
        for config_name, data in results.items():
            serializable_results[config_name] = {
                'config': data['config'],
                'metrics': {
                    k: float(v) if isinstance(v, (np.floating, np.integer)) else v
                    for k, v in data['metrics'].items()
                    if k != 'recall_at_k'  # Skip list for summary
                },
                'sample_chunk': data['chunks_sample'][0]['text'][:200] + "..." if data['chunks_sample'] else None
            }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, indent=2)
        
        print(f"✅ Results saved to: {output_path}")


def main():
    """Run chunk size evaluation"""
    
    print("\n🔬 Starting Chunk Size Empirical Analysis...\n")
    
    evaluator = ChunkSizeEvaluator()
    
    # Run comparison
    results = evaluator.run_comparison()
    
    # Generate table
    evaluator.generate_table(results)
    
    # Save results
    evaluator.save_results(results)
    
    print("\n" + "="*70)
    print("✅ Analysis Complete!")
    print("="*70)
    print("\n📝 Next Steps:")
    print("1. Review the results above")
    print("2. Use the table values in your paper (Section 3.3)")
    print("3. Check paper_metrics/chunk_size_analysis.json for detailed metrics")
    print("\n⚠️  Note: If your constitution files are missing, this uses sample data.")
    print("   Make sure data/processed/constitution_en_raw.txt exists for real results.\n")


if __name__ == "__main__":
    main()
