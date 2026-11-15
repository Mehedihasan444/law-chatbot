"""
Example: Generate Specific Figure Categories
Use this script to generate only the figures you need
"""

import sys
from pathlib import Path

# Add visualizations to path
# This file lives in scripts/; add project root so 'visualizations' resolves
sys.path.append(str(Path(__file__).parent.parent))

# Import only the modules you need
from visualizations import (
    system_architecture,
    rag_pipeline,
    performance_metrics,
    data_analysis,
    comparison_charts
)

def main():
    """
    Generate specific figure categories
    Comment out the ones you don't need
    """
    
    print("=" * 60)
    print("Generating Selected Figures")
    print("=" * 60)
    
    # Uncomment the categories you want:
    
    # System Architecture (Figures 1-2)
    print("\n📐 Generating System Architecture...")
    system_architecture.generate_all()
    
    # RAG Pipeline (Figures 3-5)
    print("\n🔄 Generating RAG Pipeline...")
    rag_pipeline.generate_all()
    
    # Performance Metrics (Figures 6-10)
    print("\n📊 Generating Performance Metrics...")
    performance_metrics.generate_all()
    
    # Data Analysis (Figures 11-14)
    print("\n📚 Generating Data Analysis...")
    data_analysis.generate_all()
    
    # Comparison Charts (Figures 15-17)
    print("\n🔍 Generating Comparison Charts...")
    comparison_charts.generate_all()
    
    print("\n" + "=" * 60)
    print("✅ Selected figures generated!")
    print("=" * 60)


def generate_single_figure_example():
    """
    Example: Generate just one specific figure
    """
    print("Generating a single figure...")
    
    # Import the module
    from visualizations import system_architecture
    
    # Call specific function
    system_architecture.generate_overall_architecture()
    
    print("✅ Figure 1 generated!")


def generate_results_only():
    """
    Example: Generate only figures for Results section
    """
    print("Generating Results Section Figures (6-13)...")
    
    from visualizations import performance_metrics, data_analysis
    
    performance_metrics.generate_all()  # Figures 6-10
    data_analysis.generate_all()        # Figures 11-14 (subset for results)
    
    print("✅ Results figures generated!")


def generate_methodology_only():
    """
    Example: Generate only figures for Methodology section
    """
    print("Generating Methodology Section Figures (3-5, 14)...")
    
    from visualizations import rag_pipeline, data_analysis
    
    rag_pipeline.generate_all()  # Figures 3-5
    data_analysis.generate_data_processing_pipeline()  # Figure 14
    
    print("✅ Methodology figures generated!")


if __name__ == "__main__":
    # Run main function to generate all
    main()
    
    # Or uncomment one of these to generate specific subsets:
    # generate_single_figure_example()
    # generate_results_only()
    # generate_methodology_only()
