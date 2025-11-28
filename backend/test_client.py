import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key found: {bool(api_key)}")

try:
    client = genai.Client(api_key=api_key)
    print("Client initialized successfully")
except Exception as e:
    print(f"Error initializing client: {e}")
