import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / '.env')

# Keep local embedding models inside the project (instead of ~/.cache) so they are easy to delete
os.environ.setdefault('HF_HOME', str(BASE_DIR / 'cache' / 'huggingface'))

# Older .env files only have these two keys, they are used as fallbacks below
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
SILICONFLOW_API_KEY = os.environ.get('SILICONFLOW_API_KEY', '')
SILICONFLOW_API_BASE = 'https://api.siliconflow.cn/v1'

LLM_TASKS = ('summary', 'qa', 'metadata')
# Seconds to wait for each task, matching what the frontend waits for
DEFAULT_TIMEOUTS = {'summary': 90, 'qa': 60, 'metadata': 30}


def _env(name: str, default: str = '') -> str:
    return os.environ.get(name) or default


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    UPLOAD_FOLDER = BASE_DIR / 'src' / 'data' / 'uploads'
    VECTOR_DB_PATH = BASE_DIR / 'src' / 'data' / 'vector_db'
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024

    # Default chat model, any OpenAI-compatible API
    LLM_BASE_URL = _env('LLM_BASE_URL', 'https://api.deepseek.com/v1')
    LLM_API_KEY = _env('LLM_API_KEY', DEEPSEEK_API_KEY)
    LLM_MODEL = _env('LLM_MODEL', 'deepseek-chat')

    # Embeddings: "api" (OpenAI-compatible /embeddings endpoint) or "local" (sentence-transformers)
    EMBEDDING_PROVIDER = _env('EMBEDDING_PROVIDER', 'api').lower()
    EMBEDDING_BASE_URL = _env('EMBEDDING_BASE_URL', SILICONFLOW_API_BASE)
    EMBEDDING_API_KEY = _env('EMBEDDING_API_KEY', SILICONFLOW_API_KEY)
    EMBEDDING_MODEL = _env('EMBEDDING_MODEL', 'BAAI/bge-large-en-v1.5')

    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50
    TOP_K = 3

    @classmethod
    def llm_settings(cls, task: str) -> dict:
        """
        Returns base_url, api_key, model and timeout for a task (summary, qa or metadata).
        Each <TASK>_LLM_* variable overrides the default LLM_* one.
        """
        if task not in LLM_TASKS:
            raise ValueError(f'Unknown LLM task: {task}')

        defaults = {
            'base_url': cls.LLM_BASE_URL,
            'api_key': cls.LLM_API_KEY,
            'model': cls.LLM_MODEL,
            'timeout': _env('LLM_TIMEOUT', str(DEFAULT_TIMEOUTS[task])),
        }
        # Older setup: metadata extraction used SiliconFlow whenever its key was set
        legacy_env = not (os.environ.get('LLM_API_KEY') or os.environ.get('LLM_BASE_URL'))
        if task == 'metadata' and legacy_env and SILICONFLOW_API_KEY:
            defaults.update(base_url=SILICONFLOW_API_BASE, api_key=SILICONFLOW_API_KEY,
                            model='Qwen/Qwen2.5-7B-Instruct')

        prefix = task.upper()
        settings = {key: _env(f'{prefix}_LLM_{key.upper()}', value) for key, value in defaults.items()}
        settings['timeout'] = float(settings['timeout'])
        return settings

    @classmethod
    def init_directories(cls):
        cls.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
        cls.VECTOR_DB_PATH.mkdir(parents=True, exist_ok=True)

Config.init_directories()
