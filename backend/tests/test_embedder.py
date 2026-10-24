import sys
from types import ModuleType, SimpleNamespace

import numpy as np
import pytest

from config import Config
from services.embedder import Embedder


class FakeEmbeddingsAPI:
    def __init__(self):
        self.calls = []

    def create(self, model, input):
        self.calls.append({'model': model, 'input': input})
        return SimpleNamespace(data=[SimpleNamespace(embedding=[float(len(text)), 1.0]) for text in input])


@pytest.fixture
def api_embedder(monkeypatch):
    monkeypatch.setattr(Config, 'EMBEDDING_PROVIDER', 'api')
    embedder = Embedder()
    embedder._client = SimpleNamespace(embeddings=FakeEmbeddingsAPI())
    return embedder


def test_api_provider_sends_model_and_text(api_embedder):
    vectors = api_embedder.embed_text(['first', 'second'])

    call = api_embedder._client.embeddings.calls[0]
    assert call == {'model': Config.EMBEDDING_MODEL, 'input': ['first', 'second']}
    assert vectors.shape == (2, 2)


def test_long_text_is_truncated_to_512_characters(api_embedder):
    api_embedder.embed_text('x' * 2000)
    assert api_embedder._client.embeddings.calls[0]['input'] == ['x' * 512]


def test_embed_query_returns_one_vector(api_embedder):
    assert api_embedder.embed_query('a question').shape == (2,)


def test_embed_documents_returns_one_vector_per_document(api_embedder):
    assert api_embedder.embed_documents(['a', 'bb', 'ccc']).shape == (3, 2)


def test_local_provider_uses_sentence_transformers(monkeypatch):
    loaded = []

    class FakeSentenceTransformer:
        def __init__(self, model):
            loaded.append(model)

        def encode(self, text):
            return np.ones((len(text), 3))

    fake_module = ModuleType('sentence_transformers')
    fake_module.SentenceTransformer = FakeSentenceTransformer
    monkeypatch.setitem(sys.modules, 'sentence_transformers', fake_module)
    monkeypatch.setattr(Config, 'EMBEDDING_PROVIDER', 'local')

    embedder = Embedder()
    vectors = embedder.embed_text(['a', 'b'])
    embedder.embed_text('c')

    assert vectors.shape == (2, 3)
    # The model is loaded once and reused
    assert loaded == [Config.EMBEDDING_MODEL]


def test_invalid_provider_raises(monkeypatch):
    monkeypatch.setattr(Config, 'EMBEDDING_PROVIDER', 'cloud')
    with pytest.raises(ValueError):
        Embedder()
