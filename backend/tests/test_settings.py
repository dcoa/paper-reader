import importlib

import pytest

import config.settings

ENV_VARS = [
    'DEEPSEEK_API_KEY', 'SILICONFLOW_API_KEY', 'LLM_BASE_URL', 'LLM_API_KEY', 'LLM_MODEL', 'LLM_TIMEOUT',
    'EMBEDDING_PROVIDER', 'EMBEDDING_BASE_URL', 'EMBEDDING_API_KEY', 'EMBEDDING_MODEL',
] + [f'{task}_LLM_{key}' for task in ('SUMMARY', 'QA', 'METADATA') for key in ('BASE_URL', 'API_KEY', 'MODEL', 'TIMEOUT')]


@pytest.fixture
def load_config(monkeypatch):
    """
    Reloads the settings with only the given environment variables set.
    """
    def load(**env):
        for name in ENV_VARS:
            monkeypatch.delenv(name, raising=False)
        for name, value in env.items():
            monkeypatch.setenv(name, value)
        return importlib.reload(config.settings).Config

    yield load
    # Leave a clean module for the other tests
    for name in ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    importlib.reload(config.settings)


def test_old_env_uses_deepseek_and_siliconflow_for_metadata(load_config):
    Config = load_config(DEEPSEEK_API_KEY='ds-key', SILICONFLOW_API_KEY='sf-key')

    summary = Config.llm_settings('summary')
    assert (summary['base_url'], summary['model'], summary['api_key']) == \
        ('https://api.deepseek.com/v1', 'deepseek-chat', 'ds-key')

    metadata = Config.llm_settings('metadata')
    assert (metadata['base_url'], metadata['model'], metadata['api_key']) == \
        ('https://api.siliconflow.cn/v1', 'Qwen/Qwen2.5-7B-Instruct', 'sf-key')

    assert (Config.EMBEDDING_BASE_URL, Config.EMBEDDING_API_KEY) == ('https://api.siliconflow.cn/v1', 'sf-key')


def test_new_llm_settings_apply_to_every_task(load_config):
    Config = load_config(LLM_BASE_URL='https://api.openai.com/v1', LLM_API_KEY='oai-key',
                         LLM_MODEL='gpt-4o-mini', SILICONFLOW_API_KEY='sf-key')

    for task in ('summary', 'qa', 'metadata'):
        settings = Config.llm_settings(task)
        assert (settings['base_url'], settings['model'], settings['api_key']) == \
            ('https://api.openai.com/v1', 'gpt-4o-mini', 'oai-key')


def test_task_override_only_changes_that_task(load_config):
    Config = load_config(LLM_BASE_URL='http://localhost:11434/v1', LLM_MODEL='llama3.1',
                         SUMMARY_LLM_MODEL='qwen2.5:14b')

    assert Config.llm_settings('summary')['model'] == 'qwen2.5:14b'
    assert Config.llm_settings('summary')['base_url'] == 'http://localhost:11434/v1'
    assert Config.llm_settings('qa')['model'] == 'llama3.1'


def test_timeouts_default_per_task_and_can_be_overridden(load_config):
    Config = load_config()
    assert [Config.llm_settings(task)['timeout'] for task in ('summary', 'qa', 'metadata')] == [90, 60, 30]

    Config = load_config(LLM_TIMEOUT='45', QA_LLM_TIMEOUT='120')
    assert Config.llm_settings('summary')['timeout'] == 45
    assert Config.llm_settings('qa')['timeout'] == 120


def test_empty_api_key_when_nothing_is_configured(load_config):
    Config = load_config()
    assert Config.llm_settings('qa')['api_key'] == ''
    assert Config.EMBEDDING_PROVIDER == 'api'
    assert Config.EMBEDDING_MODEL == 'BAAI/bge-large-en-v1.5'


def test_unknown_task_raises(load_config):
    Config = load_config()
    with pytest.raises(ValueError):
        Config.llm_settings('translation')
