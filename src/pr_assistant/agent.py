import json
import os
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from pr_assistant.config import ConfigManager
from pr_assistant.codebase import CodebaseReader
from pr_assistant.prompts import SYSTEM_PROMPT
from pr_assistant.rate_limiter import RateLimiter

class Agent:
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        self.config = config_manager or ConfigManager()
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
        content = content.replace("```json", "").replace("```", "").strip()
        
        try:
            data = json.loads(content)
            return data.get("prs", [])
        except json.JSONDecodeError:
            return []

    def review_pr(self, pr_details: dict, diff: str, persona: str = "Senior Software Engineer") -> str:
        """
        Reviews a PR based on the diff and persona.
        """
        if not self.rate_limiter.check_limit():
            raise RuntimeError("Rate limit exceeded. Please try again later.")

        prompt = f"""
        You are an expert code reviewer acting as a {persona}.
        
        PR Title: {pr_details['title']}
        PR Description: {pr_details['body']}
        
        Review the following code changes (diff) for:
        1. Bugs and potential runtime errors.
        2. Code style and best practices (Pythonic code, etc.).
        3. Performance improvements.
        4. Security vulnerabilities.
        5. Test coverage (if applicable).
        
        Be constructive, professional, and strict where necessary.
        
        IMPORTANT: Keep your review CONCISE.
        - Use bullet points.
        - Avoid long explanations unless critical.
        - Focus on high-impact issues.
        - Do not compliment the code excessively; just state the facts.
        
        Provide a summary of your findings and specific actionable feedback.
        
        Code Changes (Diff):
        {diff}
        """
        
        response = self.model.generate_content(prompt)
        return response.text
