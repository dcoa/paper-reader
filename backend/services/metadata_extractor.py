import json
import requests
from typing import Dict
from config import Config

class MetadataExtractor:
    
    def __init__(self):
        self.api_key = Config.SILICONFLOW_API_KEY or Config.DEEPSEEK_API_KEY
        self.api_base = Config.SILICONFLOW_API_BASE if Config.SILICONFLOW_API_KEY else Config.DEEPSEEK_API_BASE
    
    def extract_metadata(self, text: str) -> Dict:
        prompt = f"""Extract metadata information from the following paper text and return it in JSON format.

Paper text (first 2000 characters):
{text[:2000]}

Please extract the following information:
1. Paper title (title)
2. Author list (authors), as an array
3. Keyword list (keywords), as an array
4. Abstract (abstract)
5. Publication year (year)

Return only JSON format, no other explanatory text. Format as follows:
{{
    "title": "Paper Title",
    "authors": ["Author 1", "Author 2"],
    "keywords": ["Keyword 1", "Keyword 2"],
    "abstract": "Abstract content",
    "year": "2024"
}}"""

        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat" if "deepseek" in self.api_base else "Qwen/Qwen2.5-7B-Instruct",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']

                content = content.strip()
                if content.startswith('```json'):
                    content = content[7:]
                if content.startswith('```'):
                    content = content[3:]
                if content.endswith('```'):
                    content = content[:-3]
                content = content.strip()

                metadata = json.loads(content)
                return metadata
            else:
                return self._get_default_metadata()

        except Exception as e:
            print(f"Metadata extraction failed: {str(e)}")
            return self._get_default_metadata()

    def _get_default_metadata(self) -> Dict:
        return {
            "title": "Unknown Title",
            "authors": [],
            "keywords": [],
            "abstract": "",
            "year": ""
        }

