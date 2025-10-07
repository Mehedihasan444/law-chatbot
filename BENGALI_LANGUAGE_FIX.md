# Bengali Language Response Fix

## Issue
When users ask questions in Bengali (বাংলা), the chatbot detects the language correctly but responds in English instead of Bengali.

## Root Cause
The language parameter was being detected in `chatbot.py` but was **not being passed** to the RAG pipeline's response generation methods. The LLM prompts and fallback response templates were not language-aware.

## Required Changes

### 1. Update `src/chatbot.py`
Pass the detected language to the RAG system:

```python
# Line ~207
rag_result = self.rag_system.query(processed_query, use_llm=use_llm, language=language)
```

### 2. Update `src/rag_pipeline.py` - Method Signatures

Add `language: str = 'en'` parameter to these methods:

```python
def query(self, question: str, use_llm: bool = False, language: str = 'en') -> Dict:

def generate_response_simple(self, query: str, context: str, language: str = 'en') -> str:

def generate_response_with_llm(self, query: str, context: str, language: str = 'en') -> str:

def _use_local_model_or_simple(self, query: str, context: str, language: str = 'en') -> str:

def _format_human_friendly_response(self, query: str, context: str, language: str = 'en') -> str:

def _format_emergency_powers_response(self, excerpts: List[str], language: str = 'en') -> str:

def _format_preamble_response(self, language: str = 'en') -> str:

def _format_article_response(self, article: str, excerpts: List[str], language: str = 'en') -> str:
```

### 3. Update Gemini Prompt for Bengali

In `generate_response_with_llm`, add language-specific prompt:

```python
def make_gemini_call():
    try:
        # Create language-specific prompt
        if language == 'bn':
            prompt = f"""আপনি বাংলাদেশের সংবিধান সম্পর্কে একজন বিশেষজ্ঞ সহায়ক। নিচের প্রসঙ্গ ব্যবহার করে প্রশ্নের উত্তর দিন।

প্রসঙ্গ:
{context[:8000]}

প্রশ্ন: {query}

অনুগ্রহ করে বাংলায় একটি বিস্তারিত, তথ্যবহুল উত্তর প্রদান করুন। সাংবিধানিক বিধানগুলি ব্যাখ্যা করুন এবং তাদের তাৎপর্য বর্ণনা করুন।"""
        else:
            prompt = self.config.USER_PROMPT_TEMPLATE.format(
                context=context[:8000],
                question=query
            )
        response = self.llm.invoke(prompt)
        # ... rest of code
```

### 4. Update Bengali Fallback Responses

Add Bengali versions for all fallback response methods:

```python
def generate_response_simple(self, query: str, context: str, language: str = 'en') -> str:
    if not context or "No relevant information found" in context:
        if language == 'bn':
            return (
                "দুঃখিত, আপনার প্রশ্নের বিষয়ে বাংলাদেশের সংবিধানে নির্দিষ্ট তথ্য পাওয়া যায়নি। "
                "অনুগ্রহ করে আপনার প্রশ্নটি অন্যভাবে করুন বা নির্দিষ্ট অনুচ্ছেদ বা বিধান সম্পর্কে জিজ্ঞাসা করুন।\n\n" +
                self.config.DISCLAIMER
            )
        return (
            "I couldn't find specific information about your query..."
        )
```

### 5. Update All Method Calls

Ensure all internal calls pass the language parameter:

```python
# In query() method
response = self.generate_response_with_llm(question, context, language=language)
response = self.generate_response_simple(question, context, language=language)

# In generate_response_with_llm()
return self._use_local_model_or_simple(query, context, language=language)

# In _use_local_model_or_simple()
return self.generate_response_simple(query, context, language=language)

# In _format_human_friendly_response()
return self._format_emergency_powers_response(excerpts, language=language)
return self._format_preamble_response(language=language)
return self._format_article_response(art, excerpts, language=language)
```

## Current Status

**⚠️ IMPORTANT**: The `src/rag_pipeline.py` file appears to have gotten corrupted during the editing process. 

### Next Steps:

1. **Restore the file from git**:
   ```bash
   cd "/d/projects/law chatbot"
   git checkout src/rag_pipeline.py
   ```

2. **Apply the changes carefully** using the complete replacement files I can provide, or

3. **Manual approach**: Follow this document and make the changes one method at a time.

## Testing

After implementing the fixes:

1. Ask a question in Bengali: "প্রধানমন্ত্রীর ভূমিকা কী?"
2. The response should be in Bengali
3. Ask in English: "What is the role of the Prime Minister?"
4. The response should be in English

## Expected Behavior

- Bengali query → Bengali response (বাংলা উত্তর)
- English query → English response
- Mixed language → Response in detected primary language
