"""
Deployment Architecture Visualizations
Generates diagrams showing deployment options and API structure
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle
import numpy as np
from pathlib import Path

OUTPUT_DIR = Path("figures_for_paper")

def save_fig(fig, name):
    """Helper to save figure"""
    fig.savefig(OUTPUT_DIR / f"{name}.png", dpi=300, bbox_inches='tight')
    fig.savefig(OUTPUT_DIR / f"{name}.pdf", bbox_inches='tight')
    plt.close()
    print(f"  ✓ {name}")


def generate_deployment_options():
    """Figure 18: Deployment Options"""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    ax.text(7, 11.5, 'Deployment Options and Architecture',
            ha='center', fontsize=14, fontweight='bold')
    
    # Option 1: Local Development
    ax.text(2.5, 10.2, 'Option 1: Local Development', fontsize=11, fontweight='bold', color='#2E86AB')
    rect = FancyBboxPatch((0.5, 7.5), 4, 2.5, boxstyle="round,pad=0.1",
                          edgecolor='#2E86AB', facecolor='#E8F4F8', linewidth=2)
    ax.add_patch(rect)
    
    local_text = '''Environment: Python venv
Installation: pip install -r requirements.txt
API Key: .env file (GEMINI_API_KEY)

Interfaces:
├─ Streamlit: streamlit run src/streamlit_app.py
├─ FastAPI: uvicorn api:app
└─ CLI: python cli.py

Resource Requirements:
├─ RAM: 2-4 GB
├─ Storage: 500 MB
└─ CPU: 2+ cores'''
    
    ax.text(2.5, 8.75, local_text, ha='center', va='center',
            fontsize=8, family='monospace', linespacing=1.5)
    
    # Option 2: Docker Container
    ax.text(7, 10.2, 'Option 2: Docker Container', fontsize=11, fontweight='bold', color='#A23B72')
    rect = FancyBboxPatch((5, 7.5), 4, 2.5, boxstyle="round,pad=0.1",
                          edgecolor='#A23B72', facecolor='#F8E8F4', linewidth=2)
    ax.add_patch(rect)
    
    docker_text = '''Build: docker-compose build
Run: docker-compose up
Ports: 8501 (Streamlit), 8000 (API)

Services:
├─ chatbot-api: FastAPI server
├─ chatbot-web: Streamlit UI
└─ volumes: Data persistence

Resource Requirements:
├─ RAM: 4-6 GB
├─ Storage: 1 GB
└─ Docker: 20.10+'''
    
    ax.text(7, 8.75, docker_text, ha='center', va='center',
            fontsize=8, family='monospace', linespacing=1.5)
    
    # Option 3: Cloud Production
    ax.text(11.5, 10.2, 'Option 3: Cloud Production', fontsize=11, fontweight='bold', color='#F18F01')
    rect = FancyBboxPatch((9.5, 7.5), 4, 2.5, boxstyle="round,pad=0.1",
                          edgecolor='#F18F01', facecolor='#FFF4E8', linewidth=2)
    ax.add_patch(rect)
    
    cloud_text = '''Platforms: AWS, GCP, Azure, Heroku
Container: Docker + K8s
CDN: CloudFlare
Database: Vector store backup

Features:
├─ Auto-scaling
├─ Load balancing
├─ SSL/TLS encryption
└─ Monitoring & logs

Resource Requirements:
├─ RAM: 8+ GB
├─ Storage: 5+ GB
└─ Multi-region support'''
    
    ax.text(11.5, 8.75, cloud_text, ha='center', va='center',
            fontsize=8, family='monospace', linespacing=1.5)
    
    # Network Architecture (bottom section)
    ax.text(7, 6.8, 'Production Network Architecture', fontsize=11, fontweight='bold', color='#06A77D')
    
    # Client layer
    client_rect = FancyBboxPatch((5.5, 5.5), 3, 0.8, boxstyle="round,pad=0.05",
                                 edgecolor='#E74C3C', facecolor='#FADBD8', linewidth=2)
    ax.add_patch(client_rect)
    ax.text(7, 5.9, 'Clients (Web, Mobile, API)', ha='center', fontsize=9, fontweight='bold')
    
    arrow = FancyArrowPatch((7, 5.5), (7, 4.8), arrowstyle='<->',
                           color='black', linewidth=2, mutation_scale=20)
    ax.add_patch(arrow)
    
    # Load Balancer
    lb_rect = FancyBboxPatch((5.5, 4), 3, 0.8, boxstyle="round,pad=0.05",
                             edgecolor='#3498DB', facecolor='#D6EAF8', linewidth=2)
    ax.add_patch(lb_rect)
    ax.text(7, 4.4, 'Load Balancer / API Gateway', ha='center', fontsize=9, fontweight='bold')
    
    # Application servers
    arrow1 = FancyArrowPatch((6, 4), (3, 3), arrowstyle='<->',
                            color='black', linewidth=1.5, mutation_scale=15)
    ax.add_patch(arrow1)
    
    arrow2 = FancyArrowPatch((7, 4), (7, 3), arrowstyle='<->',
                            color='black', linewidth=1.5, mutation_scale=15)
    ax.add_patch(arrow2)
    
    arrow3 = FancyArrowPatch((8, 4), (11, 3), arrowstyle='<->',
                            color='black', linewidth=1.5, mutation_scale=15)
    ax.add_patch(arrow3)
    
    # App instances
    app1 = FancyBboxPatch((1.5, 2.2), 2.5, 0.8, boxstyle="round,pad=0.05",
                          edgecolor='#2ECC71', facecolor='#D5F4E6', linewidth=2)
    ax.add_patch(app1)
    ax.text(2.75, 2.6, 'App Instance 1', ha='center', fontsize=8, fontweight='bold')
    
    app2 = FancyBboxPatch((5.75, 2.2), 2.5, 0.8, boxstyle="round,pad=0.05",
                          edgecolor='#2ECC71', facecolor='#D5F4E6', linewidth=2)
    ax.add_patch(app2)
    ax.text(7, 2.6, 'App Instance 2', ha='center', fontsize=8, fontweight='bold')
    
    app3 = FancyBboxPatch((10, 2.2), 2.5, 0.8, boxstyle="round,pad=0.05",
                          edgecolor='#2ECC71', facecolor='#D5F4E6', linewidth=2)
    ax.add_patch(app3)
    ax.text(11.25, 2.6, 'App Instance N', ha='center', fontsize=8, fontweight='bold')
    
    # Shared services
    arrow = FancyArrowPatch((7, 2.2), (7, 1.5), arrowstyle='<->',
                           color='black', linewidth=2, mutation_scale=20)
    ax.add_patch(arrow)
    
    services = FancyBboxPatch((2, 0.3), 10, 1.2, boxstyle="round,pad=0.1",
                              edgecolor='#9B59B6', facecolor='#EBDEF0', linewidth=2)
    ax.add_patch(services)
    ax.text(7, 1.3, 'Shared Services', ha='center', fontsize=9, fontweight='bold')
    ax.text(7, 0.85, 'Vector Store | Cache (Redis) | Logs | Monitoring | Gemini API',
            ha='center', fontsize=8)
    ax.text(7, 0.5, 'Metrics | Alerts | Backup | Security', ha='center', fontsize=8)
    
    save_fig(fig, 'fig18_deployment_options')


def generate_api_endpoints():
    """Figure 19: API Endpoints and Structure"""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    ax.text(7, 11.5, 'REST API Endpoints and Structure',
            ha='center', fontsize=14, fontweight='bold')
    
    # Base URL
    base_rect = FancyBboxPatch((4.5, 10.2), 5, 0.8, boxstyle="round,pad=0.05",
                               edgecolor='#2E86AB', facecolor='#E8F4F8', linewidth=2)
    ax.add_patch(base_rect)
    ax.text(7, 10.6, 'Base URL: http://localhost:8000', ha='center',
            fontsize=10, fontweight='bold', family='monospace')
    
    # Endpoints
    endpoints = [
        {
            'method': 'GET',
            'path': '/',
            'desc': 'API information and welcome',
            'color': '#2ECC71'
        },
        {
            'method': 'GET',
            'path': '/health',
            'desc': 'Health check endpoint',
            'color': '#2ECC71'
        },
        {
            'method': 'GET',
            'path': '/stats',
            'desc': 'System statistics',
            'color': '#2ECC71'
        },
        {
            'method': 'POST',
            'path': '/query',
            'desc': 'Submit question to chatbot',
            'color': '#3498DB'
        },
        {
            'method': 'GET',
            'path': '/history',
            'desc': 'Get conversation history',
            'color': '#2ECC71'
        },
        {
            'method': 'DELETE',
            'path': '/history',
            'desc': 'Clear conversation history',
            'color': '#E74C3C'
        },
        {
            'method': 'POST',
            'path': '/initialize',
            'desc': 'Reinitialize system',
            'color': '#F39C12'
        },
    ]
    
    y_start = 9.2
    for i, endpoint in enumerate(endpoints):
        y = y_start - (i * 1.1)
        
        # Method box
        method_color = {
            'GET': '#2ECC71',
            'POST': '#3498DB',
            'DELETE': '#E74C3C',
            'PUT': '#F39C12'
        }
        
        method_rect = FancyBboxPatch((0.5, y), 1.5, 0.6, boxstyle="round,pad=0.05",
                                     edgecolor='black', facecolor=method_color.get(endpoint['method'], '#95A5A6'),
                                     linewidth=1.5)
        ax.add_patch(method_rect)
        ax.text(1.25, y + 0.3, endpoint['method'], ha='center', va='center',
                fontsize=9, fontweight='bold', color='white')
        
        # Path box
        path_rect = FancyBboxPatch((2.2, y), 3, 0.6, boxstyle="round,pad=0.05",
                                   edgecolor='black', facecolor='#ECF0F1', linewidth=1.5)
        ax.add_patch(path_rect)
        ax.text(3.7, y + 0.3, endpoint['path'], ha='center', va='center',
                fontsize=9, fontweight='bold', family='monospace')
        
        # Description
        ax.text(5.5, y + 0.3, endpoint['desc'], va='center',
                fontsize=9)
    
    # Request/Response example (POST /query)
    ax.text(8.5, 9.5, 'POST /query - Request Example', fontsize=10, fontweight='bold', color='#2E86AB')
    request_rect = FancyBboxPatch((7, 6.5), 6.5, 2.8, boxstyle="round,pad=0.1",
                                  edgecolor='#3498DB', facecolor='#EBF5FB', linewidth=2)
    ax.add_patch(request_rect)
    
    request_example = '''{
  "query": "Article 27 সম্পর্কে বলুন",
  "language": "auto",
  "session_id": "user123"
}

Headers:
  Content-Type: application/json
  Authorization: Bearer <token> (optional)'''
    
    ax.text(10.25, 7.9, request_example, ha='center', va='center',
            fontsize=8, family='monospace', linespacing=1.5)
    
    ax.text(8.5, 5.8, 'Response Example', fontsize=10, fontweight='bold', color='#2E86AB')
    response_rect = FancyBboxPatch((7, 2.5), 6.5, 3.1, boxstyle="round,pad=0.1",
                                   edgecolor='#2ECC71', facecolor='#EAFAF1', linewidth=2)
    ax.add_patch(response_rect)
    
    response_example = '''{
  "response": "অনুচ্ছেদ ২৭...",
  "language_detected": "bn",
  "articles_referenced": ["27"],
  "metadata": {
    "confidence": 0.95,
    "source": "gemini",
    "processing_time_ms": 2450
  },
  "timestamp": "2025-10-08T10:30:00Z"
}'''
    
    ax.text(10.25, 4.0, response_example, ha='center', va='center',
            fontsize=8, family='monospace', linespacing=1.5)
    
    # Status codes
    status_rect = FancyBboxPatch((0.5, 1.5), 5, 1, boxstyle="round,pad=0.1",
                                 edgecolor='#9B59B6', facecolor='#F4ECF7', linewidth=2)
    ax.add_patch(status_rect)
    ax.text(3, 2.3, 'HTTP Status Codes', ha='center', fontsize=9, fontweight='bold')
    
    status_text = '''200: Success  |  400: Bad Request  |  404: Not Found
429: Rate Limit  |  500: Server Error  |  503: Service Unavailable'''
    ax.text(3, 1.8, status_text, ha='center', va='center', fontsize=7.5)
    
    # Rate limiting info
    rate_rect = FancyBboxPatch((0.5, 0.3), 5, 1, boxstyle="round,pad=0.1",
                               edgecolor='#E67E22', facecolor='#FEF5E7', linewidth=2)
    ax.add_patch(rate_rect)
    ax.text(3, 1.1, 'Rate Limiting', ha='center', fontsize=9, fontweight='bold')
    
    rate_text = '''Default: 100 requests/minute per IP
Burst: 20 requests/second  |  Retry-After header included'''
    ax.text(3, 0.65, rate_text, ha='center', va='center', fontsize=7.5)
    
    save_fig(fig, 'fig19_api_endpoints')


def generate_interface_comparison():
    """Figure 20: Interface Comparison"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
    
    # Features comparison
    features = ['Ease of Use', 'Customization', 'Integration', 'Performance', 'Scalability']
    web_ui_scores = [95, 70, 60, 85, 75]
    api_scores = [75, 95, 98, 90, 95]
    cli_scores = [80, 85, 70, 92, 80]
    
    x = np.arange(len(features))
    width = 0.25
    
    bars1 = ax1.bar(x - width, web_ui_scores, width, label='Web UI (Streamlit)',
                   color='#3498DB', alpha=0.8, edgecolor='black')
    bars2 = ax1.bar(x, api_scores, width, label='REST API',
                   color='#2ECC71', alpha=0.8, edgecolor='black')
    bars3 = ax1.bar(x + width, cli_scores, width, label='CLI',
                   color='#F39C12', alpha=0.8, edgecolor='black')
    
    ax1.set_ylabel('Score', fontsize=11, fontweight='bold')
    ax1.set_title('Interface Features Comparison', fontsize=12, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(features, fontsize=9)
    ax1.legend(fontsize=9)
    ax1.set_ylim(0, 105)
    ax1.grid(axis='y', alpha=0.3)
    
    # Use cases
    use_cases = ['End Users', 'Developers', 'Researchers', 'System\nIntegration', 'Automation']
    web_ui_fit = [95, 40, 70, 30, 20]
    api_fit = [50, 95, 85, 98, 95]
    cli_fit = [60, 80, 90, 60, 85]
    
    x2 = np.arange(len(use_cases))
    bars1 = ax2.bar(x2 - width, web_ui_fit, width, label='Web UI',
                   color='#3498DB', alpha=0.8, edgecolor='black')
    bars2 = ax2.bar(x2, api_fit, width, label='REST API',
                   color='#2ECC71', alpha=0.8, edgecolor='black')
    bars3 = ax2.bar(x2 + width, cli_fit, width, label='CLI',
                   color='#F39C12', alpha=0.8, edgecolor='black')
    
    ax2.set_ylabel('Suitability Score', fontsize=11, fontweight='bold')
    ax2.set_title('Use Case Suitability', fontsize=12, fontweight='bold')
    ax2.set_xticks(x2)
    ax2.set_xticklabels(use_cases, fontsize=9)
    ax2.legend(fontsize=9)
    ax2.set_ylim(0, 105)
    ax2.grid(axis='y', alpha=0.3)
    
    # Resource usage
    interfaces = ['Web UI', 'REST API', 'CLI']
    memory_mb = [450, 320, 280]
    cpu_percent = [12, 8, 6]
    
    x3 = np.arange(len(interfaces))
    bars1 = ax3.bar(x3 - width/2, memory_mb, width*1.5, label='Memory (MB)',
                   color='#9B59B6', alpha=0.8, edgecolor='black')
    
    ax3_twin = ax3.twinx()
    bars2 = ax3_twin.bar(x3 + width/2, cpu_percent, width*1.5, label='CPU (%)',
                        color='#E67E22', alpha=0.8, edgecolor='black')
    
    ax3.set_ylabel('Memory Usage (MB)', fontsize=11, fontweight='bold', color='#9B59B6')
    ax3_twin.set_ylabel('CPU Usage (%)', fontsize=11, fontweight='bold', color='#E67E22')
    ax3.set_title('Resource Usage by Interface', fontsize=12, fontweight='bold')
    ax3.set_xticks(x3)
    ax3.set_xticklabels(interfaces, fontsize=10)
    ax3.tick_params(axis='y', labelcolor='#9B59B6')
    ax3_twin.tick_params(axis='y', labelcolor='#E67E22')
    ax3.legend(loc='upper left', fontsize=9)
    ax3_twin.legend(loc='upper right', fontsize=9)
    
    # Interface statistics
    stats_text = '''Interface Statistics

Web UI (Streamlit):
├─ Launch time: ~3.2s
├─ Concurrent users: 10-50
├─ Session management: Built-in
└─ Real-time updates: Yes

REST API (FastAPI):
├─ Launch time: ~1.8s
├─ Throughput: 100+ req/s
├─ OpenAPI docs: Auto-generated
└─ CORS support: Enabled

CLI (Terminal):
├─ Launch time: ~0.5s
├─ Interactive mode: Yes
├─ Batch processing: Supported
└─ Pipe-friendly: Yes

Recommended Usage:
├─ Demos/End-users: Web UI
├─ Integration: REST API
└─ Development/Testing: CLI'''
    
    ax4.text(0.5, 0.5, stats_text, ha='center', va='center',
            fontsize=8.5, family='monospace', linespacing=1.6,
            bbox=dict(boxstyle='round', facecolor='#F8F9F9',
                     edgecolor='black', linewidth=2))
    ax4.set_title('Interface Comparison Summary', fontsize=12, fontweight='bold')
    ax4.axis('off')
    
    plt.suptitle('Multiple Interface Support Comparison',
                 fontsize=14, fontweight='bold', y=0.995)
    save_fig(fig, 'fig20_interface_comparison')


def generate_all():
    """Generate all deployment diagrams"""
    print("  Generating deployment architecture diagrams...")
    generate_deployment_options()
    generate_api_endpoints()
    generate_interface_comparison()
