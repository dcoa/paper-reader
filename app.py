#!/usr/bin/env python3
"""
科研加速Web应用主文件
Flask应用入口点
"""
import os
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime

# 导入配置
from config import (
    get_config, DATABASE_CONFIG, CORS_CONFIG, 
    LOGGING_CONFIG, UPLOAD_CONFIG
)

def create_app():
    """
    应用工厂函数
    创建并配置Flask应用实例
    """
    # 创建Flask应用
    app = Flask(__name__)
    
    # 加载配置
    config_class = get_config()
    app.config.from_object(config_class)
    
    # 设置上传文件夹
    app.config['UPLOAD_FOLDER'] = UPLOAD_CONFIG['upload_folder']
    app.config['MAX_CONTENT_LENGTH'] = UPLOAD_CONFIG['max_file_size']
    
    # 配置日志
    setup_logging(app)
    
    # 配置CORS跨域
    setup_cors(app)
    
    # 初始化数据库
    init_db(app)
    
    # 注册蓝图路由
    register_blueprints(app)
    
    # 注册错误处理器
    register_error_handlers(app)
    
    # 注册上下文处理器
    register_context_processors(app)
    
    # 应用启动日志
    app.logger.info('Flask应用创建成功')
    
    return app

def setup_cors(app):
    """
    配置CORS跨域
    """
    try:
        CORS(app, 
             origins=CORS_CONFIG['origins'],
             allow_headers=CORS_CONFIG['allow_headers'],
             methods=CORS_CONFIG['allow_methods'],
             allow_credentials=CORS_CONFIG['allow_credentials'])
        app.logger.info('CORS跨域配置成功')
    except Exception as e:
        app.logger.error(f'CORS配置失败: {e}')

def init_db(app):
    """
    初始化数据库连接
    """
    try:
        # 确保上传目录存在
        upload_dir = app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
            app.logger.info(f'创建上传目录: {upload_dir}')
        
        # 确保日志目录存在
        log_dir = os.path.dirname(LOGGING_CONFIG['file'])
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            app.logger.info(f'创建日志目录: {log_dir}')
        
        app.logger.info('数据库初始化成功')
    except Exception as e:
        app.logger.error(f'数据库初始化失败: {e}')

def register_blueprints(app):
    try:
        print("📦 Starting to import blueprints...")

        import importlib

        for module_name in [
            "routes.auth",
            "routes.papers",
            "routes.annotations",
            "routes.ai",
            "routes.publication_types",
            "routes.admin",
            "routes.analysis",
        ]:
            print(f"🔍 Importing {module_name} ...")
            importlib.import_module(module_name)
            print(f"✅ {module_name} imported")

        from routes.auth import auth_bp
        from routes.papers import papers_bp
        from routes.annotations import annotations_bp
        from routes.ai import ai_bp
        from routes.publication_types import publication_types_bp
        from routes.admin import admin_bp
        from routes.analysis import analysis_bp

        app.register_blueprint(auth_bp, url_prefix="/api/auth")
        app.register_blueprint(papers_bp, url_prefix="/api/papers")
        app.register_blueprint(annotations_bp, url_prefix="/api/annotations")
        app.register_blueprint(ai_bp, url_prefix="/api/ai")
        app.register_blueprint(publication_types_bp, url_prefix="/api/publication-types")
        app.register_blueprint(admin_bp, url_prefix="/api/admin")
        app.register_blueprint(analysis_bp, url_prefix="/api/papers")

        app.logger.info("路由注册成功")

    except Exception as e:
        import traceback
        traceback.print_exc()  # full traceback
        app.logger.error(f"路由注册失败: {e}")


def register_error_handlers(app):
    """
    注册错误处理器
    """
    @app.errorhandler(404)
    def not_found(error):
        """404错误处理"""
        return jsonify({
            'success': False,
            'error': '请求的资源不存在',
            'code': 404
        }), 404
    
    @app.errorhandler(400)
    def bad_request(error):
        """400错误处理"""
        return jsonify({
            'success': False,
            'error': '请求参数错误',
            'code': 400
        }), 400
    
    @app.errorhandler(500)
    def internal_error(error):
        """500错误处理"""
        app.logger.error(f'服务器内部错误: {error}')
        return jsonify({
            'success': False,
            'error': '服务器内部错误',
            'code': 500
        }), 500
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        """文件过大错误处理"""
        return jsonify({
            'success': False,
            'error': f'文件大小超过限制 ({UPLOAD_CONFIG["max_file_size"] // 1024 // 1024}MB)',
            'code': 413
        }), 413

def register_context_processors(app):
    """
    注册上下文处理器
    """
    @app.before_request
    def before_request():
        """请求前处理"""
        app.logger.info(f'{request.method} {request.path} - {request.remote_addr}')
    
    @app.after_request
    def after_request(response):
        """请求后处理"""
        # 设置响应头
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        return response

def setup_logging(app):
    """
    配置日志系统
    """
    if not app.debug:
        # 生产环境日志配置
        from logging.handlers import RotatingFileHandler
        
        # 确保日志目录存在
        log_dir = os.path.dirname(LOGGING_CONFIG['file'])
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 配置文件日志处理器
        file_handler = RotatingFileHandler(
            LOGGING_CONFIG['file'],
            maxBytes=LOGGING_CONFIG['max_bytes'],
            backupCount=LOGGING_CONFIG['backup_count']
        )
        file_handler.setFormatter(logging.Formatter(LOGGING_CONFIG['format']))
        file_handler.setLevel(getattr(logging, LOGGING_CONFIG['level']))
        
        app.logger.addHandler(file_handler)
        app.logger.setLevel(getattr(logging, LOGGING_CONFIG['level']))

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    """
    应用启动入口
    """
    print("🚀 启动科研加速Web应用...")
    from config import get_database_config, DEEPSEEK_CONFIG
    current_db_config = get_database_config()
    print(f"📊 数据库: {current_db_config['database']}")
    print(f"🔑 API Key: {DEEPSEEK_CONFIG['api_key'][:20]}...")
    print(f"📁 上传目录: {UPLOAD_CONFIG['upload_folder']}")
    print(f"🌐 访问地址: http://{app.config.get('HOST', '127.0.0.1')}:{app.config.get('PORT', 5000)}")
    print("=" * 50)
    
    # 导入配置
    from config import Config
    
    # 启动应用
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    ) 