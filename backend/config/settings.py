import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / '.env')

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    UPLOAD_FOLDER = BASE_DIR / 'src' / 'data' / 'uploads'
    VECTOR_DB_PATH = BASE_DIR / 'src' / 'data' / 'vector_db'
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
    
    DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
    SILICONFLOW_API_KEY = os.environ.get('SILICONFLOW_API_KEY', '')
    
    DEEPSEEK_API_BASE = 'https://api.deepseek.com/v1'
    SILICONFLOW_API_BASE = 'https://api.siliconflow.cn/v1'
    
    EMBEDDING_MODEL = 'BAAI/bge-large-en-v1.5'
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50
    TOP_K = 3
    
    @classmethod
    def init_directories(cls):
        cls.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
        cls.VECTOR_DB_PATH.mkdir(parents=True, exist_ok=True)

Config.init_directories()

