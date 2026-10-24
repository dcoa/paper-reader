import pytest

from conftest import FakeLLM, fake_embed_text
from services.llm_client import LLMError
from services.metadata_extractor import MetadataExtractor
from services.rag_engine import RAGEngine
from services.summarizer import Summarizer

METADATA = {'title': 'Attention Is All You Need', 'authors': ['Ashish Vaswani'],
            'keywords': ['transformer'], 'abstract': 'Attention based model.', 'year': '2017'}


def extractor_with(reply):
    extractor = MetadataExtractor()
    extractor.llm = FakeLLM(reply)
    return extractor


def test_metadata_extractor_returns_model_metadata():
    assert extractor_with(METADATA).extract_metadata('paper text') == METADATA


def test_metadata_extractor_fills_in_missing_fields():
    metadata = extractor_with({'title': 'Only a title'}).extract_metadata('paper text')

    assert metadata == {'title': 'Only a title', 'authors': [], 'keywords': [], 'abstract': '', 'year': ''}


def test_metadata_extractor_sends_the_start_of_the_text():
    extractor = extractor_with(METADATA)
    extractor.extract_metadata('A' * 1990 + 'B' * 100)

    prompt = extractor.llm.calls[0][0]['content']
    assert 'A' * 1990 + 'B' * 10 in prompt
    assert 'B' * 11 not in prompt


@pytest.mark.parametrize('reply', [LLMError('provider down'), ['not', 'an', 'object']])
def test_metadata_extractor_falls_back_to_default_metadata(reply):
    assert extractor_with(reply).extract_metadata('paper text')['title'] == 'Unknown Title'


def summarizer_with(reply):
    summarizer = Summarizer()
    summarizer.llm = FakeLLM(reply)
    return summarizer


def test_summarizer_returns_summary_and_recommendations():
    summarizer = summarizer_with({'summary': 'A summary.', 'recommendations': ['Paper A']})

    result = summarizer.generate_summary_and_recommendations(METADATA, 'full text', '- Paper A')

    assert result == {'summary': 'A summary.', 'recommendations': ['Paper A'], 'metadata': METADATA}
    prompt = summarizer.llm.calls[0][1]['content']
    assert 'Attention Is All You Need' in prompt
    assert '- Paper A' in prompt


def test_summarizer_handles_missing_fields_in_the_reply():
    result = summarizer_with({}).generate_summary_and_recommendations(METADATA, 'full text', '')
    assert result['recommendations'] == []


def test_summarizer_lets_llm_errors_through():
    with pytest.raises(LLMError):
        summarizer_with(LLMError('invalid key')).generate_summary_and_recommendations(METADATA, 'text', '')


def rag_engine_with(store, reply):
    engine = RAGEngine(vector_store=store)
    engine.embedder.embed_text = fake_embed_text
    engine.llm = FakeLLM(reply)
    return engine


def test_rag_engine_without_documents(store):
    engine = rag_engine_with(store, 'unused')

    result = engine.answer_question('What is attention?')

    assert result['answer'].startswith('Sorry, no relevant content found')
    assert result['sources'] == []
    assert engine.llm.calls == []


def test_rag_engine_answers_from_the_retrieved_chunks(store):
    chunks = ['Attention lets the model focus.', 'Transformers use self-attention.']
    store.add_documents(documents=chunks, vectors=fake_embed_text(chunks), metadata=METADATA)
    engine = rag_engine_with(store, 'Attention is a mechanism.')

    result = engine.answer_question('What is attention?', top_k=2)

    assert result['answer'] == 'Attention is a mechanism.'
    assert {source['document'] for source in result['sources']} == set(chunks)
    prompt = engine.llm.calls[0][1]['content']
    assert 'Title: Attention Is All You Need' in prompt
    assert 'What is attention?' in prompt


def test_rag_engine_lets_llm_errors_through(store):
    store.add_documents(documents=['chunk'], vectors=fake_embed_text(['chunk']), metadata=METADATA)
    with pytest.raises(LLMError):
        rag_engine_with(store, LLMError('timeout')).answer_question('Q?')
