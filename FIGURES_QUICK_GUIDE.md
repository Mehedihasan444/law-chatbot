# Quick Guide: Generating Journal Paper Figures

## 📝 Overview

This guide helps you generate all 20 figures for your journal paper in under 5 minutes.

## 🚀 Steps

### Step 1: Install Visualization Dependencies

Open your terminal in the project root and run:

```bash
# Windows
pip install -r requirements_visualization.txt

# Linux/Mac
pip3 install -r requirements_visualization.txt
```

This installs:
- `matplotlib` - For creating all figures
- `seaborn` - For beautiful statistical visualizations
- `numpy` - For numerical computations

### Step 2: Generate All Figures

```bash
# Run the generator
python generate_figures.py
```

You'll see output like:
```
============================================================
Generating Figures for Journal Paper
Bangladesh Constitution Chatbot
============================================================

📊 Generating System Architecture Diagrams...
  ✓ fig1_system_architecture
  ✓ fig2_component_interaction

📊 Generating RAG Pipeline Visualizations...
  ✓ fig3_rag_pipeline_detailed
  ✓ fig4_embedding_process
  ✓ fig5_hybrid_retrieval

... (continues for all 20 figures)

============================================================
✅ All figures saved to: D:\projects\law chatbot\figures_for_paper
============================================================
```

### Step 3: Access Your Figures

All figures are now in the `figures_for_paper` directory:

```
figures_for_paper/
├── fig1_system_architecture.png         (for PowerPoint/presentations)
├── fig1_system_architecture.pdf         (for LaTeX papers)
├── fig2_component_interaction.png
├── fig2_component_interaction.pdf
├── ... (38 files total: 20 PNG + 20 PDF)
```

## 📊 Figure Categories

### 🏗️ Architecture & Design (6 figures)
- Figures 1-2: System architecture
- Figures 3-5: RAG pipeline
- Figure 14: Data processing

### 📈 Performance & Metrics (5 figures)
- Figures 6-7: Response times and latency
- Figure 8: Retrieval effectiveness
- Figures 9-10: Resource utilization

### 📚 Data & Language (3 figures)
- Figures 11-12: Document and language statistics
- Figure 13: Vector store analysis

### 🔍 Evaluation & Comparison (3 figures)
- Figure 15: Model comparison
- Figure 16: Fallback mechanism
- Figure 17: Bilingual support

### 🚀 Deployment (3 figures)
- Figure 18: Deployment options
- Figure 19: API endpoints
- Figure 20: Interface comparison

## 📝 Using Figures in Your Paper

### For LaTeX

```latex
\usepackage{graphicx}

\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures_for_paper/fig1_system_architecture.pdf}
\caption{Overall system architecture of the Bangladesh Constitution Chatbot showing the layered design with user interfaces, application logic, RAG pipeline, services, and data layers.}
\label{fig:architecture}
\end{figure}
```

### For Microsoft Word

1. Go to Insert → Pictures
2. Select the PNG file (e.g., `fig1_system_architecture.png`)
3. Resize to fit your page (300 DPI ensures quality)
4. Add caption using Insert → Caption

### For Google Docs

1. Insert → Image → Upload from computer
2. Select PNG files
3. Resize as needed (quality maintained)
4. Add caption below

## 🎨 Customization Tips

### Change Colors

Edit the Python files in `visualizations/` directory. For example:

```python
# visualizations/system_architecture.py
draw_component_box(ax, x, y, width, height, text, color='#YOUR_COLOR')
```

### Modify Data

Update the data arrays in each function:

```python
# Example in performance_metrics.py
gemini_scores = [92, 89, 91, 94, 96]  # Change these values
```

### Adjust Figure Size

```python
fig, ax = plt.subplots(figsize=(14, 10))  # Change width, height
```

## 🐛 Troubleshooting

### Issue: "Module not found: matplotlib"
**Solution**: 
```bash
pip install matplotlib seaborn numpy
```

