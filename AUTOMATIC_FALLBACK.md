# Automatic Fallback Mechanism

## Overview

The Bangladesh Constitution Chatbot now features an **intelligent automatic fallback system** that seamlessly switches from Gemini API to a local LLM when the API becomes unavailable or fails.

## How It Works

### 1. **Primary Mode: Gemini API**
When the system starts, it attempts to use Google's Gemini API for high-quality responses:
- Fast response times (typically 5-10 seconds)
- Advanced natural language understanding
- Detailed, context-aware answers

### 2. **Automatic Failure Detection**
The system monitors for various failure scenarios:

#### Network/Connectivity Issues:
- Connection timeouts
- DNS resolution failures
- Network unavailability
- Socket errors

#### API-Related Issues:
- Invalid API keys
- Rate limit exceeded (429 errors)
- Service unavailable (503 errors)
- Quota exceeded
- Server errors (500 errors)

#### Timeout Protection:
- **10-second timeout** on all Gemini API calls
- Prevents indefinite hanging
- Automatic fallback if timeout exceeded

### 3. **Seamless Fallback to Local LLM**
When Gemini fails, the system automatically:
1. Detects the failure type
2. Initializes the local FLAN-T5 model (if not already loaded)
3. Switches all subsequent queries to the local model
4. Continues operation without user intervention

### 4. **Persistent Fallback State**
After the first failure:
- System marks Gemini as unavailable
- All future queries use local model directly
- No repeated attempts to contact Gemini (saves time)
- Reduces unnecessary network calls

## Key Features

### ✅ Zero Downtime
- No interruption to user queries
- Smooth transition between models
- Automatic recovery

### ✅ Intelligent Error Detection
Recognizes these error patterns:
```
- Connection errors: "failed to connect", "connection error"
- Timeout errors: "timeout", "deadline exceeded"
- Network errors: "nameresolutionerror", "getaddrinfo failed"
- Service errors: "503", "unavailable", "service unavailable"
- Rate limits: "429", "quota exceeded", "resource exhausted"
- Server errors: "500", "temporary failure"
```

### ✅ User-Friendly Feedback
Clear console messages inform users about:
- Which model is being used
- When fallback occurs
- Why fallback was triggered
- Processing status

### ✅ Performance Optimization
- **First query after fallback**: ~3-5 seconds (model initialization)
- **Subsequent queries**: ~0.2-0.5 seconds (model already loaded)
- **Persistent state**: No redundant Gemini retry attempts

## Example Scenarios

### Scenario 1: Network Outage
```
User: "What is Article 27?"
System: 🌐 Attempting Gemini API call...
System: ❌ Connection error: Network unavailable
System: 🔄 Automatically falling back to local model...
System: 🏠 Initializing local FLAN-T5 model...
System: ✅ Successfully switched to local model!
System: 🏠 Generating response with local model...
System: ✅ Local model response generated successfully
```

### Scenario 2: API Timeout
```
User: "Explain fundamental rights"
System: 🌐 Attempting Gemini API call...
System: ⏰ Gemini API call timed out (>10 seconds)
System: 🔄 Automatically falling back to local model...
System: 🏠 Using already-initialized local model...
System: ✅ Local model response generated successfully
```

### Scenario 3: Invalid API Key
```
User: "What does Article 55 say?"
System: 🌐 Attempting Gemini API call...
System: ❌ Gemini API error: Invalid API key
System: 🔄 Automatically falling back to local model...
System: 🏠 All subsequent queries will use local model
```

### Scenario 4: Persistent Fallback
```
User: "What is Article 27?" (First query)
System: [Fallback triggered, local model initialized]

User: "What are fundamental rights?" (Second query)
System: ⚠️ Gemini API previously failed, using local model...
System: 🏠 Using already-initialized local model...
System: ✅ Response ready in 0.3 seconds
```

## Configuration

### Timeout Settings
Located in `src/services/llm_service.py`:
```python
llm = ChatGoogleGenerativeAI(
    model=model_name,
    request_timeout=30,      # API request timeout
    max_retries=2,           # Retry attempts
    transport="rest",        # REST for better timeout control
)
```

Located in `src/rag_pipeline.py`:
```python
# Gemini call timeout wrapper
gemini_thread.join(timeout=10)  # 10-second maximum wait
```

### Fallback Behavior
The system maintains two state flags:
- `_gemini_failed`: Tracks if Gemini has failed
- `_fallback_attempted`: Prevents repeated fallback initialization

## Testing the Fallback

### Run Automated Tests
```bash
python test_auto_fallback.py
```

This comprehensive test suite includes:
1. **Normal Operation Test** - Verifies Gemini works when available
2. **Simulated API Failure** - Tests with invalid API key
3. **Network Timeout Handling** - Demonstrates timeout protection
4. **Persistent Fallback** - Verifies fallback state persistence

### Manual Testing

