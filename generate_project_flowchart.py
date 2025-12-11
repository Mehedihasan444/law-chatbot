"""
Generate Project Flowchart for Bangladesh Constitution Chatbot
Creates a comprehensive visual flowchart showing the complete system architecture
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
import numpy as np

# Set up the figure with a light background - increased size to prevent overflow
fig, ax = plt.subplots(1, 1, figsize=(26, 18))
ax.set_xlim(0, 26)
ax.set_ylim(0, 18)
ax.axis('off')
fig.patch.set_facecolor('#f8f9fa')
ax.set_facecolor('#f8f9fa')

# Color scheme
color_header = '#FFC107'  # Amber
color_process = '#A5D6A7'  # Light Green
color_service = '#90CAF9'  # Light Blue
color_storage = '#F48FB1'  # Light Pink
color_interface = '#CE93D8'  # Light Purple
color_model = '#FFE082'  # Light Amber

def create_box(ax, x, y, width, height, text, color, fontsize=11, bold=False):
    """Create a rounded box with text"""
    box = FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.15",
        linewidth=2.5,
        edgecolor='#495057',
        facecolor=color,
        zorder=2
    )
    ax.add_patch(box)
    
    weight = 'bold' if bold else 'normal'
    ax.text(
        x + width/2, y + height/2, text,
        ha='center', va='center',
        fontsize=fontsize,
        weight=weight,
        wrap=True,
        zorder=3,
        color='#212529'
    )
    return box

def create_arrow(ax, x1, y1, x2, y2, label='', style='-|>'):
    """Create an arrow between two points"""
    arrow = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle=style,
        linewidth=3,
        color='#495057',
        mutation_scale=25,
        zorder=1
    )
    ax.add_patch(arrow)
    
    if label:
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mid_x, mid_y + 0.25, label, ha='center', fontsize=9,
                bbox=dict(boxstyle='round,pad=0.4', facecolor='white', edgecolor='none', alpha=0.8))

def create_subprocess_box(ax, x, y, width, height, items, title=''):
    """Create a box with multiple sub-items"""
    # Main box
    box = FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.1",
        linewidth=2.5,
        edgecolor='#495057',
        facecolor=color_process,
        alpha=0.8,
        zorder=2
    )
    ax.add_patch(box)
    
    # Title
    if title:
        ax.text(x + width/2, y + height - 0.35, title,
                ha='center', va='center', fontsize=10, weight='bold', zorder=3, color='#212529')
    
    # Sub-items with better spacing
    item_height = (height - 0.6) / len(items)
    for i, item in enumerate(items):
        item_y = y + 0.2 + i * item_height
        item_box = FancyBboxPatch(
            (x + 0.2, item_y), width - 0.4, item_height - 0.1,
            boxstyle="round,pad=0.1",
            linewidth=2,
            edgecolor='#6c757d',
            facecolor='#fdfdfd',
            zorder=2
        )
        ax.add_patch(item_box)
        ax.text(x + width/2, item_y + (item_height - 0.1)/2, item,
                ha='center', va='center', fontsize=9, zorder=3, color='#343a40')

# ==================== TITLE ====================
ax.text(13, 17.2, '�🇩 Bangladesh Constitution Chatbot', 
        ha='center', va='center', fontsize=24, weight='bold', color='#343a40')
ax.text(13, 16.5, 'RAG-based Bilingual Legal Assistant System Architecture',
        ha='center', va='center', fontsize=14, style='italic', color='#6c757d')

# ==================== STAGE 1: DATA COLLECTION ====================
create_box(ax, 1, 14.5, 4, 0.8, 'Data Collection', color_header, fontsize=13, bold=True)

# Data sources
create_subprocess_box(ax, 1, 12, 4, 2.2, [
    'Constitution PDF (English)',
    'Constitution PDF (Bengali)',
    'Legal Documents'
], '')

create_box(ax, 2, 11.3, 2, 0.6, 'PyPDF2 / PDFPlumber', color_service, fontsize=10)

# ==================== STAGE 2: DATA PREPROCESSING ====================
create_box(ax, 6, 14.5, 4.5, 0.8, 'Data Preprocessing', color_header, fontsize=13, bold=True)

create_subprocess_box(ax, 6, 12, 4.5, 2.2, [
    'Text Extraction',
    'Cleaning & Normalization',
    'Article Segmentation',
    'Chunk Creation (512 tokens)',
    'Metadata Enrichment'
], '')

create_arrow(ax, 5, 13.1, 6, 13.1)

# ==================== STAGE 3: EMBEDDING & VECTORIZATION ====================
create_box(ax, 11.5, 14.5, 4, 0.8, 'Embedding Generation', color_header, fontsize=13, bold=True)

create_subprocess_box(ax, 11.5, 12, 4, 2.2, [
    'Sentence Transformers',
    'paraphrase-multilingual-mpnet-base-v2',
    'Vector Embeddings',
    'Dimension: 768'
], '')

create_arrow(ax, 10.5, 13.1, 11.5, 13.1)

# ==================== STAGE 4: VECTOR STORAGE ====================
create_box(ax, 16.5, 14.5, 4, 0.8, 'Vector Storage', color_header, fontsize=13, bold=True)

create_subprocess_box(ax, 16.5, 12, 4, 2.2, [
    'FAISS Index',
    'Bilingual Vectorstore',
    'Metadata Storage',
    'Fast Similarity Search'
], '')

create_arrow(ax, 15.5, 13.1, 16.5, 13.1)

# ==================== STAGE 5: MODEL SELECTION ====================
create_box(ax, 21.5, 14.5, 4, 0.8, 'LLM Selection', color_header, fontsize=13, bold=True)

# Primary model
create_box(ax, 21.5, 13.2, 4, 1, 'Primary: Gemini 2.0 Flash', color_model, fontsize=11, bold=True)

# Fallback model
create_box(ax, 21.5, 12, 4, 1, 'Fallback: FLAN-T5 Large\n(Offline Support)', color_model, fontsize=10)

create_arrow(ax, 20.5, 13.1, 21.5, 13.1)

# ==================== STAGE 6: RAG PIPELINE ====================
create_box(ax, 6, 10.5, 4.5, 0.8, 'RAG Pipeline', color_header, fontsize=13, bold=True)

create_subprocess_box(ax, 6, 8, 4.5, 2.2, [
    'Query Processing',
    'Language Detection',
    'Embedding Generation',
    'Semantic Search (FAISS)',
    'Context Retrieval (Top-K)',
    'Prompt Engineering'
], '')

create_arrow(ax, 18.5, 12, 13, 10.5, 'Initialize')

# ==================== STAGE 7: INFERENCE & FALLBACK ====================
create_box(ax, 11.5, 10.5, 4, 0.8, 'Inference Engine', color_header, fontsize=13, bold=True)

# Inference box with fallback mechanism
inference_x, inference_y = 11.5, 8
create_box(ax, inference_x, inference_y + 1.5, 4, 0.7, 'Try Gemini API', color_service, fontsize=10)
create_box(ax, inference_x + 0.4, inference_y + 0.7, 1.5, 0.6, 'Success ✓', '#A5D6A7', fontsize=9)
create_box(ax, inference_x + 2.1, inference_y + 0.7, 1.5, 0.6, 'Timeout ✗', '#F48FB1', fontsize=9)
create_box(ax, inference_x, inference_y, 4, 0.6, 'Auto Fallback to FLAN-T5', color_model, fontsize=9)

create_arrow(ax, 10.5, 9.1, 11.5, 9.1)
create_arrow(ax, 12.2, 8.7, 12.2, 8.0, 'Fail')
create_arrow(ax, 14.8, 8.7, 14.8, 8.0, 'Fail')

# ==================== STAGE 8: RESPONSE GENERATION ====================
create_box(ax, 16.5, 10.5, 4, 0.8, 'Response Processing', color_header, fontsize=13, bold=True)

create_subprocess_box(ax, 16.5, 8, 4, 2.2, [
    'Answer Generation',
    'Citation Extraction',
    'Legal Disclaimer',
    'Bilingual Support',
    'Context Formatting',
    'Confidence Scoring'
], '')

create_arrow(ax, 15.5, 9.1, 16.5, 9.1)

# ==================== STAGE 9: INTERFACES ====================
create_box(ax, 21.5, 10.5, 4, 0.8, 'User Interfaces', color_header, fontsize=13, bold=True)

# Three interface options
create_box(ax, 21.5, 9.4, 4, 0.8, 'Streamlit Web UI', color_interface, fontsize=10)
create_box(ax, 21.5, 8.4, 4, 0.8, 'FastAPI REST API', color_interface, fontsize=10)
create_box(ax, 21.5, 7.4, 4, 0.8, 'CLI Terminal', color_interface, fontsize=10)

create_arrow(ax, 20.5, 9.1, 21.5, 9.1)

# ==================== STAGE 10: DEPLOYMENT ====================
create_box(ax, 11.5, 6.5, 4, 0.8, 'Deployment & Delivery', color_header, fontsize=13, bold=True)

create_subprocess_box(ax, 11.5, 4, 4, 2.2, [
    'Docker Container',
    'Docker Compose',
    'Environment Config',
    'Health Monitoring',
    'Rate Limiting',
    'Error Logging'
], '')

# ==================== SUPPORTING SERVICES (Bottom Section) ====================
# Left column - Services
create_box(ax, 1, 6.5, 4.5, 0.8, 'Core Services', color_header, fontsize=13, bold=True)
create_subprocess_box(ax, 1, 4, 4.5, 2.2, [
    'Embedding Service',
    'LLM Service (Gemini + Fallback)',
    'Vectorstore Service',
    'Retrieval Service',
    'Language Detection'
], '')

# Right column - Features
create_box(ax, 16.5, 6.5, 4, 0.8, 'Key Features', color_header, fontsize=13, bold=True)
create_subprocess_box(ax, 16.5, 4, 4, 2.2, [
    'Bilingual Support',
    'Hybrid Search',
    'Smart Fallback',
    'Citation Support',
    'Zero Downtime'
], '')

# Monitoring and Validation
create_box(ax, 21.5, 6.5, 4, 0.8, 'Monitoring & Validation', color_header, fontsize=13, bold=True)
create_subprocess_box(ax, 21.5, 4, 4, 2.2, [
    'Environment Validation',
    'System Health Checks',
    'Resource Monitoring',
    'Performance Metrics',
    'Error Tracking'
], '')

# ==================== DATA FLOW ARROWS ====================
# Vertical flow from deployment to interfaces
create_arrow(ax, 13.5, 6.5, 13.5, 7.4, '', '->')
create_arrow(ax, 23.5, 7.4, 23.5, 6.5, 'Monitor', '->')

# Connection from services to RAG
create_arrow(ax, 5.5, 6.5, 8.25, 8, '', '->')

# ==================== LEGEND ====================
legend_y = 3
ax.text(1.5, legend_y, 'Legend:', fontsize=12, weight='bold', color='#343a40')

legend_items = [
    (color_header, 'Stage Headers', 1.5, legend_y - 0.6),
    (color_process, 'Processing', 1.5, legend_y - 1.2),
    (color_service, 'Services', 6, legend_y - 0.6),
    (color_storage, 'Storage', 6, legend_y - 1.2),
    (color_model, 'AI Models', 10.5, legend_y - 0.6),
    (color_interface, 'Interfaces', 10.5, legend_y - 1.2),
]

for color, label, x, y in legend_items:
    legend_box = Rectangle((x, y), 0.5, 0.4, facecolor=color, edgecolor='#495057', linewidth=2)
    ax.add_patch(legend_box)
    ax.text(x + 0.6, y + 0.2, label, fontsize=10, va='center', color='#343a40')

# ==================== ANNOTATIONS ====================
# Add system highlights
ax.text(13, 2.2, 'Highlights: High Accuracy RAG • Bilingual (EN/BN) • Smart Fallback • Citation Support • Production Ready', 
        ha='center', fontsize=12, style='italic',
        bbox=dict(boxstyle='round,pad=0.8', facecolor='#fff3cd', edgecolor='#495057', linewidth=2.5))

# Add workflow direction indicators
ax.text(13, 15.6, 'Data Flow', ha='center', fontsize=11, weight='bold', color='#6c757d')
ax.text(13, 11.6, 'Processing Pipeline', ha='center', fontsize=11, weight='bold', color='#6c757d')
ax.text(13, 7.6, 'Inference & Delivery', ha='center', fontsize=11, weight='bold', color='#6c757d')

# User interaction flow
create_arrow(ax, 23.5, 8.4, 18.5, 8.4, 'User Query', '<-')
create_arrow(ax, 18.5, 9.4, 23.5, 9.4, 'Response', '->')

# ==================== FOOTER ====================
ax.text(13, 0.8, '© 2025 Bangladesh Constitution Chatbot | Built with FastAPI, Streamlit & Google Gemini', 
        ha='center', fontsize=10, color='#6c757d')
ax.text(13, 0.4, 'RAG Architecture: LangChain • FAISS • Sentence Transformers • FLAN-T5', 
        ha='center', fontsize=9, color='#868e96')

# Save the figure
plt.tight_layout(pad=1.0)
plt.savefig('figures_for_paper/fig1_system_architecture.png', dpi=300, bbox_inches='tight', facecolor='#f8f9fa')
plt.savefig('figures_for_paper/fig1_system_architecture.pdf', bbox_inches='tight', facecolor='#f8f9fa')

print("✅ Project flowchart generated successfully!")
print("📁 Saved to:")
print("   - figures_for_paper/fig1_system_architecture.png")
print("   - figures_for_paper/fig1_system_architecture.pdf")

plt.show()
