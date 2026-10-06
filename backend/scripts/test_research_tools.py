import asyncio
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import settings
from app.tools.research.web_search import TavilyWebSearchTool
from app.tools.research.academic_search import ArxivAcademicSearchTool
from app.tools.research.base import ResearchToolConfigurationError, ResearchToolProviderError, ResearchToolValidationError

async def run_manual_test():
    load_dotenv()
    settings.TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    query = "Latest AI trends 2026"
    
    print("\n--- 📚 Testing ArXiv Academic Search ---")
    try:
        academic_tool = ArxivAcademicSearchTool()
        academic_results = await academic_tool.search(query=query, max_results=2)
        for res in academic_results:
            print(f"✅ Found: {res.title} | {res.url}")
    except (ResearchToolProviderError, ResearchToolValidationError) as e:
        print(f"❌ ArXiv Error: {e}")

    print("\n--- 🌐 Testing Tavily Web Search ---")
    if not settings.TAVILY_API_KEY:
        print("⚠ TAVILY_API_KEY not found in .env. Skipping web search test.")
    else:
        try:
            web_tool = TavilyWebSearchTool()
            web_results = await web_tool.search(query=query, max_results=2)
            for res in web_results:
                print(f"✅ Found: {res.title} | {res.url}")
        except (ResearchToolConfigurationError, ResearchToolProviderError, ResearchToolValidationError) as e:
            print(f"❌ Web Provider Error: {e}")

if __name__ == "__main__":
    asyncio.run(run_manual_test())