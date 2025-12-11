"""
Fix Figure 1 - System Architecture with proper legend positioning
Addresses Issue #6: Legend overlap problem
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

def create_fixed_figure1():
    """
    Generate System Architecture diagram with legend positioned to avoid overlap
    """
    
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Define colors
    color_interface = '#E3F2FD'  # Light blue
    color_orchestration = '#FFF3E0'  # Light orange
    color_service = '#E8F5E9'  # Light green
    color_storage = '#F3E5F5'  # Light purple
    
    # Component dimensions
    box_width = 1.8
    box_height = 0.8
    
    # Layer 1: User Interface (Top)
    interface_y = 8.5
    streamlit_box = FancyBboxPatch((1, interface_y), box_width, box_height,
                                   boxstyle="round,pad=0.05", 
                                   edgecolor='black', facecolor=color_interface,
                                   linewidth=2)
    ax.add_patch(streamlit_box)
    ax.text(1 + box_width/2, interface_y + box_height/2, 'Streamlit UI\n(Web Interface)',
            ha='center', va='center', fontsize=10, weight='bold')
    
    fastapi_box = FancyBboxPatch((4, interface_y), box_width, box_height,
                                 boxstyle="round,pad=0.05",
                                 edgecolor='black', facecolor=color_interface,
                                 linewidth=2)
    ax.add_patch(fastapi_box)
    ax.text(4 + box_width/2, interface_y + box_height/2, 'FastAPI\n(REST API)',
            ha='center', va='center', fontsize=10, weight='bold')
    
    cli_box = FancyBboxPatch((7, interface_y), box_width, box_height,
                             boxstyle="round,pad=0.05",
                             edgecolor='black', facecolor=color_interface,
                             linewidth=2)
    ax.add_patch(cli_box)
    ax.text(7 + box_width/2, interface_y + box_height/2, 'CLI\n(Command Line)',
            ha='center', va='center', fontsize=10, weight='bold')
    
    # Layer 2: RAG Pipeline (Orchestration)
    rag_y = 6.5
    rag_box = FancyBboxPatch((3.5, rag_y), 3, box_height,
                             boxstyle="round,pad=0.05",
                             edgecolor='black', facecolor=color_orchestration,
                             linewidth=2)
    ax.add_patch(rag_box)
    ax.text(5, rag_y + box_height/2, 'RAG Pipeline\n(ConstitutionRAG)',
            ha='center', va='center', fontsize=11, weight='bold')
    
    # Layer 3: Services
    service_y = 4.5
    
    # Embedding Service
    embedding_box = FancyBboxPatch((0.5, service_y), box_width, box_height,
                                   boxstyle="round,pad=0.05",
                                   edgecolor='black', facecolor=color_service,
                                   linewidth=2)
    ax.add_patch(embedding_box)
    ax.text(0.5 + box_width/2, service_y + box_height/2, 'Embedding\nService',
            ha='center', va='center', fontsize=10, weight='bold')
    
    # LLM Service
    llm_box = FancyBboxPatch((3, service_y), box_width, box_height,
                             boxstyle="round,pad=0.05",
                             edgecolor='black', facecolor=color_service,
                             linewidth=2)
    ax.add_patch(llm_box)
    ax.text(3 + box_width/2, service_y + box_height/2, 'LLM Service\n(Gemini API)',
            ha='center', va='center', fontsize=10, weight='bold')
    
    # Retrieval Service
    retrieval_box = FancyBboxPatch((5.5, service_y), box_width, box_height,
                                   boxstyle="round,pad=0.05",
                                   edgecolor='black', facecolor=color_service,
                                   linewidth=2)
    ax.add_patch(retrieval_box)
    ax.text(5.5 + box_width/2, service_y + box_height/2, 'Retrieval\nService',
            ha='center', va='center', fontsize=10, weight='bold')
    
    # Fallback Handler
    fallback_box = FancyBboxPatch((8, service_y), box_width, box_height,
                                  boxstyle="round,pad=0.05",
                                  edgecolor='black', facecolor=color_service,
                                  linewidth=2)
    ax.add_patch(fallback_box)
    ax.text(8 + box_width/2, service_y + box_height/2, 'Fallback\nHandler',
            ha='center', va='center', fontsize=10, weight='bold')
    
    # Layer 4: Storage
    storage_y = 2.5
    vectorstore_box = FancyBboxPatch((3.5, storage_y), 3, box_height,
                                     boxstyle="round,pad=0.05",
                                     edgecolor='black', facecolor=color_storage,
                                     linewidth=2)
    ax.add_patch(vectorstore_box)
    ax.text(5, storage_y + box_height/2, 'FAISS Vectorstore\n(Constitution Embeddings)',
            ha='center', va='center', fontsize=11, weight='bold')
    
    # Layer labels (on left side)
    ax.text(-0.3, interface_y + box_height/2, 'Layer 1:\nInterface', 
            ha='right', va='center', fontsize=9, style='italic', color='gray')
    ax.text(-0.3, rag_y + box_height/2, 'Layer 2:\nOrchestration', 
            ha='right', va='center', fontsize=9, style='italic', color='gray')
    ax.text(-0.3, service_y + box_height/2, 'Layer 3:\nServices', 
            ha='right', va='center', fontsize=9, style='italic', color='gray')
    ax.text(-0.3, storage_y + box_height/2, 'Layer 4:\nStorage', 
            ha='right', va='center', fontsize=9, style='italic', color='gray')
    
    # Arrows - Data Flow (solid)
    # Interface → RAG
    arrow1 = FancyArrowPatch((1.9, interface_y), (4.5, rag_y + box_height),
                            arrowstyle='->', mutation_scale=20, linewidth=2,
                            color='#1976D2')
    ax.add_patch(arrow1)
    
    arrow2 = FancyArrowPatch((4.9, interface_y), (5, rag_y + box_height),
                            arrowstyle='->', mutation_scale=20, linewidth=2,
                            color='#1976D2')
    ax.add_patch(arrow2)
    
    arrow3 = FancyArrowPatch((7.9, interface_y), (5.5, rag_y + box_height),
                            arrowstyle='->', mutation_scale=20, linewidth=2,
                            color='#1976D2')
    ax.add_patch(arrow3)
    
    # RAG → Services
    arrow4 = FancyArrowPatch((4, rag_y), (1.4, service_y + box_height),
                            arrowstyle='->', mutation_scale=20, linewidth=2,
                            color='#1976D2')
    ax.add_patch(arrow4)
    
    arrow5 = FancyArrowPatch((5, rag_y), (3.9, service_y + box_height),
                            arrowstyle='->', mutation_scale=20, linewidth=2,
                            color='#1976D2')
    ax.add_patch(arrow5)
    
    arrow6 = FancyArrowPatch((6, rag_y), (6.4, service_y + box_height),
                            arrowstyle='->', mutation_scale=20, linewidth=2,
                            color='#1976D2')
    ax.add_patch(arrow6)
    
    # Services → Vectorstore
    arrow7 = FancyArrowPatch((1.4, service_y), (4, storage_y + box_height),
                            arrowstyle='<->', mutation_scale=20, linewidth=2,
                            color='#388E3C')
    ax.add_patch(arrow7)
    
    arrow8 = FancyArrowPatch((6.4, service_y), (6, storage_y + box_height),
                            arrowstyle='<->', mutation_scale=20, linewidth=2,
                            color='#388E3C')
    ax.add_patch(arrow8)
    
    # Fallback control flow (dashed)
    arrow9 = FancyArrowPatch((3.9, service_y + 0.2), (8, service_y + 0.2),
                            arrowstyle='->', mutation_scale=20, linewidth=1.5,
                            linestyle='--', color='#D32F2F')
    ax.add_patch(arrow9)
    
    # Response flow back (dashed)
    arrow10 = FancyArrowPatch((5.5, rag_y + box_height), (5.5, interface_y),
                             arrowstyle='->', mutation_scale=20, linewidth=1.5,
                             linestyle='--', color='#F57C00')
    ax.add_patch(arrow10)
    
    # Legend - POSITIONED OUTSIDE to avoid overlap
    legend_elements = [
        mpatches.Patch(facecolor=color_interface, edgecolor='black', label='Interface Layer'),
        mpatches.Patch(facecolor=color_orchestration, edgecolor='black', label='Orchestration Layer'),
        mpatches.Patch(facecolor=color_service, edgecolor='black', label='Service Layer'),
        mpatches.Patch(facecolor=color_storage, edgecolor='black', label='Storage Layer'),
        mpatches.Patch(facecolor='none', edgecolor='none', label=''),  # Spacer
        mpatches.FancyArrow(0, 0, 0.5, 0, width=0.1, color='#1976D2', label='Query Data Flow'),
        mpatches.FancyArrow(0, 0, 0.5, 0, width=0.1, color='#388E3C', label='DB Operations'),
        mpatches.FancyArrow(0, 0, 0.5, 0, width=0.05, linestyle='--', 
                           color='#D32F2F', label='Fallback Control'),
        mpatches.FancyArrow(0, 0, 0.5, 0, width=0.05, linestyle='--',
                           color='#F57C00', label='Response Flow'),
    ]
    
    # Position legend BELOW the figure to avoid overlap
    legend = ax.legend(handles=legend_elements, 
                      loc='upper center',
                      bbox_to_anchor=(0.5, -0.05),  # Below the plot
                      ncol=3,  # 3 columns
                      frameon=True,
                      fancybox=True,
                      shadow=True,
                      fontsize=9)
    
    # Title
    ax.text(5, 9.7, 'System Architecture - Four-Layer Design',
            ha='center', va='center', fontsize=14, weight='bold')
    
    plt.tight_layout()
    
    # Save with tight bounding box to include legend
    plt.savefig('fig1_system_architecture_fixed.pdf', 
                dpi=300, bbox_inches='tight', format='pdf')
    plt.savefig('fig1_system_architecture_fixed.png', 
                dpi=300, bbox_inches='tight', format='png')
    
    print("✅ Figure 1 generated with fixed legend positioning")
    print("   Saved as: fig1_system_architecture_fixed.pdf/png")
    print("   Legend positioned below diagram to avoid overlap")
    
    plt.show()


def create_simple_figure1_alternative():
    """
    Alternative simpler version with legend on the side
    """
    
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Define colors
    colors = {
        'interface': '#4A90E2',
        'orchestration': '#F5A623',
        'service': '#7ED321',
        'storage': '#BD10E0'
    }
    
    # Simplified boxes
    components = [
        # (x, y, width, height, label, color_key)
        (1, 8, 2, 0.8, 'User\nInterfaces', 'interface'),
        (1, 6.5, 7, 0.8, 'RAG Pipeline', 'orchestration'),
        (0.5, 4.5, 1.8, 0.8, 'Embedding', 'service'),
        (3, 4.5, 1.8, 0.8, 'LLM', 'service'),
        (5.5, 4.5, 1.8, 0.8, 'Retrieval', 'service'),
        (1, 2.5, 4, 0.8, 'FAISS Vectorstore', 'storage'),
    ]
    
    for x, y, w, h, label, color_key in components:
        box = FancyBboxPatch((x, y), w, h,
                            boxstyle="round,pad=0.05",
                            edgecolor='black',
                            facecolor=colors[color_key],
                            linewidth=2,
                            alpha=0.7)
        ax.add_patch(box)
        ax.text(x + w/2, y + h/2, label,
               ha='center', va='center',
               fontsize=10, weight='bold',
               color='white')
    
    # Add arrows (simplified)
    arrows = [
        (2, 8, 4, 7.3),  # Interface → RAG
        (3, 6.5, 1.4, 5.3),  # RAG → Embedding
        (4.5, 6.5, 3.9, 5.3),  # RAG → LLM
        (6, 6.5, 6.4, 5.3),  # RAG → Retrieval
        (1.4, 4.5, 3, 3.3),  # Services → DB
    ]
    
    for x1, y1, x2, y2 in arrows:
        arrow = FancyArrowPatch((x1, y1), (x2, y2),
                               arrowstyle='->', mutation_scale=20,
                               linewidth=2, color='#333')
        ax.add_patch(arrow)
    
    # Legend on the RIGHT side
    legend_x = 9.5
    legend_y = 7
    legend_spacing = 0.8
    
    ax.text(legend_x, legend_y + 1.5, 'Components:',
           fontsize=11, weight='bold')
    
    legend_items = [
        ('Interface Layer', 'interface'),
        ('Orchestration', 'orchestration'),
        ('Service Layer', 'service'),
        ('Storage Layer', 'storage'),
    ]
    
    for i, (label, color_key) in enumerate(legend_items):
        y_pos = legend_y + 1 - (i * legend_spacing)
        
        # Color box
        box = mpatches.Rectangle((legend_x, y_pos - 0.2), 0.4, 0.4,
                                facecolor=colors[color_key],
                                edgecolor='black',
                                linewidth=1)
        ax.add_patch(box)
        
        # Label
        ax.text(legend_x + 0.6, y_pos, label,
               fontsize=9, va='center')
    
    # Title
    ax.text(4, 9.5, 'System Architecture',
           ha='center', fontsize=14, weight='bold')
    
    plt.tight_layout()
    plt.savefig('fig1_system_architecture_alternative.pdf',
               dpi=300, bbox_inches='tight')
    plt.savefig('fig1_system_architecture_alternative.png',
               dpi=300, bbox_inches='tight')
    
    print("✅ Alternative Figure 1 generated")
    print("   Legend positioned on the right side")
    
    plt.show()


if __name__ == "__main__":
    print("Generating fixed Figure 1 - System Architecture")
    print("="*60)
    
    print("\n📊 Option 1: Legend below diagram (recommended)")
    create_fixed_figure1()
    
    print("\n📊 Option 2: Legend on right side (alternative)")
    create_simple_figure1_alternative()
    
    print("\n✅ Both versions generated successfully!")
    print("\nRecommendation: Use the first version (legend below)")
    print("with the updated caption:")
    print("""
Fig. 1. System architecture showing four-layer design: (1) Interface layer
(Streamlit/FastAPI/CLI), (2) Orchestration layer (RAG pipeline), (3) Service 
layer (Embedding, LLM, Retrieval, Fallback), and (4) Storage layer (FAISS 
vectorstore). Solid blue arrows indicate query data flow; green arrows show 
database operations; dashed red arrows represent fallback control; dashed 
orange arrows show response flow back to users.
    """)
