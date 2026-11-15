"""
Memory-Safe Model Configuration for Bangladesh Constitution Chatbot
This script helps determine the best local model based on available system resources.
"""
import psutil
import torch

def get_recommended_model():
    """Get recommended model based on system resources"""
    
    # Check available RAM
    memory = psutil.virtual_memory()
    available_gb = memory.available / (1024**3)
    total_gb = memory.total / (1024**3)
    
    print(f"💾 System Memory Analysis:")
    print(f"   Total RAM: {total_gb:.1f} GB")
    print(f"   Available RAM: {available_gb:.1f} GB")
    print(f"   Used RAM: {(total_gb - available_gb):.1f} GB ({((total_gb - available_gb) / total_gb * 100):.1f}%)")
    
    # Check GPU availability
    gpu_available = torch.cuda.is_available()
    if gpu_available:
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        print(f"🎮 GPU Available: {gpu_name} ({gpu_memory:.1f} GB)")
    else:
        print("🎮 GPU: Not available (CPU only)")
    
    # Model recommendations based on resources
    print(f"\n📊 Model Recommendations:")
    
    if available_gb >= 16 and gpu_available:
        recommended = "google/flan-t5-xl"
        reason = "High RAM + GPU - can handle largest model"
        print(f"✅ Recommended: {recommended}")
        print(f"   Reason: {reason}")
    elif available_gb >= 8:
        recommended = "google/flan-t5-large"
        reason = "Medium RAM - good balance of performance and memory usage"
        print(f"✅ Recommended: {recommended}")
        print(f"   Reason: {reason}")
    elif available_gb >= 4:
        recommended = "google/flan-t5-base"
        reason = "Limited RAM - most stable option"
        print(f"✅ Recommended: {recommended}")
        print(f"   Reason: {reason}")
    else:
        recommended = None
        reason = "Very low RAM - local models may not work reliably"
        print(f"⚠️  Warning: {reason}")
        print(f"💡 Suggestion: Use Gemini API only or upgrade system RAM")
    
    # Safety warnings
    print(f"\n⚠️  Safety Notes:")
    print(f"   • FLAN-T5-Base: ~2GB RAM, most stable")
    print(f"   • FLAN-T5-Large: ~6GB RAM, better quality")
    print(f"   • FLAN-T5-XL: ~11GB RAM, best quality but can crash")
    print(f"   • Always ensure 2-4GB RAM remains free for system")
    
    return recommended

def create_safe_env_file():
    """Create a .env file with safe model configuration"""
    recommended_model = get_recommended_model()
    
    if recommended_model:
        env_content = f"""# Auto-generated safe configuration
GEMINI_API_KEY=your_gemini_api_key_here
LLM_MODEL=gemini-1.5-flash
LLM_TYPE=gemini
CPU_LLM_MODEL={recommended_model}
"""
        
        print(f"\n📄 Suggested .env configuration:")
        print(env_content)
        
        try:
            with open('.env.safe', 'w') as f:
                f.write(env_content)
            print(f"✅ Safe configuration saved to .env.safe")
            print(f"💡 You can copy this to .env if needed")
        except Exception as e:
            print(f"❌ Could not save .env.safe: {e}")

if __name__ == "__main__":
    print("🔍 Bangladesh Constitution Chatbot - Memory Safety Check")
    print("=" * 60)
    create_safe_env_file()
    print("=" * 60)