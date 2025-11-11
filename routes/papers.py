#!/usr/bin/env python3
"""
文献管理路由
处理文献相关的API请求
"""
import os
from flask import Blueprint, request, send_file
from werkzeug.utils import secure_filename
from models.paper import (
    create_paper, get_papers_list, get_paper_by_id,
    search_papers, get_user_papers, get_paper_statistics
)
from utils.auth import token_required, get_user_from_request
from utils.response import success_response, error_response, validation_error_response, pagination_response
from config import UPLOAD_CONFIG

# 创建蓝图
papers_bp = Blueprint('papers', __name__)

def allowed_file(filename):
    """检查文件类型是否允许"""
    if '.' not in filename:
        return False
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in UPLOAD_CONFIG['allowed_extensions']

def save_uploaded_file(file, user_id):
    """保存上传的文件"""
    if not file or file.filename == '':
        return None, "未选择文件"
    
    if not allowed_file(file.filename):
        return None, f"不支持的文件类型，仅支持: {', '.join(UPLOAD_CONFIG['allowed_extensions'])}"
    
    # 生成安全的文件名
    filename = secure_filename(file.filename)
    
    # 生成唯一文件名（添加时间戳）
    import time
    timestamp = int(time.time())
    name, ext = os.path.splitext(filename)
    unique_filename = f"{user_id}_{timestamp}_{name}{ext}"
    
    # 确保上传目录存在
    upload_dir = UPLOAD_CONFIG['upload_folder']
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    # 保存文件
    file_path = os.path.join(upload_dir, unique_filename)
    file.save(file_path)
    
    # 获取文件大小
    file_size = os.path.getsize(file_path)
    
    return {
        'file_path': file_path,
        'filename': unique_filename,
        'original_filename': filename,
        'file_size': file_size,
        'file_type': ext[1:] if ext else ''
    }, None

@papers_bp.route('/upload', methods=['POST'])
@token_required
def upload_paper(current_user):
    """
    文献上传路由函数（对应API 2.1）
    POST /api/papers/upload
    """
    try:
        # 当前用户已通过装饰器传递
        # current_user = get_user_from_request()  # 不需要这一行了
        
        # 检查是否有文件上传
        if 'file' not in request.files:
            return validation_error_response("未找到上传文件")
        
        file = request.files['file']
        
        # 获取其他表单数据
        title = request.form.get('title')
        authors = request.form.get('authors')
        publication_type_id = request.form.get('publication_type_id')
        publication_name = request.form.get('publication_name')
        year = request.form.get('year')
        abstract = request.form.get('abstract')
        keywords = request.form.get('keywords')
        
        # 参数验证
        errors = []
        if not title:
            errors.append("文献标题不能为空")
        if not authors:
            errors.append("作者不能为空")
        
        if errors:
            return validation_error_response(errors)
        
        # 保存文件
        file_info, error = save_uploaded_file(file, current_user.user_id)
        if error:
            return error_response(error=error, code=400)
        
        # 转换数据类型
        try:
            publication_type_id = int(publication_type_id) if publication_type_id else None
            year = int(year) if year else None
        except ValueError:
            return validation_error_response("数据格式错误")
        
        # 创建文献记录
        paper = create_paper(
            title=title,
            authors=authors,
            file_path=file_info['file_path'],
            file_name=file_info['filename'],
            file_size=file_info['file_size'],
            file_type=file_info['file_type'],
            upload_user_id=current_user.user_id,
            publication_type_id=publication_type_id,
            publication_name=publication_name,
            year=year,
            abstract=abstract,
            keywords=keywords
        )
        
        if not paper:
            # 删除已上传的文件
            if os.path.exists(file_info['file_path']):
                os.remove(file_info['file_path'])
            return error_response(
                error="创建文献记录失败",
                code=500
            )
        
        return success_response(
            data={
                'paper_id': paper['paper_id'],
                'filename': file_info['original_filename'],
                'upload_time': paper['upload_time']
            },
            message="文献上传成功"
        )
        
    except Exception as e:
        return error_response(
            error=f"文献上传失败: {str(e)}",
            code=500
        )

@papers_bp.route('/list', methods=['GET'])
def get_papers_list_route():
    """
    文献列表路由函数（对应API 2.2）
    GET /api/papers/list?publication_type_id=1&publication_name=xxx&page=1&limit=10
    """
    try:
        # 获取查询参数
        publication_type_id = request.args.get('publication_type_id')
        publication_name = request.args.get('publication_name')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        
        # 转换数据类型
        if publication_type_id:
            publication_type_id = int(publication_type_id)
        
        # 获取文献列表
        result = get_papers_list(
            publication_type_id=publication_type_id,
            publication_name=publication_name,
            page=page,
            limit=limit
        )
        
        return success_response(
            data=result,
            message="获取文献列表成功"
        )
        
    except ValueError:
        return validation_error_response("页码和限制数量必须是数字")
    except Exception as e:
        return error_response(
            error=f"获取文献列表失败: {str(e)}",
            code=500
        )

@papers_bp.route('/<int:paper_id>', methods=['GET'])
def get_paper_detail_route(paper_id):
    """
    文献详情路由函数（对应API 2.3）
    GET /api/papers/{paper_id}
    """
    try:
        # 获取文献详情
        paper = get_paper_by_id(paper_id)
        
        if not paper:
            return error_response(
                error="文献不存在",
                code=404
            )
        
        return success_response(
            data=paper,
            message="获取文献详情成功"
        )
        
    except Exception as e:
        return error_response(
            error=f"获取文献详情失败: {str(e)}",
            code=500
        )

