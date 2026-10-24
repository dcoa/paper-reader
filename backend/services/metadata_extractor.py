from typing import Dict
from .llm_client import LLMClient, LLMError

class MetadataExtractor:
    
    def __init__(self):
        self.llm = LLMClient('metadata')
    
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
            metadata = self.llm.chat_json(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
        except LLMError as e:
            print(f"Metadata extraction failed: {str(e)}")
            return self._get_default_metadata()

        if not isinstance(metadata, dict):
            print("Metadata extraction failed: model did not return a JSON object")
            return self._get_default_metadata()
        # Fill in any field the model left out
        return {**self._get_default_metadata(), **metadata}

    def _get_default_metadata(self) -> Dict:
        return {
            "title": "Unknown Title",
            "authors": [],
            "keywords": [],
            "abstract": "",
            "year": ""
        }