### Issue: "Permission denied" when saving
**Solution**: 
- Close any open image viewers showing the figures
- Run terminal as administrator (Windows)

### Issue: Figures look blurry in Word
**Solution**: 
- Use PDF format for Word 365
- Or ensure PNG files are inserted at 100% scale (don't enlarge)

### Issue: Colors don't match your conference template
**Solution**: 
- Edit color codes in the Python files
- Common colors: `'#2E86AB'` (blue), `'#A23B72'` (purple), `'#F18F01'` (orange)

## ⚡ Quick Commands

```bash
# Generate all figures
python generate_figures.py

# View figures directory
cd figures_for_paper
ls  # Linux/Mac
dir # Windows

# Count figures
ls *.png | wc -l  # Should show 20

# Delete and regenerate
rm -rf figures_for_paper  # Linux/Mac
rmdir /s figures_for_paper  # Windows
python generate_figures.py
```

## 📦 What Each Figure Shows

| Figure | Type | Title | Best Used In |
|--------|------|-------|--------------|
| 1-2 | Architecture | System design | Methodology |
| 3-5 | Process Flow | RAG pipeline | Implementation |
| 6-7 | Bar/Histogram | Performance | Results |
| 8 | Line Charts | Retrieval quality | Evaluation |
| 9-10 | Mixed Charts | Resource usage | Results |
| 11-13 | Statistics | Data analysis | Data Description |
| 14 | Flowchart | Processing pipeline | Methodology |
| 15-17 | Comparison | Model evaluation | Discussion |
| 18-20 | Architecture | Deployment | Implementation |

## 📊 Figure Quality Checklist

Before submitting your paper, verify:

- [ ] All 20 figures generated successfully
- [ ] Figures are 300 DPI (check file properties)
- [ ] Text is readable at target size
- [ ] Colors are distinguishable (check in grayscale)
- [ ] Legends are clear and complete
- [ ] Axis labels are present and descriptive
- [ ] File sizes are reasonable (<5MB each)
- [ ] PDF format used for LaTeX papers
- [ ] PNG format used for PowerPoint/Word

## 🎓 Recommended Paper Structure

```
1. Introduction
   └── Figure 1: System Architecture

2. Related Work
   └── (No figures)

3. Methodology
   ├── Figure 3: RAG Pipeline
   ├── Figure 4: Embedding Process
   ├── Figure 5: Hybrid Retrieval
   └── Figure 14: Data Processing

4. Implementation
   ├── Figure 2: Component Interaction
   ├── Figure 18: Deployment Options
   └── Figure 19: API Endpoints

5. Experiments
   ├── Figure 11: Document Statistics
   ├── Figure 12: Language Distribution
   └── Figure 13: Vector Store

6. Results
   ├── Figure 6: Response Times
   ├── Figure 7: Latency Breakdown
   ├── Figure 8: Retrieval Effectiveness
   ├── Figure 9: Token Usage
   └── Figure 10: Resource Utilization

7. Discussion
   ├── Figure 15: Model Comparison
   ├── Figure 16: Fallback Mechanism
   └── Figure 17: Bilingual Effectiveness

8. Conclusion
   └── Figure 20: Interface Comparison
```

## 💡 Pro Tips

1. **Generate early**: Create figures before writing to identify gaps
2. **Use vector formats**: PDF for papers, SVG for web
3. **Consistent styling**: Don't modify colors between figures
4. **Reference in text**: Every figure should be mentioned
5. **Meaningful captions**: Explain what the figure shows
6. **Label subfigures**: Use (a), (b), (c) for multi-panel figures
7. **Check conference requirements**: Some limit figure count
8. **Keep source files**: Save Python scripts for revisions

## 📞 Need Help?

- Check `visualizations/README.md` for detailed documentation
- Review individual Python files for specific figures
- Open GitHub issue for bugs
- Email for collaboration opportunities

---

**Ready to generate?** Run: `python generate_figures.py` 🚀