#### Test Invalid API Key:
```bash
# Temporarily set invalid key
export GEMINI_API_KEY="INVALID_KEY"
python cli.py
# Try some queries - should automatically fallback
```

#### Test Network Issues:
```bash
# Disconnect from internet, then:
python cli.py
# Queries should use local model
```

## Model Comparison

### Gemini API (Primary)
| Aspect | Details |
|--------|---------|
| **Quality** | ⭐⭐⭐⭐⭐ Excellent |
| **Speed** | 5-10 seconds per query |
| **Context** | Up to 8000 characters |
| **Requires** | Internet + API key |
| **Cost** | Free tier available |

### Local FLAN-T5 (Fallback)
| Aspect | Details |
|--------|---------|
| **Quality** | ⭐⭐⭐⭐ Very Good |
| **Speed** | 0.2-0.5 seconds per query |
| **Context** | ~400 tokens (limited) |
| **Requires** | ~2GB RAM, CPU only |
| **Cost** | Completely free |

## Troubleshooting

### Fallback Not Working?

1. **Check transformers installation:**
   ```bash
   pip install transformers torch
   ```

2. **Verify local model availability:**
   ```python
   from transformers import AutoModelForSeq2SeqLM
   model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base")
   ```

3. **Check system logs:**
   Look for messages like:
   - "✅ Successfully switched to local model!"
   - "❌ Local model not available"

### Forcing Local Model from Start

Edit `.env` file:
```bash
LLM_TYPE=local  # Instead of 'gemini'
```

### Re-enabling Gemini After Failure

Restart the application:
```bash
# CLI
python cli.py

# API
python api.py

# Streamlit
streamlit run src/streamlit_app.py
```

The fallback state resets on restart.

## Benefits

### For End Users
- ✅ **Reliability**: System never goes completely offline
- ✅ **Transparency**: Clear feedback about system state
- ✅ **Performance**: Fast responses even in fallback mode

### For Developers
- ✅ **Resilience**: Robust error handling
- ✅ **Flexibility**: Works in various network conditions
- ✅ **Maintainability**: Clear separation of concerns

### For Production
- ✅ **High Availability**: Continuous service
- ✅ **Cost Management**: Automatic fallback to free local model
- ✅ **User Experience**: No visible downtime

## Architecture

```
┌─────────────────┐
│  User Query     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  RAG Pipeline           │
│  (generate_response)    │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐      Success ✅
│  Try Gemini API         │─────────────────►  Return Response
│  (10s timeout)          │
└────────┬────────────────┘
         │
         │ Failure ❌
         │ (timeout/error)
         ▼
┌─────────────────────────┐
│  Detect Error Type      │
│  - Network error?       │
│  - Timeout?             │
│  - API error?           │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Initialize Local LLM   │
│  (if not already done)  │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Set Persistent Flag    │
│  (_gemini_failed=True)  │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐      Success ✅
│  Query Local Model      │─────────────────►  Return Response
└─────────────────────────┘
         │
         │ Failure ❌
         ▼
┌─────────────────────────┐
│  Simple Fallback        │
│  (Template-based)       │
└────────┬────────────────┘
         │
         ▼
    Return Response
```

## Code Implementation

### Key Methods

#### 1. `generate_response_with_llm()` (Main Entry Point)
```python
def generate_response_with_llm(self, query: str, context: str) -> str:
    """Generates response with automatic fallback"""
    - Checks if Gemini previously failed
    - Attempts Gemini call with timeout
    - Detects failures and triggers fallback
    - Returns response from available model
```

#### 2. `_is_gemini_fatal_error()` (Error Detection)
```python
def _is_gemini_fatal_error(self, error_msg: str) -> bool:
    """Determines if error should trigger fallback"""
    - Checks error message against known patterns
    - Returns True for network/API errors
```

#### 3. `_use_local_model_or_simple()` (Fallback Handler)
```python
def _use_local_model_or_simple(self, query: str, context: str) -> str:
    """Manages local model initialization and usage"""
    - Initializes local model if needed
    - Uses existing local model if available
    - Falls back to simple responses if all else fails
```

## Future Enhancements

Potential improvements:
- [ ] Automatic Gemini retry after cooldown period
- [ ] Model performance metrics tracking
- [ ] User preference for primary model
- [ ] Custom timeout configuration per user
- [ ] Health check endpoint for API status
- [ ] Graceful degradation levels (Gemini → Local → Simple → Cached)

## Related Files

- `src/rag_pipeline.py` - Main fallback logic
- `src/services/llm_service.py` - Model initialization
- `config/config.py` - Configuration settings
- `test_auto_fallback.py` - Comprehensive tests
- `.env` - Environment configuration

## Support

For issues or questions about the fallback mechanism:
1. Check the console output for detailed error messages
2. Review `test_auto_fallback.py` for working examples
3. Verify your environment configuration in `.env`
4. Test with `python test_auto_fallback.py`

---

**Last Updated**: 2025-01-03  
**Feature Status**: ✅ Production Ready
