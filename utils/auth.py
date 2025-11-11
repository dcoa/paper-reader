#!/usr/bin/env python3
"""
认证工具模块
处理用户认证、权限验证等功能
"""
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import request, g, jsonify
from models.database import execute_query_one, execute_insert, execute_update
from utils.response import unauthorized_response, forbidden_response

logger = logging.getLogger(__name__)

def hash_password(password):
    """
    简单密码哈希
    """
    # 使用简单的MD5哈希（实际应用中应使用更安全的方法）
    return hashlib.md5(password.encode()).hexdigest()

def verify_password(password, hashed_password):
    """
    验证密码
    """
    return hash_password(password) == hashed_password

def generate_simple_token(user_id, username):
    """
    生成简单令牌
    """
    # 生成随机令牌
    token = secrets.token_urlsafe(32)

    # 计算过期时间
    expire_time = datetime.now() + timedelta(hours=24 * 7)  # 7天

    # 保存令牌到数据库
    sql = """
    INSERT INTO user_tokens (user_id, token, expire_time)
    VALUES (?, ?, ?)
    """
    try:
        execute_insert(sql, (user_id, token, expire_time))
        logger.info(f"为用户 {username} 生成令牌成功")
        return token
    except Exception as e:
        logger.error(f"生成令牌失败: {e}")
        return None

def verify_token(token):
    """
    验证令牌
    """
    if not token:
        return None

    sql = """
    SELECT t.user_id, t.token, t.expire_time, u.username, u.role, u.status
    FROM user_tokens t
    JOIN users u ON t.user_id = u.user_id
    WHERE t.token = ? AND t.status = 1 AND u.status = 1
    """

    try:
        result = execute_query_one(sql, (token,))

        if not result:
            return None

        # 检查令牌是否过期
        expire_time = result['expire_time']
        # 如果expire_time是字符串，转换为datetime对象
        if isinstance(expire_time, str):
            expire_time = datetime.fromisoformat(expire_time)

        if expire_time < datetime.now():
            logger.warning(f"令牌已过期: {token[:8]}...")
            return None

        return result

    except Exception as e:
        logger.error(f"验证令牌失败: {e}")
        return None

def get_current_user():
    """
    获取当前用户信息
    """
    # 从请求头获取令牌
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    
    # 解析Bearer令牌
    try:
        if not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        token_info = verify_token(token)
        
        if not token_info:
            return None
        
        # 构建用户对象
        from models.user import User
        user = User(
            user_id=token_info['user_id'],
            username=token_info['username'],
            role=token_info.get('role', 'user'),
            status=token_info['status']
        )
        
        return user
        
    except Exception as e:
        logger.error(f"获取当前用户失败: {e}")
        return None

def get_user_from_request():
    """
    从请求中获取用户（用于装饰器）
    """
    return getattr(g, 'current_user', None)

def token_required(f):
    """
    令牌验证装饰器
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = get_current_user()
        if current_user is None:
            return unauthorized_response("请先登录")
        
        # 将当前用户存储到全局变量中
        g.current_user = current_user
        
        # 将current_user作为参数传递给被装饰的函数
        return f(*args, current_user=current_user, **kwargs)
    
    return decorated_function

def admin_required(f):
    """
    管理员权限验证装饰器
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = get_current_user()
        if current_user is None:
            return unauthorized_response("请先登录")
        
        # 检查是否为管理员
        if not check_admin_permission(current_user):
            return forbidden_response("需要管理员权限")
        
        # 将当前用户存储到全局变量中
        g.current_user = current_user
        
        # 将current_user作为参数传递给被装饰的函数
        return f(*args, current_user=current_user, **kwargs)
    
    return decorated_function

def get_user_role(user):
    """
    获取用户角色
    """
    if not user:
        return None
    return getattr(user, 'role', 'user')

def check_admin_permission(user):
    """
    检查管理员权限
    """
    if not user:
        return False
    
    user_role = get_user_role(user)
    return user_role == 'admin'

def check_user_permission(user_id, resource_user_id):
    """
    检查用户权限（简单实现：只能操作自己的资源）
    """
    return user_id == resource_user_id

def update_last_login(user_id):
    """
    更新最后登录时间
    """
    sql = """
    UPDATE users 
    SET last_login = %s 
    WHERE user_id = %s
    """
    try:
        execute_update(sql, (datetime.now(), user_id))
        logger.info(f"更新用户 {user_id} 最后登录时间成功")
        return True
    except Exception as e:
        logger.error(f"更新最后登录时间失败: {e}")
        return False 