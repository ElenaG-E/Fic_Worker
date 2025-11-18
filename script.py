import sys
sys.path.append('.')
from google import genai

client = genai.Client(api_key='AIzaSyB17YH21i6C5HgjkVic7LLPkxmurRiIuaY')

# List available models
models = client.models.list()
for model in models:
    print(model.name)

# Then, use a valid model, e.g., 'gemini-1.5-flash-latest' which is available
response = client.models.generate_content(
    model='gemini-1.5-flash', contents='Explain how AI works in a few words'
)
print(response.text)
