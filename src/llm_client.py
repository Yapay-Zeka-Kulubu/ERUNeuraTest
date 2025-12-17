# Groq LLM Client for test generation
import re
from typing import Optional
from groq import Groq
from .config import GROQ_API_KEY, GROQ_MODEL, GENERATION_CONFIG


class LLMClient:
    """Client for interacting with Groq API for test generation."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or GROQ_API_KEY
        self.model = model or GROQ_MODEL
        self.client = Groq(api_key=self.api_key)
    
    def generate_tests(self, code: str, prompt_template: Optional[str] = None) -> str:
        """Generate unit tests for the given code."""
        if prompt_template is None:
            prompt_template = self._default_prompt()
        
        prompt = prompt_template.format(code=code)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert Python developer specializing in writing comprehensive unit tests. Generate clean, executable pytest test cases."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=GENERATION_CONFIG["temperature"],
            max_tokens=GENERATION_CONFIG["max_tokens"],
            top_p=GENERATION_CONFIG["top_p"],
        )
        
        return response.choices[0].message.content
    
    def _default_prompt(self) -> str:
        return """Generate comprehensive unit tests for the following Python code.

Requirements:
1. Use pytest framework
2. Cover edge cases and boundary conditions
3. Include both positive and negative test cases
4. Make tests self-contained and executable

Code:
```python
{code}
```

Generate the test code only, no explanations."""

    def extract_code(self, response: str) -> str:
        """Extract Python code from LLM response."""
        # Try to extract code from markdown blocks
        patterns = [
            r'```python\n(.*?)```',
            r'```\n(.*?)```',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, response, re.DOTALL)
            if matches:
                return matches[0].strip()
        
        # Return as-is if no code blocks found
        return response.strip()
