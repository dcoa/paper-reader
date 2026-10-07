import numpy as np
import requests
from typing import List, Union
from config import Config

class Embedder:
    
    def __init__(self):
        self.api_key = Config.SILICONFLOW_API_KEY
        self.api_base = Config.SILICONFLOW_API_BASE
        self.model = "BAAI/bge-large-en-v1.5"
    
    def embed_text(self, text: Union[str, List[str]]) -> np.ndarray:
        if isinstance(text, str):
            text = [text]

        max_length = 512
        text = [t[:max_length] if len(t) > max_length else t for t in text]

        try:
            response = requests.post(
                f"{self.api_base}/embeddings",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "input": text,
                    "encoding_format": "float"
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                embeddings = [item['embedding'] for item in result['data']]
                return np.array(embeddings)
            else:
                raise Exception(f"API Failed: {response.status_code}")

        except Exception as e:
            print(f"Embarrassed failed: {str(e)}")
            raise
    
    def embed_query(self, query: str) -> np.ndarray:
        embedding = self.embed_text(query)
        return embedding[0]
    
    def embed_documents(self, documents: List[str]) -> np.ndarray:
        batch_size = 1
        all_embeddings = []

        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            try:
                embeddings = self.embed_text(batch)
                all_embeddings.append(embeddings)
            except Exception as e:
                print(f"List {i//batch_size + 1} embarrassed failed: {str(e)}")
                raise

        return np.vstack(all_embeddings)

