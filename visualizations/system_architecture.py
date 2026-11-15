"""
System Architecture Visualizations
Generates diagrams showing the overall system structure
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / "figures"

def save_fig(fig, name):
    """Helper to save figure"""
    fig.savefig(OUTPUT_DIR / f"{name}.png", dpi=300, bbox_inches='tight')
    fig.savefig(OUTPUT_DIR / f"{name}.pdf", bbox_inches='tight')
    plt.close()
    print(f"  ✓ {name}")


def draw_component_box(ax, x, y, width, height, text, color='lightblue', fontsize=10):
    """Draw a component box"""
    box = FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.05",
        edgecolor='black',
        facecolor=color,
        linewidth=2
    )
    ax.add_patch(box)
    ax.text(x + width/2, y + height/2, text,
            ha='center', va='center',
            fontsize=fontsize, fontweight='bold',
            wrap=True)


def draw_arrow(ax, x1, y1, x2, y2, label='', style='->', color='black'):
    """Draw arrow between components"""
    arrow = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle=style,
        color=color,
        linewidth=2,
        mutation_scale=20
    )
    ax.add_patch(arrow)
    if label:
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mid_x, mid_y, label, fontsize=8,
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))


def generate_overall_architecture():
    """Figure 1: Overall System Architecture"""
    fig, ax = plt.subplots(figsize=(12, 10), constrained_layout=True)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Title
    ax.text(5, 11.5, 'Bangladesh Constitution Chatbot\nSystem Architecture',
            ha='center', fontsize=14, fontweight='bold')
    
    # Layer 1: User Interface Layer
    ax.text(0.5, 10.5, 'User Interface Layer', fontsize=11, fontweight='bold')
    draw_component_box(ax, 0.5, 9.5, 2.5, 0.8, 'Web UI\n(Streamlit)', '#FFE5B4')
    draw_component_box(ax, 3.5, 9.5, 2.5, 0.8, 'REST API\n(FastAPI)', '#FFE5B4')
    draw_component_box(ax, 6.5, 9.5, 2.5, 0.8, 'CLI\n(Terminal)', '#FFE5B4')
    
    # Layer 2: Application Layer
    ax.text(0.5, 8.5, 'Application Layer', fontsize=11, fontweight='bold')
    draw_component_box(ax, 2, 7.5, 5.5, 0.8, 'Chatbot Controller\n(Query Processing & Response)', '#B4D7FF')
    
    # Layer 3: RAG Pipeline
    ax.text(0.5, 6.5, 'RAG Pipeline Layer', fontsize=11, fontweight='bold')
    draw_component_box(ax, 1, 5.5, 7.5, 0.8, 'RAG Orchestrator\n(Retrieval-Augmented Generation)', '#D4FFB4')
    
    # Layer 4: Service Layer
    ax.text(0.5, 4.5, 'Service Layer', fontsize=11, fontweight='bold')
    draw_component_box(ax, 0.5, 3.2, 2, 1, 'Embedding\nService\n(MiniLM-L6)', '#FFD4D4', 9)
    draw_component_box(ax, 3, 3.2, 2, 1, 'LLM Service\n(Gemini API +\nFLAN-T5)', '#FFD4D4', 9)
    draw_component_box(ax, 5.5, 3.2, 2, 1, 'Retrieval\nService\n(Hybrid Search)', '#FFD4D4', 9)
    draw_component_box(ax, 8, 3.2, 1.5, 1, 'Vector\nStore\n(FAISS)', '#FFD4D4', 9)
    
    # Layer 5: Data Layer
    ax.text(0.5, 2.2, 'Data Layer', fontsize=11, fontweight='bold')
    draw_component_box(ax, 1.5, 0.8, 2.5, 1, 'Constitution\nEN PDF', '#E5E5E5', 9)
    draw_component_box(ax, 4.5, 0.8, 2.5, 1, 'Constitution\nBN PDF', '#E5E5E5', 9)
    draw_component_box(ax, 7.5, 0.8, 1.5, 1, 'Processed\nChunks', '#E5E5E5', 9)
    
    # Arrows - User Interface to Application
    draw_arrow(ax, 1.75, 9.5, 3.5, 8.3, 'HTTP')
    draw_arrow(ax, 4.75, 9.5, 4.75, 8.3, 'HTTP')
    draw_arrow(ax, 7.75, 9.5, 5.5, 8.3, 'Direct')
    
    # Application to RAG
    draw_arrow(ax, 4.75, 7.5, 4.75, 6.3, 'Query')
    
    # RAG to Services
    draw_arrow(ax, 2.5, 5.5, 1.5, 4.2, '1')
    draw_arrow(ax, 4, 5.5, 4, 4.2, '2')
    draw_arrow(ax, 6.5, 5.5, 6.5, 4.2, '3')
    draw_arrow(ax, 7.5, 5.5, 8.5, 4.2, '4')
    
    # Services to Data
    draw_arrow(ax, 1.5, 3.2, 2.5, 1.8, 'Embed')
    draw_arrow(ax, 6.5, 3.2, 5.75, 1.8, 'Retrieve')
    draw_arrow(ax, 8.75, 3.2, 8.25, 1.8, 'Store')
    
    # Legend
    legend_elements = [
        mpatches.Patch(color='#FFE5B4', label='User Interface'),
        mpatches.Patch(color='#B4D7FF', label='Application Logic'),
        mpatches.Patch(color='#D4FFB4', label='RAG Pipeline'),
        mpatches.Patch(color='#FFD4D4', label='Services'),
        mpatches.Patch(color='#E5E5E5', label='Data Storage')
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=9)
    
    save_fig(fig, 'fig1_system_architecture')


def generate_component_interaction():
    """Figure 2: Component Interaction Diagram"""
    fig, ax = plt.subplots(figsize=(14, 8), constrained_layout=True)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    ax.text(7, 9.5, 'Component Interaction Flow', ha='center',
            fontsize=14, fontweight='bold')
    
    # Components in sequence
    components = [
        (1, 7, 1.8, 1.2, 'User\nQuery', '#FFE5B4'),
        (3.5, 7, 2, 1.2, 'Language\nDetection', '#B4D7FF'),
        (6, 7, 2, 1.2, 'Query\nEmbedding', '#D4FFB4'),
        (8.5, 7, 2, 1.2, 'Vector\nSearch', '#FFD4D4'),
        (11, 7, 2.5, 1.2, 'Context\nRetrieval', '#FFE5B4'),
        (2, 4, 2.5, 1.2, 'LLM\nGeneration', '#B4D7FF'),
        (5.5, 4, 2.5, 1.2, 'Response\nFormatting', '#D4FFB4'),
        (9, 4, 2.5, 1.2, 'Citation\nExtraction', '#FFD4D4'),
        (5, 1, 3, 1.2, 'Final Response\nto User', '#FFE5B4')
    ]
    
    for x, y, w, h, text, color in components:
        draw_component_box(ax, x, y, w, h, text, color, 9)
    
    # Flow arrows with labels
    draw_arrow(ax, 2.8, 7.6, 3.5, 7.6, '1', color='#2E86AB')
    draw_arrow(ax, 5.5, 7.6, 6, 7.6, '2', color='#2E86AB')
    draw_arrow(ax, 8, 7.6, 8.5, 7.6, '3', color='#2E86AB')
    draw_arrow(ax, 10.5, 7.6, 11, 7.6, '4', color='#2E86AB')
    draw_arrow(ax, 12.25, 7, 4, 5.2, '5', color='#2E86AB')
    draw_arrow(ax, 3.25, 4, 5.5, 4.6, '6', color='#2E86AB')
    draw_arrow(ax, 8, 4.6, 9, 4.6, '7', color='#2E86AB')
    draw_arrow(ax, 10.25, 4, 7, 2.2, '8', color='#2E86AB')
    draw_arrow(ax, 6.5, 1, 6.5, 0.3, '9', color='#2E86AB')
    
    # Process descriptions
    processes = [
        (2, 6.3, '1. Detect language (EN/BN)'),
        (4.5, 6.3, '2. Generate embeddings'),
        (7, 6.3, '3. Search vector DB'),
        (10, 6.3, '4. Retrieve top-k chunks'),
        (7, 5.8, '5. Pass context to LLM'),
        (4, 3.3, '6. Format with citations'),
        (7.5, 3.3, '7. Extract references'),
        (8, 2.8, '8. Add disclaimers'),
        (6.5, 0.5, '9. Return to user')
    ]
    
    for x, y, text in processes:
        ax.text(x, y, text, fontsize=8, style='italic',
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))
    
    save_fig(fig, 'fig2_component_interaction')


def generate_all():
    """Generate all system architecture figures"""
    print("  Generating system architecture diagrams...")
    generate_overall_architecture()
    generate_component_interaction()
