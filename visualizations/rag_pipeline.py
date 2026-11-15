"""
RAG Pipeline Visualizations
Generates detailed RAG process flow diagrams
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
import numpy as np
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / "figures"

def save_fig(fig, name):
    """Helper to save figure"""
    fig.savefig(OUTPUT_DIR / f"{name}.png", dpi=300, bbox_inches='tight')
    fig.savefig(OUTPUT_DIR / f"{name}.pdf", bbox_inches='tight')
    plt.close()
    print(f"  ✓ {name}")


def generate_rag_pipeline_detailed():
    """Figure 3: Detailed RAG Pipeline Flow"""
    fig, ax = plt.subplots(figsize=(14, 10), constrained_layout=True)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    ax.text(7, 11.5, 'RAG Pipeline: Detailed Process Flow',
            ha='center', fontsize=14, fontweight='bold')
    
    # Phase 1: Input Processing
    ax.text(1, 10.5, 'Phase 1: Input', fontsize=10, fontweight='bold', color='#2E86AB')
    rect = FancyBboxPatch((0.5, 9.2), 3, 1.2, boxstyle="round,pad=0.1",
                          edgecolor='#2E86AB', facecolor='#E8F4F8', linewidth=2)
    ax.add_patch(rect)
    ax.text(2, 9.8, 'User Query\n"Article 27 সম্পর্কে বলুন"', ha='center', va='center', fontsize=9)
    
    # Language Detection
    rect = FancyBboxPatch((0.5, 7.5), 3, 1.2, boxstyle="round,pad=0.1",
                          edgecolor='#2E86AB', facecolor='#B4D7FF', linewidth=2)
    ax.add_patch(rect)
    ax.text(2, 8.1, 'Language Detection\nDetected: Bengali (bn)', ha='center', va='center', fontsize=9)
    
    arrow = FancyArrowPatch((2, 9.2), (2, 8.7), arrowstyle='->', 
                           color='#2E86AB', linewidth=2, mutation_scale=20)
    ax.add_patch(arrow)
    
    # Phase 2: Embedding
    ax.text(5.5, 10.5, 'Phase 2: Embedding', fontsize=10, fontweight='bold', color='#A23B72')
    rect = FancyBboxPatch((4.5, 9.2), 3, 1.2, boxstyle="round,pad=0.1",
                          edgecolor='#A23B72', facecolor='#F8E8F4', linewidth=2)
    ax.add_patch(rect)
    ax.text(6, 9.8, 'Query Embedding\n(MiniLM-L6)', ha='center', va='center', fontsize=9)
    
    rect = FancyBboxPatch((4.5, 7.5), 3, 1.2, boxstyle="round,pad=0.1",
                          edgecolor='#A23B72', facecolor='#FFD4E5', linewidth=2)
    ax.add_patch(rect)
    ax.text(6, 8.1, 'Vector: [384 dimensions]\n→ Dense representation', ha='center', va='center', fontsize=9)
    
    arrow = FancyArrowPatch((6, 9.2), (6, 8.7), arrowstyle='->', 
                           color='#A23B72', linewidth=2, mutation_scale=20)
    ax.add_patch(arrow)
    
    arrow = FancyArrowPatch((3.5, 9.8), (4.5, 9.8), arrowstyle='->', 
                           color='black', linewidth=2, mutation_scale=20)
    ax.add_patch(arrow)
    
    # Phase 3: Retrieval
    ax.text(10, 10.5, 'Phase 3: Retrieval', fontsize=10, fontweight='bold', color='#F18F01')
    rect = FancyBboxPatch((8.5, 9.2), 3, 1.2, boxstyle="round,pad=0.1",
                          edgecolor='#F18F01', facecolor='#FFF4E8', linewidth=2)
    ax.add_patch(rect)
    ax.text(10, 9.8, 'Hybrid Search\n(Semantic + Keyword)', ha='center', va='center', fontsize=9)
    
    rect = FancyBboxPatch((8.5, 7.5), 3, 1.2, boxstyle="round,pad=0.1",
                          edgecolor='#F18F01', facecolor='#FFE5CC', linewidth=2)
    ax.add_patch(rect)
    ax.text(10, 8.1, 'Top-5 Relevant Chunks\n(FAISS Vector Store)', ha='center', va='center', fontsize=9)
    
    arrow = FancyArrowPatch((10, 9.2), (10, 8.7), arrowstyle='->', 
                           color='#F18F01', linewidth=2, mutation_scale=20)
    ax.add_patch(arrow)
    
    arrow = FancyArrowPatch((7.5, 9.8), (8.5, 9.8), arrowstyle='->', 
                           color='black', linewidth=2, mutation_scale=20)
    ax.add_patch(arrow)
    
    # Phase 4: Context Assembly
    ax.text(2, 6.2, 'Phase 4: Context', fontsize=10, fontweight='bold', color='#06A77D')
    rect = FancyBboxPatch((0.5, 4.5), 5, 1.5, boxstyle="round,pad=0.1",
                          edgecolor='#06A77D', facecolor='#E8F8F4', linewidth=2)
    ax.add_patch(rect)
    ax.text(3, 5.5, 'Context Assembly', ha='center', fontsize=9, fontweight='bold')
    ax.text(3, 5.1, '• Retrieved chunks: 5\n• Total tokens: ~1500\n• Language: Bengali',
            ha='center', va='center', fontsize=8)
    
    arrow = FancyArrowPatch((10, 7.5), (5.5, 6), arrowstyle='->', 
                           color='black', linewidth=2, mutation_scale=20)
    stats_text = '''Model Size: 80 MB
Parameters: 22.7M
Max Sequence: 512 tokens
Avg. Inference: ~50ms
Languages: 100+'''
    ax.text(2.75, 1.3, stats_text, ha='center', va='center', fontsize=8, family='monospace')
    ax.add_patch(rect)
    ax.text(9.5, 5.5, 'LLM Processing', ha='center', fontsize=9, fontweight='bold')
    ax.text(9.5, 5.1, 'Gemini-2.0-Flash-Exp (Primary)\n+ FLAN-T5 (Fallback)',
            ha='center', va='center', fontsize=8)
    ax.text(9.5, 4.7, 'Prompt: System + Context + Query',
            ha='center', va='center', fontsize=8, style='italic')
    
    arrow = FancyArrowPatch((5.5, 5.25), (7, 5.25), arrowstyle='->', 
                           color='black', linewidth=2, mutation_scale=20)
    ax.add_patch(arrow)
    
    # Phase 6: Response Formatting
    ax.text(7, 3.2, 'Phase 6: Output', fontsize=10, fontweight='bold', color='#5F0F40')
    rect = FancyBboxPatch((4, 1.5), 6, 1.5, boxstyle="round,pad=0.1",
                          edgecolor='#5F0F40', facecolor='#F4E8F8', linewidth=2)
    ax.add_patch(rect)
    ax.text(7, 2.5, 'Response Formatting', ha='center', fontsize=9, fontweight='bold')
    ax.text(7, 2.1, '• Add citations (Article numbers)\n• Add legal disclaimer\n• Format in Bengali',
            ha='center', va='center', fontsize=8)
    ax.text(7, 1.7, '→ Final response to user', ha='center', fontsize=8,
            style='italic', color='#5F0F40')
    
    arrow = FancyArrowPatch((9.5, 4.5), (7, 3), arrowstyle='->', 
                           color='black', linewidth=2, mutation_scale=20)
    ax.add_patch(arrow)
    
    # Add timing information
    timings = [
        (2, 6.8, '~50ms'),
        (6, 6.8, '~100ms'),
        (10, 6.8, '~200ms'),
        (9.5, 3.5, '~2000ms'),
        (7, 0.8, 'Total: ~2.5s')
    ]
    
    for x, y, text in timings:
        ax.text(x, y, text, fontsize=8, color='red', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
    
    save_fig(fig, 'fig3_rag_pipeline_detailed')


def generate_embedding_process():
    """Figure 4: Embedding Generation Process"""
    fig, ax = plt.subplots(figsize=(12, 6), constrained_layout=True)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis('off')
    
    ax.text(6, 5.5, 'Embedding Generation Process',
            ha='center', fontsize=13, fontweight='bold')
    
    # Input text
    rect = FancyBboxPatch((0.5, 3.5), 3, 1.5, boxstyle="round,pad=0.1",
                          edgecolor='#2E86AB', facecolor='#E8F4F8', linewidth=2)
    ax.add_patch(rect)
    ax.text(2, 4.5, 'Input Text', ha='center', fontsize=10, fontweight='bold')
    ax.text(2, 4.1, '"What is Article 27\nof the Constitution?"',
            ha='center', va='center', fontsize=8)
    
    # Tokenization
    arrow = FancyArrowPatch((3.5, 4.25), (4.5, 4.25), arrowstyle='->', 
                           color='black', linewidth=2, mutation_scale=20)
    ax.add_patch(arrow)
    
    rect = FancyBboxPatch((4.5, 3.5), 2.5, 1.5, boxstyle="round,pad=0.1",
                          edgecolor='#A23B72', facecolor='#F8E8F4', linewidth=2)
    ax.add_patch(rect)
    ax.text(5.75, 4.5, 'Tokenization', ha='center', fontsize=10, fontweight='bold')
    ax.text(5.75, 4.0, 'Tokens: 12\nMax length: 512',
            ha='center', va='center', fontsize=8)
    
    # Model
    arrow = FancyArrowPatch((7, 4.25), (8, 4.25), arrowstyle='->', 
                           color='black', linewidth=2, mutation_scale=20)
    ax.add_patch(arrow)
    
    rect = FancyBboxPatch((8, 3.5), 3.5, 1.5, boxstyle="round,pad=0.1",
                          edgecolor='#F18F01', facecolor='#FFF4E8', linewidth=2)
    ax.add_patch(rect)
    ax.text(9.75, 4.5, 'MiniLM-L6 Model', ha='center', fontsize=10, fontweight='bold')
    ax.text(9.75, 4.0, 'Sentence Transformers\n384-dim output',
            ha='center', va='center', fontsize=8)
    
    # Output vector
    arrow = FancyArrowPatch((9.75, 3.5), (9.75, 2.5), arrowstyle='->', 
                           color='black', linewidth=2, mutation_scale=20)
    ax.add_patch(arrow)
    
    rect = FancyBboxPatch((6, 0.5), 7.5, 1.8, boxstyle="round,pad=0.1",
                          edgecolor='#06A77D', facecolor='#E8F8F4', linewidth=2)
    ax.add_patch(rect)
    ax.text(9.75, 2.1, 'Embedding Vector (384 dimensions)', ha='center',
            fontsize=10, fontweight='bold')
    ax.text(9.75, 1.7, '[0.123, -0.456, 0.789, ..., 0.321]', ha='center',
            fontsize=8, family='monospace')
    ax.text(9.75, 1.3, '→ Stored in FAISS Index', ha='center',
            fontsize=8, style='italic')
    ax.text(9.75, 0.9, '→ Used for similarity search', ha='center',
            fontsize=8, style='italic')
    
    # Statistics box
    rect = FancyBboxPatch((0.5, 0.5), 4.5, 2.2, boxstyle="round,pad=0.1",
                          edgecolor='#5F0F40', facecolor='#F4E8F8', linewidth=2)
    ax.add_patch(rect)
    ax.text(2.75, 2.4, 'Model Statistics', ha='center', fontsize=10, fontweight='bold')
    stats_text = '''Model Size: 80 MB
Parameters: 22.7M
Max Sequence: 512 tokens
Avg. Inference: ~50ms
Languages: 100+'''
    ax.text(2.75, 1.3, stats_text, ha='center', va='center', fontsize=8, family='monospace')
    
    save_fig(fig, 'fig4_embedding_process')


def generate_retrieval_mechanism():
    """Figure 5: Hybrid Retrieval Mechanism"""
    fig, ax = plt.subplots(figsize=(12, 8), constrained_layout=True)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    ax.text(6, 9.5, 'Hybrid Retrieval Mechanism',
            ha='center', fontsize=13, fontweight='bold')
    
    # Query embedding
    rect = FancyBboxPatch((4.5, 7.8), 3, 1, boxstyle="round,pad=0.1",
                          edgecolor='#2E86AB', facecolor='#E8F4F8', linewidth=2)
    ax.add_patch(rect)
    ax.text(6, 8.3, 'Query Embedding Vector', ha='center', fontsize=10, fontweight='bold')
    
    # Split into two paths
    arrow1 = FancyArrowPatch((4.5, 8.3), (2, 7), arrowstyle='->', 
                            color='#A23B72', linewidth=2.5, mutation_scale=20)
    ax.add_patch(arrow1)
    ax.text(3, 7.7, 'Semantic', fontsize=9, color='#A23B72', fontweight='bold')
    
    arrow2 = FancyArrowPatch((7.5, 8.3), (10, 7), arrowstyle='->', 
                            color='#F18F01', linewidth=2.5, mutation_scale=20)
    ax.add_patch(arrow2)
    ax.text(9, 7.7, 'Keyword', fontsize=9, color='#F18F01', fontweight='bold')
    
    # Semantic Search
    rect = FancyBboxPatch((0.5, 5.3), 3, 1.5, boxstyle="round,pad=0.1",
                          edgecolor='#A23B72', facecolor='#F8E8F4', linewidth=2)
    ax.add_patch(rect)
    ax.text(2, 6.5, 'Semantic Search', ha='center', fontsize=10, fontweight='bold')
    ax.text(2, 6.1, 'Cosine Similarity\nTop-5 results',
            ha='center', va='center', fontsize=8)
    
    # Keyword Search
    rect = FancyBboxPatch((8.5, 5.3), 3, 1.5, boxstyle="round,pad=0.1",
                          edgecolor='#F18F01', facecolor='#FFF4E8', linewidth=2)
    ax.add_patch(rect)
    ax.text(10, 6.5, 'Keyword Search', ha='center', fontsize=10, fontweight='bold')
    ax.text(10, 6.1, 'BM25 Algorithm\nTop-5 results',
            ha='center', va='center', fontsize=8)
    
    # Merge results
    arrow1 = FancyArrowPatch((2, 5.3), (4.5, 4), arrowstyle='->', 
                            color='black', linewidth=2, mutation_scale=20)
    ax.add_patch(arrow1)
    
    arrow2 = FancyArrowPatch((10, 5.3), (7.5, 4), arrowstyle='->', 
                            color='black', linewidth=2, mutation_scale=20)
    ax.add_patch(arrow2)
    
    rect = FancyBboxPatch((4.5, 2.8), 3, 1.2, boxstyle="round,pad=0.1",
                          edgecolor='#06A77D', facecolor='#E8F8F4', linewidth=2)
    ax.add_patch(rect)
    ax.text(6, 3.6, 'Result Fusion', ha='center', fontsize=10, fontweight='bold')
    ax.text(6, 3.2, 'Reciprocal Rank Fusion',
            ha='center', va='center', fontsize=8)
    
    # Re-ranking
    arrow = FancyArrowPatch((6, 2.8), (6, 1.8), arrowstyle='->', 
                           color='black', linewidth=2, mutation_scale=20)
    ax.add_patch(arrow)
    
    rect = FancyBboxPatch((4, 0.5), 4, 1.2, boxstyle="round,pad=0.1",
                          edgecolor='#C73E1D', facecolor='#FFF0E8', linewidth=2)
    ax.add_patch(rect)
    ax.text(6, 1.3, 'Re-ranked Top-K Results', ha='center', fontsize=10, fontweight='bold')
    ax.text(6, 0.9, '→ Final 5 chunks for LLM context',
            ha='center', va='center', fontsize=8, style='italic')
    
    save_fig(fig, 'fig5_hybrid_retrieval')


def generate_all():
    """Generate all RAG pipeline figures"""
    print("  Generating RAG pipeline visualizations...")
    generate_rag_pipeline_detailed()
    generate_embedding_process()
    generate_retrieval_mechanism()