@papers_bp.route('/<int:paper_id>/download', methods=['GET'])
@token_required
def download_paper_route(paper_id, current_user):
    """
    文献下载路由函数（对应API 2.4）
    GET /api/papers/{paper_id}/download
    """
    try:
        # 获取文献信息
        paper = get_paper_by_id(paper_id)
        
        if not paper:
            return error_response(
                error="文献不存在",
                code=404
            )
        
        # 检查文件是否存在
        file_path = paper['file_path']
        if not os.path.exists(file_path):
            return error_response(
                error="文件不存在",
                code=404
            )
        
        # 返回文件
        return send_file(
            file_path,
            as_attachment=True,
            download_name=paper['file_name']
        )
        
    except Exception as e:
        return error_response(
            error=f"文献下载失败: {str(e)}",
            code=500
        )

@papers_bp.route('/search', methods=['GET'])
def search_papers_route():
    """
    搜索文献
    GET /api/papers/search?keyword=xxx&page=1&limit=10
    """
    try:
        # 获取查询参数
        keyword = request.args.get('keyword', '')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        
        if not keyword:
            return validation_error_response("搜索关键词不能为空")
        
        # 搜索文献
        result = search_papers(keyword, page=page, limit=limit)
        
        return pagination_response(
            data=result['papers'],
            total=result['total'],
            page=result['page'],
            limit=result['limit'],
            message="搜索文献成功"
        )
        
    except ValueError:
        return validation_error_response("页码和限制数量必须是数字")
    except Exception as e:
        return error_response(
            error=f"搜索文献失败: {str(e)}",
            code=500
        )

@papers_bp.route('/user/<int:user_id>', methods=['GET'])
@token_required
def get_user_papers_route(user_id, current_user):
    """
    获取用户上传的文献
    GET /api/papers/user/{user_id}?page=1&limit=10
    """
    try:
        # 当前用户已通过装饰器传递
        # current_user = get_user_from_request()  # 不需要这一行了
        
        # 检查权限（只能查看自己的文献，或者开放给所有人查看）
        # 这里简化实现，允许查看任何用户的文献
        
        # 获取查询参数
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        
        # 获取用户文献
        result = get_user_papers(user_id, page=page, limit=limit)
        
        return pagination_response(
            data=result['papers'],
            total=result['total'],
            page=result['page'],
            limit=result['limit'],
            message="获取用户文献成功"
        )
        
    except ValueError:
        return validation_error_response("页码和限制数量必须是数字")
    except Exception as e:
        return error_response(
            error=f"获取用户文献失败: {str(e)}",
            code=500
        )

@papers_bp.route('/statistics', methods=['GET'])
def get_paper_statistics_route():
    """
    获取文献统计信息
    GET /api/papers/statistics
    """
    try:
        # 获取文献统计
        statistics = get_paper_statistics()
        
        return success_response(
            data=statistics,
            message="获取文献统计成功"
        )
        
    except Exception as e:
        return error_response(
            error=f"获取文献统计失败: {str(e)}",
            code=500
        )

@papers_bp.route('/user-statistics', methods=['GET'])
@token_required
def get_user_statistics_route(current_user):
    """
    获取用户文献统计
    GET /api/papers/user-statistics
    """
    try:
        # 当前用户已通过装饰器传递
        # current_user = get_user_from_request()  # 不需要这一行了
        
        # 获取用户文献数量
        user_papers_result = get_user_papers(current_user.user_id, page=1, limit=1)
        total_papers = user_papers_result.get('total', 0)
        
        # 获取用户批注数量
        from models.annotation import get_user_annotations_count
        try:
            total_annotations = get_user_annotations_count(current_user.user_id)
        except:
            total_annotations = 0
        
        # 获取用户AI对话数量
        from models.ai_conversation import get_user_conversations_count
        try:
            total_conversations = get_user_conversations_count(current_user.user_id)
        except:
            total_conversations = 0
        
        return success_response(
            data={
                'total_papers': total_papers,
                'total_annotations': total_annotations,
                'total_conversations': total_conversations
            },
            message="获取用户统计成功"
        )
        
    except Exception as e:
        return error_response(
            error=f"获取用户统计失败: {str(e)}",
            code=500
        )

@papers_bp.route('/<int:paper_id>', methods=['DELETE'])
@token_required
def delete_paper_route(paper_id, current_user):
    """
    删除文献（软删除）
    DELETE /api/papers/{paper_id}
    """
    try:
        # 当前用户已通过装饰器传递
        # current_user = get_user_from_request()  # 不需要这一行了
        
        # 检查文献是否存在以及权限
        paper = get_paper_by_id(paper_id)
        if not paper:
            return error_response(
                error="文献不存在",
                code=404
            )
        
        # 检查权限（只能删除自己上传的文献）
        from utils.auth import check_user_permission
        if not check_user_permission(current_user.user_id, paper['upload_user_id']):
            return error_response(
                error="无权删除该文献",
                code=403
            )
        
        # 删除文献
        from models.paper import delete_paper
        success = delete_paper(paper_id)
        
        if not success:
            return error_response(
                error="删除文献失败",
                code=500
            )
        
        return success_response(
            message="文献删除成功"
        )
        
    except Exception as e:
        return error_response(
            error=f"删除文献失败: {str(e)}",
            code=500
        ) 