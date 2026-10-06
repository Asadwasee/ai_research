import asyncio
import os
import sys
from dotenv import load_dotenv

# Allow importing from the 'app' module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import settings
from app.services.llm.gemini import GeminiLLMProvider, LLMConfigurationError

async def test_real_connection():
    # Load environment variables from .env if present
    load_dotenv()
    
    # Reload settings API key explicitly for the script context
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found in environment.")
        print("Please add it to your .env file to run this manual test.")
        return

    # Update settings singleton dynamically for this standalone script
    settings.GEMINI_API_KEY = api_key

    print(f"🔌 Testing Gemini connectivity with model: {settings.GEMINI_MODEL}")
    
    try:
        provider = GeminiLLMProvider()
        prompt = "Reply with exactly: Gemini connection successful."
        print(f"✉️ Sending prompt: '{prompt}'")
        
        response = await provider.generate_text(prompt)
        print("\n✅ --- Response ---")
        print(response)
        print("------------------\n")
        
    except LLMConfigurationError as e:
        print(f"❌ Configuration Error: {e}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_real_connection())