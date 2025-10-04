"""
Network Connectivity Checker for Gemini API
Quick check before initializing LLM to detect network issues early
"""
import socket
import urllib.request
import time

def check_internet_connectivity(timeout=3):
    """Quick internet connectivity check"""
    try:
        # Try to resolve Google DNS
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
        return True
    except Exception:
        return False

def check_google_api_connectivity(timeout=5):
    """Check if Google APIs are reachable"""
    try:
        # Try to reach generativelanguage.googleapis.com
        response = urllib.request.urlopen(
            "https://generativelanguage.googleapis.com", 
            timeout=timeout
        )
        return response.getcode() in [200, 404, 403]  # Any response means connectivity
    except Exception as e:
        print(f"   API connectivity check failed: {type(e).__name__}")
        return False

def pre_check_connectivity():
    """Comprehensive connectivity pre-check"""
    print("🔍 Running connectivity pre-check...")
    
    # Basic internet check
    if not check_internet_connectivity():
        print("❌ No internet connectivity detected")
        return False
    
    print("✅ Basic internet connectivity OK")
    
    # Google API specific check
    if not check_google_api_connectivity():
        print("⚠️  Google API endpoints may be unreachable")
        print("   This could cause timeouts with Gemini API")
        return False
    
    print("✅ Google API connectivity OK")
    return True

if __name__ == "__main__":
    print("🌐 Network Connectivity Check")
    print("=" * 30)
    
    start_time = time.time()
    is_connected = pre_check_connectivity()
    check_time = time.time() - start_time
    
    print(f"\n📊 Results:")
    print(f"   Connected: {is_connected}")
    print(f"   Check time: {check_time:.2f} seconds")
    
    if is_connected:
        print("   💡 Gemini API should work normally")
    else:
        print("   💡 Recommend using local model fallback")