"""
Test Gemini API with correct model name
"""
from config.config import Config
import google.generativeai as genai

config = Config()
print('API Key:', config.GEMINI_API_KEY[:20] + '...')
print('Model:', config.LLM_MODEL)
print()

genai.configure(api_key=config.GEMINI_API_KEY)

# List available models
print('Available Gemini models:')
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f'  - {model.name}')

# Test the model
print()
print('Testing model:', config.LLM_MODEL)
try:
    model = genai.GenerativeModel(config.LLM_MODEL)
    response = model.generate_content("Say 'Hello, I am working!'")
    print('Response:', response.text)
    print('SUCCESS!')
except Exception as e:
    print('ERROR:', str(e))
