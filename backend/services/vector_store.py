import numpy as np
import chromadb
from typing import List, Dict
from config import Config
import json
from pathlib import Path
import uuid

BASE_DIR = Path(__file__).resolve().parent.parent
mock_data_file = BASE_DIR / 'papers_emb.json'
loaded_mock_data = False
class VectorStore:
    
    def __init__(self, store_path: str = None):
        """
        Initializes the Chroma client and collection. If no store_path is given, it uses the default path.
        """
        # Initialize Chroma client
        self.client = chromadb.PersistentClient(path=store_path if store_path else Config.VECTOR_DB_PATH)
        self.collection_name = "document_collection"
        self.collection = self.client.get_or_create_collection(name=self.collection_name)
        self.last_processed_metadata = None

        if not mock_data_file.exists():
            print(f"{mock_data_file.name} not found, skipping preloaded papers. "
                  "Run `python build_dataset.py` to generate it.")
            return

        if not loaded_mock_data:

            # Load mock data into the vector store to test
            with open( mock_data_file, 'r', encoding='utf-8') as f:
                print("Loading mock data into vector store...")
                papers = json.load(f)
                if self.collection.count() > 0:
                    print("Vector store already has data, skipping mock data load.")
                    self.loaded_mock_data = True
                    return
                for paper in papers:
                    documents = []
                    vectors = []
                    year = paper['update_date'].split('-')[0] if 'update_date' in paper else 'N/A'
                    metadata = {
                            'paper_id': paper['paper_id'],
                            'title': paper['title'],
                            'authors': paper['authors'],
                            'abstract': paper['abstract'],
                            'year': year
                        }
                    for embedding in paper['chunks_with_embeddings']:
                        documents.append(embedding['text'])
                        vectors.append(embedding['embedding'])
                    self.add_documents(documents=documents, vectors=vectors, metadata=metadata)
                self.loaded_mock_data = True
                print("Mock data loaded.")

    def convert_metadata_to_strings(metadata: Dict) -> Dict:
        """
        Converts all values in the metadata dictionary to strings.
        """
        return {key: str(value) if not isinstance(value, str) else value for key, value in metadata.items()}


    def add_documents(self, documents: List[str], vectors , metadata: List[Dict]):
        """
        Adds documents to Chroma along with their metadata. Chroma will automatically handle vector storage.
        """        
        # Prepare the document IDs
        document_ids = [uuid.uuid4().hex for _ in range(len(documents))]

        metadata_parsed = metadata.copy()
        for key, value in metadata_parsed.items():
                if not isinstance(value, str):
                    metadata_parsed[key] = str(value)
        metadata_parsed = [metadata_parsed for _ in range(len(vectors))]

        # Add documents to the Chroma collection
        self.collection.add(
            ids=document_ids,
            embeddings=vectors,
            documents=documents,
            metadatas=metadata_parsed
        )

        self.last_processed_metadata = metadata
    
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Performs a search query to retrieve the most similar documents.
        """
        try:

            # Query the collection for the top_k most similar documents
            results = self.collection.query(
                query_embeddings= query,
                n_results=top_k
            )
            docs = results.get("documents", [[]])[0]
            metas = results.get("metadatas", [[]])[0]
            dists = results.get("distances", [[]])[0]

            formatted_results = []

            for i in range(min(top_k, len(docs))):
                formatted_results.append({
                    "document": docs[i],
                    "metadata": metas[i],
                    "score": float(dists[i])  # already a single float
                })

        except Exception as e:
            print(f"Search failed: {str(e)}")
            return []
        return formatted_results
    

    def get_stats(self) -> Dict:
        """
        Returns statistics about the Chroma collection.
        """
        return {
            'total_documents': self.collection.count(),
            'collection_name': self.collection_name
        }

    def clear(self):
        """
        Clears all data from the Chroma collection.
        """
        self.collection.delete(self.collection.get()['ids'])
    
    def get_latest_document(self) -> Dict:
        """
        Returns the last processed document of the most recently added document.
        """
        # Get the metadata of the last document added
        results = self.collection.get(
            where={ "title": self.last_processed_metadata['title'] },
        )
        documents = results.get("documents", [])
        if not documents:
            return None

            # Join all matching documents into a single string
        parsed_text = "\n\n".join(documents)
        return parsed_text, self.last_processed_metadata

    def get_recommended_papers(self, keywords_emb: Dict, top_k: int = 5) -> List[Dict]:
        """
        Returns recommended papers based on the given keywords.
        """

        results = self.collection.query(
            query_embeddings= keywords_emb,
            where={ "title": {"$nin": [self.last_processed_metadata['title']]} },
            n_results=top_k
        )
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [])[0]
        recommendations = []
        for i, metadata in enumerate(metadatas):
            metadata['score'] = distances[i]
            recommendations.append(metadata)
        print(recommendations)
        return recommendations
