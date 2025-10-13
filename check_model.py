# check_models.py
import google.generativeai as genai
from decouple import config

try:
    # Make sure your .env file has GOOGLE_API_KEY defined
    api_key = config('GOOGLE_API_KEY')
    genai.configure(api_key=api_key)

    print("\n--- Finding Available Models ---\n")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
    print("\n------------------------------\n")

except Exception as e:
    print(f"An error occurred: {e}")