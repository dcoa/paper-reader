from types import SimpleNamespace

import openai
import pytest

from services.llm_client import LLMClient, LLMError, parse_json_response


@pytest.mark.parametrize('text', [
    '{"title": "A"}',
    '```json\n{"title": "A"}\n```',
    '```\n{"title": "A"}\n```',
    'Sure! Here is the JSON:\n{"title": "A"}\nLet me know if you need more.',
])
def test_parse_json_response_accepts_common_model_outputs(text):
    assert parse_json_response(text) == {'title': 'A'}


@pytest.mark.parametrize('text', ['no json here', '{"title": ', ''])
def test_parse_json_response_rejects_invalid_json(text):
    with pytest.raises(LLMError):
        parse_json_response(text)


class FakeCompletions:
    def __init__(self, content=None, error=None):
        self.content = content
        self.error = error
        self.kwargs = None

    def create(self, **kwargs):
        self.kwargs = kwargs
        if self.error:
            raise self.error
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=self.content))])


def client_with(completions):
    llm = LLMClient('qa')
    llm.client = SimpleNamespace(chat=SimpleNamespace(completions=completions))
    return llm


def test_chat_returns_the_message_content():
    completions = FakeCompletions(content='An answer')
    llm = client_with(completions)

    assert llm.chat([{'role': 'user', 'content': 'Q'}], max_tokens=100) == 'An answer'
    assert completions.kwargs['model'] == llm.model
    assert completions.kwargs['max_tokens'] == 100


def test_chat_leaves_out_max_tokens_when_not_given():
    completions = FakeCompletions(content='An answer')
    client_with(completions).chat([{'role': 'user', 'content': 'Q'}])

    assert 'max_tokens' not in completions.kwargs


def test_chat_wraps_provider_errors():
    llm = client_with(FakeCompletions(error=openai.OpenAIError('Authentication Fails')))

    with pytest.raises(LLMError, match='Authentication Fails'):
        llm.chat([{'role': 'user', 'content': 'Q'}])


def test_chat_rejects_empty_response():
    with pytest.raises(LLMError, match='empty response'):
        client_with(FakeCompletions(content='')).chat([{'role': 'user', 'content': 'Q'}])


def test_chat_json_parses_the_response():
    llm = client_with(FakeCompletions(content='```json\n{"summary": "S"}\n```'))
    assert llm.chat_json([{'role': 'user', 'content': 'Q'}]) == {'summary': 'S'}


def test_missing_api_key_uses_placeholder():
    # No key is configured in the tests, which is what local servers such as Ollama need
    assert LLMClient('summary').client.api_key == 'not-needed'
