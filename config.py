#!/usr/bin/env python3
"""
科研加速Web应用配置文件
包含数据库、DeepSeek AI、文件上传等配置
"""
import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

# 基础配置
class Config:
    """Flask应用基础配置"""
    # 应用密钥
    SECRET_KEY = os.environ.get('DB_SECRET_KEY')
    
    # 调试模式
    DEBUG = True
    
    # 主机和端口
    HOST = '0.0.0.0'
    PORT = 5600

# 数据库配置 - SQLite
DATABASE_CONFIG = {
    'type': 'sqlite',
    'database': 'paper_reader.db',
    'timeout': 5.0,
    'check_same_thread': False
}

# DeepSeek AI配置
DEEPSEEK_CONFIG = {
    'api_key': os.environ.get('DEEPSEEK_KEY'),
    'base_url': 'https://api.deepseek.com',
    'model': 'deepseek-chat',
    'timeout': 30,
    'max_tokens': 4000,
    'temperature': 0.7
}

# 文件上传配置
UPLOAD_CONFIG = {
    'upload_folder': 'uploads',
    'max_file_size': 50 * 1024 * 1024,  # 50MB
    'allowed_extensions': {'pdf', 'doc', 'docx'},
    'allowed_mime_types': {
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }
}

# 会话配置
SESSION_CONFIG = {
    'permanent_session_lifetime': timedelta(days=7),  # 7天过期
    'session_cookie_name': 'paper_reader_session',
    'session_cookie_httponly': True,
    'session_cookie_secure': False,  # 开发环境为False
    'session_cookie_samesite': 'Lax'
}

# Token配置
TOKEN_CONFIG = {
    'token_expire_hours': 24 * 7,  # 7天过期
    'token_algorithm': 'simple',  # 简单token算法
    'token_prefix': 'PR_'
}

# CORS跨域配置 - 允许所有请求
CORS_CONFIG = {
    'origins': '*',  # 允许所有域名
    'allow_headers': ['Content-Type', 'Authorization', 'X-Requested-With', 'Accept', 'Origin', 'X-CSRF-Token'],  # 允许常用请求头
    'allow_methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'HEAD', 'PATCH'],  # 允许所有方法
    'allow_credentials': False,  # 当使用*时，需要设置为False
    'supports_credentials': False
}

# 分页配置
PAGINATION_CONFIG = {
    'default_page_size': 10,
    'max_page_size': 100,
    'page_size_options': [5, 10, 20, 50, 100]
}

# 日志配置
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'logs/app.log',
    'max_bytes': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5
}

# 缓存配置
CACHE_CONFIG = {
    'cache_type': 'simple',
    'cache_default_timeout': 300  # 5分钟
}

# API响应配置
API_CONFIG = {
    'default_language': 'zh-CN',
    'json_ensure_ascii': False,
    'json_sort_keys': False
}

# 安全配置
SECURITY_CONFIG = {
    'password_min_length': 6,
    'password_require_uppercase': False,
    'password_require_lowercase': False,
    'password_require_numbers': False,
    'password_require_symbols': False,
    'max_login_attempts': 5,
    'login_lockout_minutes': 15
}

def get_config():
    """获取配置类"""
    return Config

def get_database_config():
    """获取数据库配置"""
    return DATABASE_CONFIG