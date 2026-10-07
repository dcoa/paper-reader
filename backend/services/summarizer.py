import requests
from typing import Dict
from config import Config

class Summarizer:
    
    def __init__(self):
        self.api_key = Config.DEEPSEEK_API_KEY
        self.api_base = Config.DEEPSEEK_API_BASE
    
    def generate_summary_and_recommendations(self, metadata: Dict, full_text: str, recomended_papers) -> Dict:
        """
        Generate paper summary and recommend related academic articles in APA 7 format
        """
        title = metadata.get('title', 'Unknown Title')
        authors = metadata.get('authors', [])
        keywords = metadata.get('keywords', [])
        abstract = metadata.get('abstract', '')
        
        
        prompt = f"""You are an academic research assistant. Based on the following paper information, please:

1. Generate a comprehensive summary of the paper (200-300 words)
2. Recommend 5 related academic articles that actually exist in the literature.

Paper Information:
- Title: {title}
- Authors: {', '.join(authors) if authors else 'Not specified'}
- Keywords: {', '.join(keywords) if keywords else 'Not specified'}
- Abstract: {abstract if abstract else 'Not available'}
- Content excerpt: {full_text[:3000]}

Paper Recommendations:
{ recomended_papers }

Requirements:
1. Summary should cover: research objectives, methodology, key findings, and significance
2. Must inclide articles for the "Paper Recommendations" list. Do not repete the same article
3. If less than 5 recomendations are found, complete the list with articles in the references of the document.
4. Format all recommendations in APA 7th edition style. Return only five recomendations.
5. Each recommendation should include: Author(s), Year, Title, Relevance, Journal/Publisher (if available), DOI (if available)

Please respond in the following JSON format:
{{
    "summary": "Your comprehensive summary here...",
    "recommendations": [
        "Author, A. A., & Author, B. B. (Year). Title of the article. Journal Name, Volume(Issue), pages. https://doi.org/xxxxx" (Relevance: 80%),
        "Author, C. C. (Year). Title of the book. Publisher. (Relevance: 5%)",
        "Author, C. C. (Year). Title. (Relevance: 65%)",
        ...
    ]
}}

Respond only with valid JSON, no additional text."""

        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {
                            "role": "system", 
                            "content": "You are an expert academic research assistant with deep knowledge of academic literature across various fields. You provide accurate summaries and recommend real, published academic papers in proper APA 7 format."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 3000
                },
                timeout=90
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
                
                import json
                parsed_result = json.loads(content)
                
                return {
                    'summary': parsed_result.get('summary', 'Summary generation failed'),
                    'recommendations': parsed_result.get('recommendations', []),
                    'metadata': metadata
                }
            else:
                return self._get_default_response(metadata)
                
        except Exception as e:
            print(f"Summary generation failed: {str(e)}")
            return self._get_default_response(metadata)
    
    def _get_default_response(self, metadata: Dict) -> Dict:
        return {
            'summary': 'Unable to generate summary at this time. Please try again later.',
            'recommendations': [],
            'metadata': metadata
        }

