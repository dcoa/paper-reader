#!/usr/bin/env python3
"""
管理员管理路由
处理管理员相关的API请求
"""
from flask import Blueprint, request
from models.paper import (
    get_all_papers_admin, update_paper_admin, delete_paper_admin, 
    restore_paper_admin, get_admin_paper_statistics
)
from models.user import (
    get_users_list, update_user, update_user_status, delete_user, get_user_statistics
)
from models.publication_type import get_all_publication_types
from utils.auth import admin_required, get_user_from_request
from utils.response import success_response, error_response, validation_error_response, pagination_response

# 创建蓝图
admin_bp = Blueprint('admin', __name__)

# ================ 管理员文献管理 ================

@admin_bp.route('/papers', methods=['GET'])
@admin_required
def get_admin_papers(current_user=None):
    """
    管理员获取所有文献列表（对应API 6.2.1）
    GET /api/admin/papers?page=1&limit=10&search=关键词&publication_type_id=1&user_id=1&status=1
    """
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        search = request.args.get('search')
        publication_type_id = request.args.get('publication_type_id')
        user_id = request.args.get('user_id')
        status = request.args.get('status')
        
        # 转换数据类型
        if publication_type_id:
            publication_type_id = int(publication_type_id)
        if user_id:
            user_id = int(user_id)
        if status:
            status = int(status)
        
        # 获取文献列表
        result = get_all_papers_admin(
            page=page,
            limit=limit,
            search=search,
            publication_type_id=publication_type_id,
            user_id=user_id,
            status=status
        )
        
        return pagination_response(
            data=result['papers'],
            total=result['total'],
            page=result['page'],
            limit=result['limit'],
            message="获取文献列表成功"
        )
        
    except ValueError:
        return validation_error_response("页码、限制数量、类型ID和用户ID必须是数字")
    except Exception as e:
        return error_response(
            error=f"获取文献列表失败: {str(e)}",
            code=500
        )

@admin_bp.route('/papers/<int:paper_id>', methods=['PUT'])
@admin_required
def update_admin_paper(paper_id, current_user=None):
    """
    管理员编辑文献（对应API 6.2.2）
    PUT /api/admin/papers/{paper_id}
    """
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            return validation_error_response("请求数据格式错误")
        
        title = data.get('title')
        authors = data.get('authors')
        publication_type_id = data.get('publication_type_id')
        publication_name = data.get('publication_name')
        year = data.get('year')
        abstract = data.get('abstract')
        keywords = data.get('keywords')
        status = data.get('status')
        
        # 更新文献
        success = update_paper_admin(
            paper_id=paper_id,
            title=title,
            authors=authors,
            publication_type_id=publication_type_id,
            publication_name=publication_name,
            year=year,
            abstract=abstract,
            keywords=keywords,
            status=status
        )
        
        if not success:
            return error_response(
                error="文献不存在或更新失败",
                code=404
            )
        
        return success_response(
            data={
                'paper_id': paper_id,
                'update_time': 'now'
            },
            message="文献更新成功"
        )
        
    except Exception as e:
        return error_response(
            error=f"更新文献失败: {str(e)}",
            code=500
        )

@admin_bp.route('/papers/<int:paper_id>', methods=['DELETE'])
@admin_required
def delete_admin_paper(paper_id, current_user=None):
    """
    管理员删除文献（对应API 6.2.3）
    DELETE /api/admin/papers/{paper_id}
    """
    try:
        # 删除文献
        success = delete_paper_admin(paper_id)
        
        if not success:
            return error_response(
                error="文献不存在或删除失败",
                code=404
            )
        
        return success_response(
            message="文献删除成功"
        )
        
    except Exception as e:
        return error_response(
            error=f"删除文献失败: {str(e)}",
            code=500
        )

@admin_bp.route('/papers/<int:paper_id>/restore', methods=['POST'])
@admin_required
def restore_admin_paper(paper_id, current_user=None):
    """
    管理员恢复文献（对应API 6.2.4）
    POST /api/admin/papers/{paper_id}/restore
    """
    try:
        # 恢复文献
        success = restore_paper_admin(paper_id)
        
        if not success:
            return error_response(
                error="文献不存在或恢复失败",
                code=404
            )
        
        return success_response(
            message="文献恢复成功"
        )
        
    except Exception as e:
        return error_response(
            error=f"恢复文献失败: {str(e)}",
            code=500
        )

# ================ 管理员用户管理 ================

