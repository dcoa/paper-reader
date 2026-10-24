import io
import logging

from conftest import make_pdf
from routes import api
from services.llm_client import LLMError

PAPER = make_pdf('Attention Is All You Need', 'We propose a new network architecture, the Transformer.')
# Different file, same paper: only the text after the title changes
SAME_PAPER_OTHER_FILE = make_pdf('Attention Is All You Need', 'Camera ready version of the paper.')


def upload(client, content=PAPER, filename='paper.pdf'):
    return client.post('/api/upload', data={'file': (io.BytesIO(content), filename)},
                       content_type='multipart/form-data')


def test_upload_without_file(client):
    response = client.post('/api/upload', data={}, content_type='multipart/form-data')
    assert response.status_code == 400
    assert response.get_json()['error'] == 'No file uploaded'


def test_upload_with_empty_filename(client):
    assert upload(client, filename='').status_code == 400


def test_upload_rejects_non_pdf_files(client):
    response = upload(client, content=b'plain text', filename='notes.txt')
    assert response.status_code == 400
    assert response.get_json()['error'] == 'Only PDF files are supported'


def test_upload_processes_and_stores_the_paper(client):
    response = upload(client)

    assert response.status_code == 200
    body = response.get_json()
    assert body['metadata']['title'] == 'Attention Is All You Need'
    assert body['num_chunks'] == 1
    assert api.vector_store.find_by_hash(body['metadata']['file_hash']) is not None


def test_uploading_the_same_file_twice_is_rejected(client):
    upload(client)
    total_before = api.vector_store.get_stats()['total_documents']

    response = upload(client, filename='copy.pdf')

    assert response.status_code == 409
    body = response.get_json()
    assert body['duplicate'] is True
    assert body['filename'] == 'copy.pdf'
    assert body['metadata']['title'] == 'Attention Is All You Need'
    assert body['metadata']['authors'] == ['Ashish Vaswani', 'Noam Shazeer']
    assert body['num_chunks'] == 1
    assert api.vector_store.get_stats()['total_documents'] == total_before


def test_same_file_is_detected_before_calling_the_llm(client, llms):
    upload(client)
    upload(client)
    assert len(llms['metadata'].calls) == 1


def test_same_paper_from_another_file_is_rejected(client):
    upload(client)

    response = upload(client, content=SAME_PAPER_OTHER_FILE, filename='camera-ready.pdf')

    assert response.status_code == 409
    assert response.get_json()['duplicate'] is True


def test_duplicate_becomes_the_current_paper_for_summaries(client):
    upload(client)
    api.vector_store.last_processed_metadata = None  # as after a backend restart

    assert upload(client).status_code == 409
    assert client.post('/api/summarize').status_code == 200


def test_upload_error_is_logged_but_not_shown(client, monkeypatch, caplog):
    def fail(*args, **kwargs):
        raise RuntimeError('secret provider details')
    monkeypatch.setattr(api.embedder, 'embed_text', fail)

    with caplog.at_level(logging.ERROR):
        response = upload(client)

    assert response.status_code == 500
    assert response.get_json() == {'error': 'The PDF could not be processed. Please try again later.'}
    assert 'secret provider details' in caplog.text


def test_ask_requires_a_question(client):
    assert client.post('/api/ask', json={}).status_code == 400


def test_ask_returns_the_answer_and_sources(client):
    upload(client)

    response = client.post('/api/ask', json={'question': 'What does the paper propose?'})

    assert response.status_code == 200
    body = response.get_json()
    assert body['answer'] == 'The paper proposes the Transformer.'
    assert body['question'] == 'What does the paper propose?'
    assert body['sources'][0]['metadata']['title'] == 'Attention Is All You Need'


def test_ask_hides_llm_errors(client, llms):
    upload(client)
    llms['qa'].reply = LLMError('Authentication Fails, Your api key: ****7d3c is invalid')

    response = client.post('/api/ask', json={'question': 'Q?'})

    assert response.status_code == 500
    assert response.get_json() == {'error': 'The question could not be answered. Please try again later.'}


def test_summarize_without_a_paper(client):
    response = client.post('/api/summarize')
    assert response.status_code == 400
    assert response.get_json()['error'] == 'No paper selected. Please upload a PDF first.'


def test_summarize_after_restart_asks_for_upload(client):
    upload(client)
    api.vector_store.last_processed_metadata = None

    assert client.post('/api/summarize').status_code == 400


def test_summarize_the_uploaded_paper(client, llms):
    upload(client)

    response = client.post('/api/summarize')

    assert response.status_code == 200
    body = response.get_json()
    assert body['summary'] == 'A short summary.'
    assert body['recommendations'] == ['Paper A', 'Paper B']
    assert body['metadata']['title'] == 'Attention Is All You Need'


def test_summarize_hides_llm_errors(client, llms):
    upload(client)
    llms['summary'].reply = LLMError('DeepSeek API returned 401')

    response = client.post('/api/summarize')

    assert response.status_code == 500
    assert response.get_json() == {'error': 'The summary could not be generated. Please try again later.'}


def test_stats(client):
    upload(client)
    assert client.get('/api/stats').get_json()['total_documents'] == 1


def test_clear_empties_the_knowledge_base(client):
    upload(client)

    assert client.post('/api/clear').status_code == 200
    assert client.get('/api/stats').get_json()['total_documents'] == 0
    assert client.post('/api/summarize').status_code == 400
