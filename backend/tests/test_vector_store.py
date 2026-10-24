import json

import pytest

import services.vector_store as vector_store_module
from config import Config
from conftest import fake_embed_text, fake_vector
from services.vector_store import VectorStore, collection_name_for

ATTENTION = {
    'title': 'Attention Is All You Need',
    'authors': ['Ashish Vaswani', 'Noam Shazeer'],
    'keywords': ['transformer'],
    'year': '2017',
    'file_hash': 'hash-attention',
}
BERT = {
    'title': 'BERT: Pre-training of Deep Bidirectional Transformers',
    'authors': ['Jacob Devlin'],
    'keywords': ['language model'],
    'year': '2018',
    'file_hash': 'hash-bert',
}


def add_paper(store, metadata, chunks):
    store.add_documents(documents=chunks, vectors=fake_embed_text(chunks), metadata=metadata)


def test_add_and_search(store):
    add_paper(store, ATTENTION, ['attention chunk one', 'attention chunk two'])

    results = store.search(fake_vector('attention chunk two'), top_k=1)

    assert results[0]['document'] == 'attention chunk two'
    assert results[0]['metadata']['title'] == ATTENTION['title']
    assert store.get_stats()['total_documents'] == 2


def test_find_by_hash(store):
    add_paper(store, ATTENTION, ['chunk one', 'chunk two'])

    found = store.find_by_hash('hash-attention')

    assert found['num_chunks'] == 2
    assert found['metadata']['title'] == ATTENTION['title']
    assert found['metadata']['authors'] == ATTENTION['authors']
    assert store.find_by_hash('unknown-hash') is None


@pytest.mark.parametrize('title', [
    'Attention Is All You Need',
    'attention is all you need.',
    '  ATTENTION   is all you NEED ',
])
def test_find_by_title_ignores_case_spacing_and_punctuation(store, title):
    add_paper(store, ATTENTION, ['chunk'])
    assert store.find_by_title(title)['metadata']['title'] == ATTENTION['title']


def test_find_by_title_without_match(store):
    add_paper(store, ATTENTION, ['chunk'])
    assert store.find_by_title('A Different Paper') is None
    assert store.find_by_title('') is None
    assert store.find_by_title(None) is None


def test_unknown_title_never_matches(store):
    add_paper(store, {**ATTENTION, 'title': 'Unknown Title'}, ['chunk'])
    assert store.find_by_title('Unknown Title') is None


def test_restore_metadata_turns_stored_strings_back_into_lists():
    restored = VectorStore._restore_metadata({
        'authors': "['Ashish Vaswani', 'Noam Shazeer']",
        'keywords': 'transformer, attention',
        'title': 'T',
    })
    assert restored['authors'] == ['Ashish Vaswani', 'Noam Shazeer']
    assert restored['keywords'] == ['transformer', 'attention']
    assert restored['title'] == 'T'


def test_restore_metadata_handles_missing_fields():
    restored = VectorStore._restore_metadata({'title': 'T'})
    assert restored['authors'] == []
    assert restored['keywords'] == []


def test_get_latest_document_joins_the_current_paper_chunks(store):
    add_paper(store, BERT, ['bert chunk'])
    add_paper(store, ATTENTION, ['attention one', 'attention two'])

    text, metadata = store.get_latest_document()

    assert set(text.split('\n\n')) == {'attention one', 'attention two'}
    assert metadata['title'] == ATTENTION['title']


def test_recommendations_leave_out_the_current_paper(store):
    add_paper(store, BERT, ['bert chunk'])
    add_paper(store, ATTENTION, ['attention chunk'])

    recommendations = store.get_recommended_papers(fake_vector('attention chunk'), top_k=5)

    assert [paper['title'] for paper in recommendations] == [BERT['title']]
    assert 'score' in recommendations[0]


def test_set_active_paper(store):
    add_paper(store, BERT, ['bert chunk'])
    add_paper(store, ATTENTION, ['attention chunk'])

    store.set_active_paper(store.find_by_title(BERT['title'])['metadata'])

    assert store.get_latest_document()[1]['title'] == BERT['title']


def test_clear_removes_everything_and_the_current_paper(store):
    add_paper(store, ATTENTION, ['chunk'])

    store.clear()

    assert store.get_stats()['total_documents'] == 0
    assert store.last_processed_metadata is None


def test_collection_name_for():
    assert collection_name_for('BAAI/bge-large-en-v1.5') == 'document_collection'
    assert collection_name_for('text-embedding-3-small') == 'papers_text_embedding_3_small'
    assert collection_name_for('nomic-embed-text:latest') == 'papers_nomic_embed_text_latest'


@pytest.fixture
def preloaded_papers(tmp_path, monkeypatch):
    """
    A small papers_emb.json in a temporary folder, used instead of the real one.
    """
    papers_file = tmp_path / 'papers_emb.json'
    meta_file = tmp_path / 'papers_emb.meta.json'
    papers = [{
        'paper_id': '0704.0001',
        'title': 'Calculation of prompt diphoton production',
        'authors': 'C. Balazs, E. Berger',
        'abstract': 'A fully differential calculation.',
        'update_date': '2008-11-13',
        'chunks_with_embeddings': [{'text': 'A fully differential calculation.',
                                    'embedding': fake_vector('A fully differential calculation.')}],
    }]
    papers_file.write_text(json.dumps(papers))
    monkeypatch.setattr(vector_store_module, 'mock_data_file', papers_file)
    monkeypatch.setattr(vector_store_module, 'mock_data_meta_file', meta_file)
    return meta_file


def test_preload_without_meta_file_assumes_default_model(tmp_path, preloaded_papers):
    store = VectorStore(store_path=str(tmp_path / 'db'))

    assert store.get_stats()['total_documents'] == 1
    paper = store.find_by_title('Calculation of prompt diphoton production')
    assert paper['metadata']['year'] == '2008'
    # Preloaded papers are not the current paper
    assert store.last_processed_metadata is None


def test_preload_when_the_model_matches(tmp_path, preloaded_papers):
    preloaded_papers.write_text(json.dumps({'embedding_model': Config.EMBEDDING_MODEL}))
    store = VectorStore(store_path=str(tmp_path / 'db'))
    assert store.get_stats()['total_documents'] == 1


def test_preload_is_skipped_when_the_model_differs(tmp_path, preloaded_papers, capsys):
    preloaded_papers.write_text(json.dumps({'embedding_model': 'another-model'}))

    store = VectorStore(store_path=str(tmp_path / 'db'))

    assert store.get_stats()['total_documents'] == 0
    assert 'skipping preloaded papers' in capsys.readouterr().out