@admin_bp.route('/users', methods=['POST'])
@admin_required
def create_admin_user(current_user=None):
    """
    管理员添加用户（对应API 6.3.5）
    POST /api/admin/users
    """
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            return validation_error_response("请求数据格式错误")
        
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        role = data.get('role', 'user')
        status = data.get('status', 1)
        
        # 参数验证
        errors = []
        if not username:
            errors.append("用户名不能为空")
        if not password:
            errors.append("密码不能为空")
        if len(password) < 6 if password else True:
            errors.append("密码长度不能少于6位")
        if not email:
            errors.append("邮箱不能为空")
        if role not in ['user', 'admin']:
            errors.append("角色必须是user或admin")
        
        if errors:
            return validation_error_response(errors)
        
        # 创建用户
        from models.user import create_user
        new_user = create_user(username, password, email, role, status)
        
        if not new_user:
            return error_response(
                error="用户名已存在或创建失败",
                code=400
            )
        
        return success_response(
            data={
                'user_id': new_user.user_id,
                'username': new_user.username,
                'email': new_user.email,
                'role': new_user.role,
                'status': new_user.status,
                'create_time': new_user.create_time.isoformat() if new_user.create_time else None
            },
            message="用户创建成功"
        )
        
    except Exception as e:
        return error_response(
            error=f"创建用户失败: {str(e)}",
            code=500
        )

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_admin_users(current_user=None):
    """
    管理员获取用户列表（对应API 6.3.1）
    GET /api/admin/users?page=1&limit=10&search=用户名&role=admin&status=1
    """
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        search = request.args.get('search')
        role = request.args.get('role')
        status = request.args.get('status')
        
        # 转换数据类型
        if status:
            status = int(status)
        
        # 获取用户列表
        result = get_users_list(
            page=page,
            limit=limit,
            search=search,
            role=role,
            status=status
        )
        
        return pagination_response(
            data=result['users'],
            total=result['total'],
            page=result['page'],
            limit=result['limit'],
            message="获取用户列表成功"
        )
        
    except ValueError:
        return validation_error_response("页码、限制数量和状态必须是数字")
    except Exception as e:
        return error_response(
            error=f"获取用户列表失败: {str(e)}",
            code=500
        )

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_admin_user(user_id, current_user=None):
    """
    管理员编辑用户（对应API 6.3.2）
    PUT /api/admin/users/{user_id}
    """
    try:
        # 获取当前管理员用户
        current_user = get_user_from_request()
        
        # 防止管理员修改自己的角色
        if current_user.user_id == user_id:
            data = request.get_json() or {}
            if 'role' in data and data['role'] != 'admin':
                return validation_error_response("不能修改自己的管理员角色")
        
        # 获取请求数据
        data = request.get_json()
        if not data:
            return validation_error_response("请求数据格式错误")
        
        username = data.get('username')
        email = data.get('email')
        role = data.get('role')
        status = data.get('status')
        password = data.get('password')
        
        # 更新用户
        success = update_user(
            user_id=user_id,
            username=username,
            email=email,
            role=role,
            status=status,
            password=password
        )
        
        if not success:
            return error_response(
                error="用户不存在或更新失败",
                code=404
            )
        
        return success_response(
            data={
                'user_id': user_id,
                'update_time': 'now'
            },
            message="用户更新成功"
        )
        
    except Exception as e:
        return error_response(
            error=f"更新用户失败: {str(e)}",
            code=500
        )

@admin_bp.route('/users/<int:user_id>/status', methods=['PUT'])
@admin_required
def update_admin_user_status(user_id, current_user=None):
    """
    管理员禁用/启用用户（对应API 6.3.3）
    PUT /api/admin/users/{user_id}/status
    """
    try:
        # 获取当前管理员用户
        current_user = get_user_from_request()
        
        # 防止管理员禁用自己
        if current_user.user_id == user_id:
            return validation_error_response("不能禁用自己的账户")
        
        # 获取请求数据
        data = request.get_json()
        if not data:
            return validation_error_response("请求数据格式错误")
        
        status = data.get('status')
        if status is None:
            return validation_error_response("状态不能为空")
        
        # 更新用户状态
        success = update_user_status(user_id, status)
        
        if not success:
            return error_response(
                error="用户不存在或更新失败",
                code=404
            )
        
        status_text = "启用" if status == 1 else "禁用"
        return success_response(
            message=f"用户{status_text}成功"
        )
        
    except Exception as e:
        return error_response(
            error=f"更新用户状态失败: {str(e)}",
            code=500
        )

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_admin_user(user_id, current_user=None):
    """
    管理员删除用户（对应API 6.3.4）
    DELETE /api/admin/users/{user_id}
    """
    try:
        # 获取当前管理员用户
        current_user = get_user_from_request()
        
        # 防止管理员删除自己
        if current_user.user_id == user_id:
            return validation_error_response("不能删除自己的账户")
        
        # 删除用户
        success = delete_user(user_id)
        
        if not success:
            return error_response(
                error="用户不存在或删除失败",
                code=404
            )
        
        return success_response(
            message="用户删除成功"
        )
        
    except Exception as e:
        return error_response(
            error=f"删除用户失败: {str(e)}",
            code=500
        )

# ================ 管理员统计信息 ================

@admin_bp.route('/statistics', methods=['GET'])
@admin_required
def get_admin_statistics(current_user=None):
    """
    管理员获取系统统计信息（对应API 6.4.1）
    GET /api/admin/statistics
    """
    try:
        # 获取用户统计
        user_stats = get_user_statistics()
        
        # 获取文献统计
        paper_stats = get_admin_paper_statistics()
        
        # 合并统计信息
        statistics = {
            **user_stats,
            **paper_stats
        }
        
        return success_response(
            data=statistics,
            message="获取统计信息成功"
        )
        
    except Exception as e:
        return error_response(
            error=f"获取统计信息失败: {str(e)}",
            code=500
        )

# ================ 辅助接口 ================

@admin_bp.route('/publication-types', methods=['GET'])
@admin_required
def get_admin_publication_types(current_user=None):
    """
    管理员获取文献类型列表
    GET /api/admin/publication-types
    """
    try:
        publication_types = get_all_publication_types()
        
        return success_response(
            data=publication_types,
            message="获取文献类型列表成功"
        )
        
    except Exception as e:
        return error_response(
            error=f"获取文献类型列表失败: {str(e)}",
            code=500
        ) 