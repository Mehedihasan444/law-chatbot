# Journal Paper Figures Generator

This directory contains Python scripts to automatically generate all figures and visualizations required for the journal paper on the Bangladesh Constitution Chatbot project.

## 📊 Generated Figures

The scripts generate **20 high-quality figures** covering all aspects of the system:

### System Architecture (Figures 1-2)
- **Figure 1**: Overall System Architecture - Complete layered architecture showing all components
- **Figure 2**: Component Interaction Flow - Detailed interaction sequence between components

### RAG Pipeline (Figures 3-5)
- **Figure 3**: RAG Pipeline Detailed Flow - Step-by-step RAG process with timing
- **Figure 4**: Embedding Generation Process - How text is converted to vectors
- **Figure 5**: Hybrid Retrieval Mechanism - Semantic + keyword search fusion

### Performance Metrics (Figures 6-10)
- **Figure 6**: Response Time Distribution - Gemini API vs FLAN-T5 comparison
- **Figure 7**: Component Latency Breakdown - Performance analysis of each pipeline stage
- **Figure 8**: Retrieval Effectiveness Metrics - Precision, Recall, F1-Score, MRR
- **Figure 9**: Token Usage Analysis - Token distribution and cumulative usage
- **Figure 10**: System Resource Utilization - CPU, memory, disk I/O, GPU usage

### Data Analysis (Figures 11-14)
- **Figure 11**: Document Processing Statistics - Chunks, pages, words analysis
- **Figure 12**: Language Distribution - Query language distribution and detection accuracy
- **Figure 13**: Vector Store Statistics - FAISS performance and scalability
- **Figure 14**: Data Processing Pipeline - Complete data preparation workflow

### Comparison & Evaluation (Figures 15-17)
- **Figure 15**: Model Comparison - Comprehensive Gemini vs FLAN-T5 comparison
- **Figure 16**: Fallback Mechanism Performance - Reliability and availability analysis
- **Figure 17**: Bilingual Support Effectiveness - Language handling performance

### Deployment Architecture (Figures 18-20)
- **Figure 18**: Deployment Options - Local, Docker, Cloud deployment architectures
- **Figure 19**: API Endpoints Structure - Complete REST API documentation
- **Figure 20**: Interface Comparison - Web UI, API, CLI comparison

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install visualization requirements
pip install -r requirements_visualization.txt
```

### 2. Generate All Figures

```bash
# Run the main generator script
python generate_figures.py
```

This will create a `figures_for_paper` directory containing all 20 figures in both PNG and PDF formats.

### 3. Output Location

All figures will be saved to:
```
figures_for_paper/
├── fig1_system_architecture.png
├── fig1_system_architecture.pdf
├── fig2_component_interaction.png
├── fig2_component_interaction.pdf
├── ...
└── fig20_interface_comparison.pdf
```

## 📁 Project Structure

```
visualizations/
├── __init__.py                    # Package initialization
├── system_architecture.py         # Figures 1-2: Architecture diagrams
├── rag_pipeline.py               # Figures 3-5: RAG process visualizations
├── performance_metrics.py        # Figures 6-10: Performance charts
├── data_analysis.py              # Figures 11-14: Data statistics
├── comparison_charts.py          # Figures 15-17: Comparison analysis
└── deployment_diagrams.py        # Figures 18-20: Deployment architectures

generate_figures.py               # Main script to generate all figures
requirements_visualization.txt    # Visualization dependencies
README.md                         # This file
```

## 🎨 Figure Specifications

All figures are generated with:
- **Resolution**: 300 DPI (publication quality)
- **Formats**: PNG (for presentations) and PDF (for LaTeX papers)
- **Style**: Professional academic style (seaborn-paper)
- **Fonts**: Serif fonts for readability
- **Colors**: Consistent color schemes throughout

## 📝 Customization

You can customize individual figures by editing the corresponding Python module:

```python
# Example: Modify system architecture colors
# Edit: visualizations/system_architecture.py

def generate_overall_architecture():
    # Change colors in the draw_component_box calls
    draw_component_box(ax, x, y, width, height, text, color='#YourColor')
```

## 🔧 Advanced Usage

### Generate Specific Figure Categories

```python
from visualizations import system_architecture, rag_pipeline

# Generate only system architecture figures
system_architecture.generate_all()

# Generate only RAG pipeline figures
rag_pipeline.generate_all()
```

### Modify Output Directory

```python
# Edit the OUTPUT_DIR in each module
OUTPUT_DIR = Path("custom_output_directory")
```

## 📊 Figure Usage in Paper

### Recommended Figure Placement

1. **Introduction Section**: Figure 1 (System Architecture)
2. **Methodology Section**: 
   - Figures 3-5 (RAG Pipeline)
   - Figure 14 (Data Processing)
3. **Implementation Section**:
   - Figure 2 (Component Interaction)
   - Figures 18-20 (Deployment)
4. **Results Section**:
   - Figures 6-10 (Performance Metrics)
   - Figures 11-13 (Data Analysis)
5. **Evaluation Section**:
   - Figures 15-17 (Comparison & Evaluation)

### LaTeX Integration

```latex
\begin{figure}[htbp]
\centering
\includegraphics[width=0.8\textwidth]{figures_for_paper/fig1_system_architecture.pdf}
\caption{Overall System Architecture showing the layered design of the Bangladesh Constitution Chatbot.}
\label{fig:system_architecture}
\end{figure}
```

## 📈 Data Sources

The visualizations use:
- **Simulated realistic data** based on actual system performance
- **Statistical distributions** (gamma, normal) for realistic variability
- **Actual configuration values** from the project (chunk sizes, model dimensions, etc.)
- **Measured metrics** where available (embedding dimensions, vector store sizes)

## 🎯 Key Metrics Visualized

- **Response Times**: Mean, median, distribution
- **Retrieval Quality**: Precision@K, Recall@K, F1-Score, MRR
- **System Resources**: CPU, Memory, Disk I/O, GPU usage
- **Language Support**: Detection accuracy, quality scores
- **Availability**: Uptime, fallback success rates
- **Scalability**: Performance vs. dataset size

## 🔍 Quality Assurance

All figures are:
- ✅ High resolution (300 DPI)
- ✅ Properly labeled (axes, titles, legends)
- ✅ Consistent styling
- ✅ Colorblind-friendly palettes
- ✅ Publication-ready (no truncation, clear fonts)

## 🤝 Contributing

To add new figures:

1. Create a new function in the appropriate module
2. Follow the naming convention: `generate_<descriptive_name>()`
3. Use the `save_fig()` helper function
4. Add the function call to the module's `generate_all()` function
5. Update this README with the new figure description

## 📚 Citation

If you use these visualizations in your research, please cite:

```bibtex
@article{yourpaper2025,
  title={Bangladesh Constitution Chatbot: A RAG-based Bilingual Legal QA System},
  author={Your Name},
  journal={Journal Name},
  year={2025}
}
```

## 📧 Contact

For questions or issues regarding the visualizations, please open an issue on GitHub.

---

**Note**: All data in the visualizations is either simulated based on realistic system behavior or derived from actual system configurations. Adjust the values in the Python scripts if you have specific measured data from your deployment.
