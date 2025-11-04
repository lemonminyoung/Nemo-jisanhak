"""
Test script to list available Gemini models
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

if not GEMINI_API_KEY:
    print("ERROR: GEMINI_API_KEY not set")
    exit(1)

print(f"API Key: {GEMINI_API_KEY[:20]}...")
genai.configure(api_key=GEMINI_API_KEY)

print("\n" + "="*70)
print("Available Gemini Models")
print("="*70)

try:
    models = genai.list_models()
    for model in models:
        print(f"\nName: {model.name}")
        print(f"  Display Name: {model.display_name}")
        print(f"  Supported Methods: {model.supported_generation_methods}")
except Exception as e:
    print(f"Error listing models: {e}")
    print("\nTrying to use common model names...")

    # Try common model names
    test_models = [
        "gemini-pro",
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "models/gemini-pro",
        "models/gemini-1.5-pro",
        "models/gemini-1.5-flash",
    ]

    for model_name in test_models:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Say hello")
            print(f"[OK] {model_name}: {response.text[:50]}")
        except Exception as e:
            print(f"[FAIL] {model_name}: {str(e)[:80]}")
