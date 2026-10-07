import requests
from typing import Dict, List
from .vector_store import VectorStore
from .embedder import Embedder
from config import Config

class RAGEngine:

    def __init__(self, vector_store: VectorStore = None):
        self.vector_store = vector_store if vector_store else VectorStore()
        self.embedder = Embedder()
        self.api_key = Config.DEEPSEEK_API_KEY
        self.api_base = Config.DEEPSEEK_API_BASE
    
    def answer_question(self, question: str, top_k: int = 3) -> Dict:
        query_vector = self.embedder.embed_query(question)

        search_results = self.vector_store.search(query_vector, top_k)

        if not search_results:
            return {
                'answer': 'Sorry, no relevant content found in the knowledge base. Please upload PDF papers first.',
                'sources': [],
                'question': question
            }

        context = self._build_context(search_results)

        answer = self._generate_answer(question, context)

        return {
            'answer': answer,
            'sources': search_results,
            'question': question
        }
    
    def _build_context(self, search_results: List[Dict]) -> str:
        context_parts = []
        for i, result in enumerate(search_results, 1):
            metadata = result['metadata']
            doc = result['document']
            context_parts.append(f"[Document Segment {i}]")
            context_parts.append(f"Title: {metadata.get('title', 'Unknown')}")
            context_parts.append(f"Content: {doc}")
            context_parts.append("")

        return "\n".join(context_parts)
    
    def _generate_answer(self, question: str, context: str) -> str:
        prompt = f"""You are a professional academic paper Q&A assistant. Please answer the user's question based on the provided paper content.

Relevant paper content:
{context}

User question: {question}

Please provide an accurate and detailed answer based on the above paper content. If the paper content does not contain relevant information, please state it clearly. Answer in English."""

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
                        {"role": "system", "content": "You are a professional academic paper Q&A assistant, skilled at understanding and explaining academic paper content. Always respond in English."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                answer = result['choices'][0]['message']['content']
                return answer
            else:
                return f"Error generating answer: API returned status code {response.status_code}"

        except Exception as e:
            return f"Error generating answer: {str(e)}"

