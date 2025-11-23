import json
import os
from typing import List, Dict, Any
import google.generativeai as genai
from pr_assistant.config import ConfigManager
from pr_assistant.codebase import CodebaseReader
from pr_assistant.prompts import SYSTEM_PROMPT
from pr_assistant.rate_limiter import RateLimiter

class Agent:
    def __init__(self):
        self.config = ConfigManager()
        self.api_key = self.config.get("gemini_api_key") or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key not found. Set GEMINI_API_KEY env var or run init.")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-flash-latest')
        self.codebase = CodebaseReader()
        self.rate_limiter = RateLimiter()

    def propose_prs(self, instruction: str, count: int = 1) -> List[Dict[str, Any]]:
        """
        Analyzes codebase and proposes PRs based on instruction.
        """
        if not self.rate_limiter.check_limit():
            raise RuntimeError("Rate limit exceeded. Please try again later.")

        context = self.codebase.get_file_structure()
        
        prompt = f"""
        {SYSTEM_PROMPT}
        
        Instruction: {instruction}
        Create {count} distinct PRs.
        
        Codebase Structure:
        {context}
        """

        response = self.model.generate_content(prompt)
        
        content = response.text
        # Gemini might wrap JSON in markdown blocks
        content = content.replace("```json", "").replace("```", "").strip()
        
        try:
            data = json.loads(content)
            return data.get("prs", [])
        except json.JSONDecodeError:
            # Fallback or retry logic could go here
            return []
