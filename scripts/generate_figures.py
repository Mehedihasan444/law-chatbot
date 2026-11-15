"""
Generate all figures and visualizations for journal paper
Bangladesh Constitution Chatbot Project
"""
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

# Set style for professional academic figures
plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'serif'

# This file lives in scripts/; add project root so 'visualizations' resolves
sys.path.insert(0, str(Path(__file__).parent.parent))

# Create output directory (project root / figures)
OUTPUT_DIR = Path(__file__).parent.parent / "figures"
OUTPUT_DIR.mkdir(exist_ok=True)

def save_figure(fig, filename, tight=True):
    """Save figure in multiple formats"""
    if tight:
        plt.tight_layout()
    
    # Save as PNG and PDF for paper
    fig.savefig(OUTPUT_DIR / f"{filename}.png", dpi=300, bbox_inches='tight')
    fig.savefig(OUTPUT_DIR / f"{filename}.pdf", bbox_inches='tight')
    print(f"✅ Saved: {filename}")
    plt.close()

def main():
    """Generate all figures"""
    print("=" * 60)
    print("Generating Figures for Journal Paper")
    print("Bangladesh Constitution Chatbot")
    print("=" * 60)
    
    # Import visualization modules
    from visualizations import system_architecture
    from visualizations import rag_pipeline
    from visualizations import performance_metrics
    from visualizations import data_analysis
    from visualizations import comparison_charts
    
    # Generate all figures
    print("\n📊 Generating System Architecture Diagrams...")
    system_architecture.generate_all()
    
    print("\n📊 Generating RAG Pipeline Visualizations...")
    rag_pipeline.generate_all()
    
    print("\n📊 Generating Performance Metrics...")
    performance_metrics.generate_all()
    
    print("\n📊 Generating Data Analysis Charts...")
    data_analysis.generate_all()
    
    print("\n📊 Generating Comparison Charts...")
    comparison_charts.generate_all()
    
    print("\n" + "=" * 60)
    print(f"✅ All figures saved to: {OUTPUT_DIR.absolute()}")
    print("=" * 60)

if __name__ == "__main__":
    main()
