#!/usr/bin/env python3
"""
用户认证路由
处理用户登录、注册、用户信息等API请求
"""
from flask import Blueprint, request
from models.user import get_user_by_username, verify_password, update_last_login, create_user
from utils.auth import generate_simple_token, token_required, get_user_from_request
from utils.response import success_response, error_response, validation_error_response

# 创建蓝图
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    用户登录路由函数（对应API 1.1）
    POST /api/auth/login
    """
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            return validation_error_response("请求数据格式错误")
        
        username = data.get('username')
        password = data.get('password')
        
        # 参数验证
        if not username or not password:
            return validation_error_response("用户名和密码不能为空")
        
        # 用户认证
        user = get_user_by_username(username)
        if not user or not verify_password(password, user.password):
            return error_response(
                error="用户名或密码错误",
                code=401
            )
        
        # 更新最后登录时间
        update_last_login(user.user_id)
        
        # 生成token
        token = generate_simple_token(user.user_id, user.username)
        if not token:
            return error_response(
                error="生成token失败",
                code=500
            )
        
        # 返回用户信息和token（包含角色信息）
        session_data = {
            'user_id': user.user_id,
            'username': user.username,
            'role': user.role,
            'token': token
        }
        
        return success_response(
            data=session_data,
            message="登录成功"
        )
        
    except Exception as e:
        return error_response(
            error=f"登录失败: {str(e)}",
            code=500
        )

@auth_bp.route('/user/info', methods=['GET'])
@token_required
def get_user_info(current_user):
    """
    获取用户信息路由函数（对应API 1.2）
    GET /api/auth/user/info
    """
    try:
        # 当前用户已通过装饰器传递
        
        if not current_user:
            return error_response(
                error="获取用户信息失败",
                code=401
            )
        
        # 构建用户信息响应（包含角色信息）
        user_info = {
            'user_id': current_user.user_id,
            'username': current_user.username,
            'email': current_user.email,
            'role': current_user.role,
            'create_time': current_user.create_time.isoformat() if current_user.create_time else None,
            'last_login': current_user.last_login.isoformat() if current_user.last_login else None
        }
        
        return success_response(
            data=user_info,
            message="获取用户信息成功"
        )
        
    except Exception as e:
        return error_response(
            error=f"获取用户信息失败: {str(e)}",
            code=500
        )

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    用户注册路由函数
    POST /api/auth/register
    """
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            return validation_error_response("请求数据格式错误")
        
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        
        # 参数验证
        errors = []
        if not username:
            errors.append("用户名不能为空")
        if not password:
            errors.append("密码不能为空")
        if len(password) < 6 if password else True:
            errors.append("密码长度不能少于6位")
        
        if errors:
            return validation_error_response(errors)
        
        # 创建用户（默认为普通用户）
        new_user = create_user(username, password, email, role='user')
        
        if not new_user:
            return error_response(
                error="用户名已存在",
                code=400
            )
        
        # 生成token
        token = generate_simple_token(new_user.user_id, new_user.username)
        if not token:
            return error_response(
                error="生成token失败",
                code=500
            )
        
        # 返回用户信息和token
        session_data = {
            'user_id': new_user.user_id,
            'username': new_user.username,
            'role': new_user.role,
            'token': token
        }
        
        return success_response(
            data=session_data,
            message="注册成功"
        )
        
    except Exception as e:
        return error_response(
            error=f"注册失败: {str(e)}",
            code=500
        )

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    """
    用户退出登录
    POST /api/auth/logout
    """
    try:
        # 获取token
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

            # 将token标记为失效
            from models.database import execute_update
            sql = """
            UPDATE user_tokens
            SET status = 0
            WHERE token = ?
            """
            execute_update(sql, (token,))

        return success_response(
            message="退出登录成功"
        )

    except Exception as e:
        return error_response(
            error=f"退出登录失败: {str(e)}",
            code=500
        )

@auth_bp.route('/verify', methods=['GET'])
@token_required
def verify_token():
    """
    验证token有效性
    GET /api/auth/verify
    """
    try:
        current_user = get_user_from_request()
        
        return success_response(
            data={
                'user_id': current_user.user_id,
                'username': current_user.username,
                'role': current_user.role,
                'valid': True
            },
            message="Token验证成功"
        )
        
    except Exception as e:
        return error_response(
            error=f"Token验证失败: {str(e)}",
            code=500
        ) 