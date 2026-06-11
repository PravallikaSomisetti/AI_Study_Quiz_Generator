import os
import json
import time
from google import genai
from google.genai import types
from google.genai.errors import APIError  # Standard SDK exception tracking class

class QuizAPIHandler:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing from environment variables.")
        self.client = genai.Client(api_key=api_key)
        
        # Load System Prompt
        prompt_path = os.path.join("prompts", "system_prompt.txt")
        with open(prompt_path, "r") as f:
            self.system_instruction = f.read()
            
        # Load Rules
        rules_path = os.path.join("data", "quiz_rules.json")
        with open(rules_path, "r") as f:
            self.rules = json.load(f)

    def generate_quiz(self, content: str, count: int, difficulty: str) -> dict:
        diff_guideline = self.rules["difficulty_guidelines"].get(difficulty, "General recall.")
        
        user_prompt = f"""
        Target Difficulty Modifier: {diff_guideline}
        Exact Number of Questions to Output: {count}
        
        Source Study Material:
        \"\"\"
        {content}
        \"\"\"
        """
        
        # --- DEFENSIVE ERROR HANDLING & EXPONENTIAL BACKOFF RETRY STRATEGY ---
        max_retries = 3
        backoff_delay = 5  # 5-second baseline to clean transaction states
        
        for attempt in range(max_retries):
            try:
                # ROUTED TO FLASH-LITE FOR HIGH-LIMIT COGNITIVE TESTING
                response = self.client.models.generate_content(
                    model='gemini-2.5-flash-lite', # Upgraded from flash to flash-lite for 3x higher free quotas
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=self.system_instruction,
                        response_mime_type="application/json",
                        temperature=0.1,  
                    ),
                )
                return response.text
                
            except APIError as e:
                # Intercept temporary high demand spikes (503) or active rate limits (429)
                if e.code in [503, 429] and attempt < max_retries - 1:
                    # Scaling sequential wait windows
                    time.sleep(backoff_delay * (attempt + 1))  
                    continue
                else:
                    # Pass clear user feedback into app.py
                    raise RuntimeError(
                        f"The AI Engine is currently rate-limited or busy (Error {e.code}). "
                        "Please wait 10 seconds and click 'Compile & Synthesize Quiz' again."
                    )
            except Exception as e:
                # Generic fallback wrapper safety filter
                raise RuntimeError(f"An unexpected internal connection error occurred: {str(e)}")