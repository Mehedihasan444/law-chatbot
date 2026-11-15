# Automatic Fallback Mechanism

## Overview

The Bangladesh Constitution Chatbot features an **intelligent automatic fallback system** that switches from the Gemini API to a local LLM when the API becomes unavailable or fails. It distinguishes two kinds of failures:

- **Persistent failures** (network/DNS/timeout/auth): switch to the local model for the rest of the session.
- **Transient failures** (rate limit / quota / temporary outage): fall back for that one query, back off briefly, then automatically retry Gemini — no restart needed.

## How It Works

### 1. Primary Mode: Gemini API
When the system starts, it attempts to use Google's Gemini API for high-quality responses:
- Fast response times (typically 5-10 seconds)
- Advanced natural language understanding
- Detailed, context-aware answers

### 2. Automatic Failure Detection
The system monitors for various failure scenarios.

**Persistent failures** (won't recover on their own):
- Connection failures, DNS resolution failures, socket errors
- Timeouts (Gemini does not respond within the call window)
- Invalid API key / permission denied (403/401)

**Transient failures** (clear over time):
- Rate limit exceeded (HTTP 429 / "too many requests")
- Quota exceeded / "resource exhausted"
- Service unavailable (503) / temporary server errors (500)

#### Timeout Protection
- A **60-second** hard timeout wraps every Gemini call (run in a background thread)
- Prevents indefinite hanging
- A timeout counts as a persistent failure (avoids waiting 60s on every query)

### 3. Fallback to Local LLM
When Gemini fails, the system automatically:
1. Classifies the error as persistent or transient
2. Initializes the local FLAN-T5 model (if not already loaded)
3. Returns a response from the fallback model for the current query
4. Continues operation without user intervention

### 4. Persistent vs. Transient State

**Persistent failures** set `_gemini_failed = True` for the session:
- All subsequent queries use the local model directly (no repeated 60s waits)
- Gemini is retried only after restarting the application

**Transient failures** set a short cooldown (`_gemini_cooldown_until`):
- Subsequent queries skip Gemini during the cooldown (~60s) and use the fallback
- After the cooldown, Gemini is retried automatically
- A successful Gemini response clears the cooldown immediately
- No restart needed — Gemini resumes once the rate limit clears

## Key Features

### ✅ Zero Downtime
- No interruption to user queries
- Smooth transition between models
- Automatic recovery (immediate for transient failures)

### ✅ Intelligent Error Detection
Recognizes these error patterns:

```
# Persistent (switch to local for the session)
- Connection errors: "failed to connect", "connection error", "socket"
- Timeout errors: "timeout", "deadline exceeded", "connect timeout", "read timeout"
- Network errors:   "nameresolutionerror", "getaddrinfo failed", "network error"
- Auth errors:       "api key not valid", "permission denied", "403", "401"
- "max retries exceeded"

# Transient (fall back once, cool down, retry Gemini)
- Rate limits:      "429", "rate limit", "too many requests"
- Quota:            "quota exceeded", "resource exhausted"
- Temporary server: "503", "service unavailable", "unavailable", "500", "temporary failure", "retry"
```

### ✅ User-Friendly Feedback
Clear console messages inform users about:
- Which model is being used
- When fallback occurs and why
- Whether the failure is persistent (session) or transient (cooldown)

### ✅ Performance Optimization
- **First query after fallback**: ~3-5 seconds (model initialization)
- **Subsequent queries**: ~0.2-0.5 seconds (model already loaded)
- **Persistent failures**: no redundant Gemini retry attempts (saves time)
- **Transient failures**: only one failed Gemini attempt per cooldown window

## Example Scenarios

### Scenario 1: Network Outage (persistent)
```
User: "What is Article 27?"
System: 🌐 Attempting Gemini API call...
System: ❌ Connection error: Network unavailable
System: 🔄 Gemini API unavailable — switching to local model for subsequent queries
System: 🏠 Initializing local FLAN-T5 model...
System: ✅ Local model response generated successfully
# All further queries skip Gemini (persistent) until restart
```

### Scenario 2: API Timeout (persistent)
```
User: "Explain fundamental rights"
System: 🌐 Attempting Gemini API call...
System: ⏰ Gemini API call timed out (>60 seconds)
System: 🔄 Gemini API unavailable — switching to local model for subsequent queries
System: 🏠 Using already-initialized local model...
System: ✅ Local model response generated successfully
```

### Scenario 3: Invalid API Key (persistent)
```
User: "What does Article 55 say?"
System: 🌐 Attempting Gemini API call...
System: ❌ Gemini API error: API key not valid
System: 🔄 Gemini API unavailable — switching to local model for subsequent queries
System: 🏠 All subsequent queries will use local model
```

### Scenario 4: Rate Limit / Quota (transient)
```
User: "What is Article 27?"
System: 🌐 Attempting Gemini API call...
System: ❌ Gemini API error: 429 Resource has been exhausted
System: ⏳ Transient Gemini error (rate limit/quota) — backing off temporarily
System: 🏠 Generating response with local model...
System: ✅ Local model response generated successfully

User: "What are fundamental rights?" (within ~60s cooldown)
System: ⏳ Gemini in transient cooldown (rate limit) — using fallback temporarily
System: 🏠 Using already-initialized local model...

# After the cooldown, Gemini is retried automatically and resumes if the rate limit cleared
```

## Configuration

### Timeout Settings
Located in `src/services/llm_service.py`:
```python
llm = ChatGoogleGenerativeAI(
    model=model_name,
    request_timeout=60,      # API request timeout
    max_retries=2,           # Retry attempts
    transport="rest",        # REST for better timeout control
)
```

Located in `src/rag_pipeline.py`:
```python
# Gemini call timeout wrapper (background thread)
gemini_thread.join(timeout=60)  # 60-second maximum wait

# Transient-error cooldown (class constant on ConstitutionRAG)
_TRANSIENT_COOLDOWN_SECONDS = 60
```

### Fallback State Flags
The system maintains several state flags (on `ConstitutionRAG`):
- `_gemini_failed`: set `True` by **persistent** failures (stays for the session)
- `_gemini_cooldown_until`: set by **transient** failures (cleared after cooldown or on Gemini success)
- `_fallback_attempted`: prevents repeated local-model initialization
- `_fallback_happened`: per-query flag reflected in the API `fallback_used` field

## Testing the Fallback

### Run Automated Tests
```bash
python tests/test_auto_fallback.py
```

This test suite includes:
1. **Normal Operation Test** - Verifies Gemini works when available
2. **Simulated API Failure** - Tests with invalid API key
3. **Network Timeout Handling** - Demonstrates timeout protection
4. **Persistent Fallback** - Verifies fallback state persistence

### Manual Testing

#### Test Invalid API Key (persistent):
```bash
# Temporarily set invalid key
export GEMINI_API_KEY="INVALID_KEY"
python cli.py
# Queries should automatically fall back; subsequent queries stay on the local model
```

#### Test Network Issues (persistent):
```bash
# Disconnect from the internet, then:
python cli.py
# Queries should use the local model for the session
```

#### Test Rate Limit / Transient Behavior:
Triggering a real 429 requires exhausting quota. When a transient error occurs you should see:
```
⏳ Transient Gemini error (rate limit/quota) — backing off temporarily
```
and Gemini should resume automatically after the cooldown — without restarting.

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

3. **Check system logs** for messages like:
   - "✅ Local model response generated successfully"
   - "❌ Local model not available"

### Forcing Local Model from Start

Edit `.env` file:
```bash
LLM_TYPE=local  # Instead of 'gemini'
```

### Re-enabling Gemini After Failure

- **Persistent failure** (network/timeout/invalid key): restart the application:
  ```bash
  python cli.py            # CLI
  python api.py            # API
  streamlit run src/streamlit_app.py   # Web UI
  ```
  The persistent `_gemini_failed` flag resets on restart.
- **Transient failure** (rate limit/quota): no action needed — Gemini is retried
  automatically after the cooldown and resumes once the rate limit clears.

## Architecture

```
┌─────────────────┐
│  User Query     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐      Success ✅
│  Try Gemini API         │─────────────────►  Return Response
│  (60s timeout)          │
└────────┬────────────────┘
         │ Failure ❌
         ▼
┌─────────────────────────┐
│  Classify Error         │
│  Persistent or Transient│
└────────┬────────────────┘
         │
   ┌─────┴─────┐
   │           │
 Persistent  Transient
   │           │
   ▼           ▼
┌──────────────┐  ┌──────────────────────┐
│ _gemini_failed│  │ _gemini_cooldown_until│
│  = True       │  │  = now + 60s          │
└──────┬───────┘  └──────────┬────────────┘
       │                      │
       │  Initialize local LLM (if needed)
       └──────────┬───────────┘
                  ▼
┌─────────────────────────┐      Success ✅
│  Query Local Model      │─────────────────►  Return Response
└─────────────────────────┘
         │ Failure ❌
         ▼
┌─────────────────────────┐
│  Simple Fallback         │
│  (Template-based)        │
└────────┬────────────────┘
         │
         ▼
    Return Response

# Transient path: after cooldown expires (or on next Gemini success),
# Gemini is retried automatically — no restart required.
```

## Code Implementation

### Key Methods

#### 1. `generate_response_with_llm()` (Main Entry Point)
```python
def generate_response_with_llm(self, query: str, context: str, language: str = 'en') -> str:
    """Generates response with automatic fallback"""
    - Skips Gemini if already persistently failed, or during a transient cooldown
    - Attempts Gemini call with a 60s timeout
    - Classifies failures as persistent or transient
    - Returns a response from the available model
```

#### 2. `_is_gemini_fatal_error()` / `_is_gemini_transient_error()` (Error Detection)
```python
def _is_gemini_fatal_error(self, error_msg: str) -> bool:
    """True for network/DNS/timeout/auth errors → permanent switch to local"""

def _is_gemini_transient_error(self, error_msg: str) -> bool:
    """True for 429/quota/503/temporary errors → fall back once + cooldown"""
```

#### 3. `_use_local_model_or_simple()` (Fallback Handler)
```python
def _use_local_model_or_simple(self, query: str, context: str, language: str = 'en') -> str:
    """Manages local model initialization and usage"""
    - Initializes local model if needed
    - Uses existing local model if available
    - Falls back to simple responses if all else fails
```

## Future Enhancements

Potential improvements:
- [ ] Model performance metrics tracking
- [ ] User preference for primary model
- [ ] Configurable per-user timeout
- [ ] Health check endpoint for API status
- [ ] Graceful degradation levels (Gemini → Local → Simple → Cached)

## Related Files

- `src/rag_pipeline.py` - Main fallback logic (classification + cooldown)
- `src/services/llm_service.py` - Model initialization
- `config/config.py` - Configuration settings
- `tests/test_auto_fallback.py` - Comprehensive tests
- `.env` - Environment configuration

## Support

For issues or questions about the fallback mechanism:
1. Check the console output for detailed error messages
2. Review `tests/test_auto_fallback.py` for working examples
3. Verify your environment configuration in `.env`
4. Test with `python tests/test_auto_fallback.py`

---

**Feature Status**: ✅ Production Ready (transient-error cooldown implemented)
