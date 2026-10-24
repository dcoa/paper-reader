"""
Shared test setup. The tests never use the real .env, the real knowledge base or the network:
the LLM and embedding calls are replaced with fakes and Chroma runs in temporary folders.
"""
import hashlib
import os
import shutil
import tempfile
from pathlib import Path

import dotenv
import numpy as np
import pytest

# Must happen before the app is imported: keep the developer's .env (and API keys) out of the tests
dotenv.load_dotenv = lambda *args, **kwargs: False
os.environ['ANONYMIZED_TELEMETRY'] = 'False'

SESSION_DIR = Path(tempfile.mkdtemp(prefix='paper-app-tests-'))

from config import Config  # noqa: E402

Config.VECTOR_DB_PATH = SESSION_DIR / 'vector_db'
Config.UPLOAD_FOLDER = SESSION_DIR / 'uploads'
Config.init_directories()

import services.vector_store as vector_store_module  # noqa: E402

# Importing routes.api creates a VectorStore, so it must not load the real preloaded papers
vector_store_module.mock_data_file = SESSION_DIR / 'no_papers_emb.json'

from app import create_app  # noqa: E402
from routes import api  # noqa: E402
from services.llm_client import LLMError  # noqa: E402
from services.vector_store import VectorStore  # noqa: E402


def pytest_sessionfinish(session, exitstatus):
    shutil.rmtree(SESSION_DIR, ignore_errors=True)


def fake_vector(text):
    # Same text always gives the same vector, so search and duplicate checks are deterministic
    digest = hashlib.sha256(text.encode('utf-8')).digest()
    return [byte / 255 for byte in digest[:8]]


def fake_embed_text(text):
    if isinstance(text, str):
        text = [text]
    return np.array([fake_vector(t) for t in text])


class FakeLLM:
    """
    Stands in for LLMClient. `reply` is returned by chat/chat_json, or raised if it is an exception.
    """

    def __init__(self, reply=None):
        self.reply = reply
        self.calls = []

    def _respond(self, messages):
        self.calls.append(messages)
        if isinstance(self.reply, Exception):
            raise self.reply
        return self.reply

    def chat(self, messages, temperature=0.7, max_tokens=None):
        return self._respond(messages)

    def chat_json(self, messages, temperature=0.7, max_tokens=None):
        return self._respond(messages)


def _pdf_escape(text):
    return text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')


def make_pdf(*lines):
    """
    Builds a minimal one-page PDF with the given lines of text.
    """
    stream = 'BT /F1 12 Tf 72 720 Td 14 TL ' + ' '.join(f'({_pdf_escape(line)}) Tj T*' for line in lines) + ' ET'
    objects = [
        '<< /Type /Catalog /Pages 2 0 R >>',
        '<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
        '<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R '
        '/Resources << /Font << /F1 5 0 R >> >> >>',
        f'<< /Length {len(stream)} >>\nstream\n{stream}\nendstream',
        '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',
    ]
    pdf = '%PDF-1.4\n'
    offsets = []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf += f'{number} 0 obj\n{body}\nendobj\n'
    xref_offset = len(pdf)
    pdf += f'xref\n0 {len(objects) + 1}\n0000000000 65535 f \n'
    pdf += ''.join(f'{offset:010d} 00000 n \n' for offset in offsets)
    pdf += f'trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n'
    return pdf.encode('latin-1')


@pytest.fixture
def store(tmp_path):
    return VectorStore(store_path=str(tmp_path / 'vector_db'))


@pytest.fixture
def llms(monkeypatch):
    """
    Fake LLMs used by the API, one per task.
    """
    fakes = {
        'metadata': FakeLLM({
            'title': 'Attention Is All You Need',
            'authors': ['Ashish Vaswani', 'Noam Shazeer'],
            'keywords': ['transformer', 'attention'],
            'abstract': 'A new network architecture based on attention.',
            'year': '2017'
        }),
        'qa': FakeLLM('The paper proposes the Transformer.'),
        'summary': FakeLLM({'summary': 'A short summary.', 'recommendations': ['Paper A', 'Paper B']}),
    }
    monkeypatch.setattr(api.metadata_extractor, 'llm', fakes['metadata'])
    monkeypatch.setattr(api.rag_engine, 'llm', fakes['qa'])
    monkeypatch.setattr(api.summarizer, 'llm', fakes['summary'])
    return fakes


@pytest.fixture
def client(monkeypatch, store, llms):
    """
    Flask test client wired to a temporary knowledge base and fake LLMs and embeddings.
    """
    monkeypatch.setattr(api, 'vector_store', store)
    monkeypatch.setattr(api.rag_engine, 'vector_store', store)
    monkeypatch.setattr(api.embedder, 'embed_text', fake_embed_text)
    monkeypatch.setattr(api.rag_engine.embedder, 'embed_text', fake_embed_text)

    app = create_app()
    app.config['TESTING'] = True
    return app.test_client()

