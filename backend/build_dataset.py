"""
Builds papers_emb.json, the preloaded papers used for recommendations.

Reads the first papers of the Kaggle Cornell University arXiv dataset, keeps the
ones with meaningful content and embeds each abstract with the embedding provider and
model configured in .env (EMBEDDING_PROVIDER, EMBEDDING_MODEL), the same ones the app uses.

Usage:
    python build_dataset.py                          # downloads the dataset with kagglehub
    python build_dataset.py --arxiv-path <file.json> # uses a local arxiv-metadata-oai-snapshot.json
"""
import argparse
import json
import os
from pathlib import Path
from typing import Dict, List

from tqdm import tqdm

BASE_DIR = Path(__file__).resolve().parent
# Keep downloads inside the project
CACHE_DIR = BASE_DIR.parent / 'cache'
os.environ.setdefault('KAGGLEHUB_CACHE', str(CACHE_DIR / 'kagglehub'))
os.environ.setdefault('HF_HOME', str(CACHE_DIR / 'huggingface'))
OUTPUT_FILE = BASE_DIR / 'papers_emb.json'
META_FILE = BASE_DIR / 'papers_emb.meta.json'
KAGGLE_DATASET = 'Cornell-University/arxiv'
ARXIV_FILENAME = 'arxiv-metadata-oai-snapshot.json'


def split_into_chunks(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    # Same chunking as services/pdf_processor.py
    words = text.split()
    return [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size - overlap)]


def download_arxiv() -> Path:
    import kagglehub

    path = Path(kagglehub.dataset_download(KAGGLE_DATASET))
    return path / ARXIV_FILENAME


def load_papers(json_path: Path, max_samples: int) -> List[Dict]:
    papers = []
    with open(json_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= max_samples:
                break
            try:
                paper = json.loads(line)
            except json.JSONDecodeError:
                continue

            paper_data = {
                'paper_id': paper.get('id', f'paper_{i}'),
                'title': paper.get('title', '').strip(),
                'abstract': paper.get('abstract', '').strip(),
                'authors': paper.get('authors', ''),
                'categories': paper.get('categories', ''),
                'doi': paper.get('doi', ''),
                'journal-ref': paper.get('journal-ref', ''),
                'update_date': paper.get('update_date', ''),
                'versions': len(paper.get('versions', []))
            }

            # Only keep papers with meaningful content
            if len(paper_data['title']) > 10 and len(paper_data['abstract']) > 50:
                papers.append(paper_data)
    return papers


def add_embeddings(papers: List[Dict], embedder) -> List[Dict]:
    for paper in tqdm(papers, desc='Embedding papers'):
        chunks = split_into_chunks(paper['abstract'])
        embeddings = embedder.embed_text(chunks)
        paper['chunks_with_embeddings'] = [
            {'text': chunk, 'embedding': embedding.tolist()}
            for chunk, embedding in zip(chunks, embeddings)
        ]
    return papers


def main():
    parser = argparse.ArgumentParser(description='Build papers_emb.json from the arXiv dataset.')
    parser.add_argument('--arxiv-path', type=Path,
                        help=f'Local {ARXIV_FILENAME}. If omitted, it is downloaded with kagglehub.')
    parser.add_argument('--max-samples', type=int, default=1000,
                        help='Number of arXiv records to read (default: 1000)')
    args = parser.parse_args()

    arxiv_path = args.arxiv_path or download_arxiv()
    papers = load_papers(arxiv_path, args.max_samples)
    print(f'Loaded {len(papers)} papers from {arxiv_path}')

    # Same embedder as the app, so the preloaded papers and uploaded papers are comparable
    from config import Config
    from services.embedder import Embedder

    print(f'Embedding with {Config.EMBEDDING_MODEL} ({Config.EMBEDDING_PROVIDER})')
    papers = add_embeddings(papers, Embedder())
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(papers, f, indent=4)
    with open(META_FILE, 'w', encoding='utf-8') as f:
        json.dump({'embedding_model': Config.EMBEDDING_MODEL}, f, indent=4)
    print(f'Saved {len(papers)} papers to {OUTPUT_FILE}')


if __name__ == '__main__':
    main()
