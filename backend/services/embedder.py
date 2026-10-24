import numpy as np
import openai
from typing import List, Union
from config import Config

class Embedder:
    """
    Embeds text with any OpenAI-compatible /embeddings API (EMBEDDING_PROVIDER=api)
    or locally with sentence-transformers (EMBEDDING_PROVIDER=local).
    """

    def __init__(self):
        self.provider = Config.EMBEDDING_PROVIDER
        self.model = Config.EMBEDDING_MODEL
        if self.provider not in ('api', 'local'):
            raise ValueError(f"EMBEDDING_PROVIDER must be 'api' or 'local', got '{self.provider}'")

        self._client = None
        self._local_model = None

    def _embed_api(self, text: List[str]) -> List[List[float]]:
        if self._client is None:
            self._client = openai.OpenAI(
                base_url=Config.EMBEDDING_BASE_URL,
                # Local servers such as Ollama do not need a key, but the SDK requires one
                api_key=Config.EMBEDDING_API_KEY or 'not-needed',
                timeout=30,
                max_retries=0
            )
        response = self._client.embeddings.create(model=self.model, input=text)
        return [item.embedding for item in response.data]

    def _embed_local(self, text: List[str]) -> List[List[float]]:
        if self._local_model is None:
            # Optional dependency, only needed for local embeddings (requirements-local.txt)
            from sentence_transformers import SentenceTransformer
            self._local_model = SentenceTransformer(self.model)
        return self._local_model.encode(text).tolist()

    def embed_text(self, text: Union[str, List[str]]) -> np.ndarray:
        if isinstance(text, str):
            text = [text]

        max_length = 512
        text = [t[:max_length] if len(t) > max_length else t for t in text]

        try:
            if self.provider == 'local':
                embeddings = self._embed_local(text)
            else:
                embeddings = self._embed_api(text)
            return np.array(embeddings)

        except Exception as e:
            print(f"Embedding failed ({self.provider}, {self.model}): {str(e)}")
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
                print(f"Batch {i//batch_size + 1} embedding failed: {str(e)}")
                raise

        return np.vstack(all_embeddings)
