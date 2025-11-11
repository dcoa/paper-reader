#!/usr/bin/env python3
"""
用户模型
处理用户相关的数据操作
"""
import hashlib
import logging
from datetime import datetime
from .database import execute_query_one, execute_query, execute_insert, execute_update

logger = logging.getLogger(__name__)

class User:
    """用户模型类"""
    
    def __init__(self, user_id=None, username=None, password=None, email=None, 
                 role='user', create_time=None, last_login=None, status=1):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.email = email
        self.role = role
        self.create_time = create_time
        self.last_login = last_login
        self.status = status
    
    def to_dict(self):
        """转换为字典"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'create_time': self.create_time.isoformat() if self.create_time else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'status': self.status
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建用户对象"""
        return cls(
            user_id=data.get('user_id'),
            username=data.get('username'),
            password=data.get('password'),
            email=data.get('email'),
            role=data.get('role', 'user'),
            create_time=data.get('create_time'),
            last_login=data.get('last_login'),
            status=data.get('status', 1)
        )

def hash_password(password):
    """密码哈希函数"""
    return hashlib.md5(password.encode()).hexdigest()

def create_user(username, password, email=None, role='user', status=1):
    """
    创建新用户
    """
    try:
        # 检查用户名是否已存在
        existing_user = get_user_by_username(username)
        if existing_user:
            logger.warning(f"用户名已存在: {username}")
            return None
        
        # 哈希密码
        hashed_password = hash_password(password)
        
        # 插入新用户
        sql = """
        INSERT INTO users (username, password, email, role, create_time, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        
        user_id = execute_insert(sql, (
            username, hashed_password, email, role, datetime.now(), status
        ))
        
        if user_id:
            logger.info(f"创建用户成功: {username}")
            return get_user_by_id(user_id)
        else:
            logger.error(f"创建用户失败: {username}")
            return None
            
    except Exception as e:
        logger.error(f"创建用户失败: {e}")
        return None

def get_user_by_username(username):
    """
    根据用户名获取用户
    """
    try:
        sql = """
        SELECT user_id, username, password, email, role, create_time, last_login, status
        FROM users 
        WHERE username = ? AND status = 1
        """
        result = execute_query_one(sql, (username,))
        
        if result:
            user = User.from_dict(result)
            logger.info(f"根据用户名查询用户成功: {username}")
            return user
        else:
            logger.warning(f"用户不存在: {username}")
            return None
            
    except Exception as e:
        logger.error(f"根据用户名查询用户失败: {e}")
        return None

def get_user_by_id(user_id):
    """
    根据用户ID获取用户
    """
    try:
        sql = """
        SELECT user_id, username, password, email, role, create_time, last_login, status
        FROM users 
        WHERE user_id = ?
        """
        result = execute_query_one(sql, (user_id,))
        
        if result:
            user = User.from_dict(result)
            logger.info(f"根据ID查询用户成功: {user_id}")
            return user
        else:
            logger.warning(f"用户不存在: {user_id}")
            return None
            
    except Exception as e:
        logger.error(f"根据ID查询用户失败: {e}")
        return None

def verify_password(password, user_password):
    """
    验证密码
    """
    return hash_password(password) == user_password

def update_last_login(user_id):
    """
    更新最后登录时间
    """
    try:
        sql = """
        UPDATE users 
        SET last_login = ? 
        WHERE user_id = ?
        """
        affected_rows = execute_update(sql, (datetime.now(), user_id))
        logger.info(f"更新用户 {user_id} 最后登录时间成功")
        return affected_rows > 0
        
    except Exception as e:
        logger.error(f"更新最后登录时间失败: {e}")
        return False

def get_all_users(limit=10, offset=0):
    """
    获取所有用户列表
    """
    try:
        sql = """
        SELECT user_id, username, email, role, create_time, last_login, status
        FROM users 
        WHERE status = 1
        ORDER BY create_time DESC
        LIMIT ? OFFSET ?
        """
        results = execute_query(sql, (limit, offset))
        
        users = []
        for result in results:
            user = User.from_dict(result)
            users.append(user)
        
        logger.info(f"查询用户列表成功，返回 {len(users)} 条记录")
        return users
        
    except Exception as e:
        logger.error(f"查询用户列表失败: {e}")
        raise

def get_users_list(page=1, limit=10, search=None, role=None, status=None):
    """
    获取用户列表（管理员功能）
    """
    try:
        offset = (page - 1) * limit
        
        # 构建查询条件
        conditions = []
        params = []
        
        if search:
            conditions.append("(username LIKE ? OR email LIKE ?)")
            search_pattern = f"%{search}%"
            params.extend([search_pattern, search_pattern])
        
        if role:
            conditions.append("role = ?")
            params.append(role)
        
        if status is not None:
            conditions.append("status = ?")
            params.append(status)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        # 查询用户列表
        sql = f"""
        SELECT u.user_id, u.username, u.email, u.role, u.create_time, u.last_login, u.status,
               COUNT(p.paper_id) as paper_count
        FROM users u
        LEFT JOIN papers p ON u.user_id = p.upload_user_id AND p.status = 1
        WHERE {where_clause}
        GROUP BY u.user_id
        ORDER BY u.create_time DESC
        LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])
        
        results = execute_query(sql, params)
        
        # 查询总数
        count_sql = f"""
        SELECT COUNT(*) as total
        FROM users
        WHERE {where_clause}
        """
        count_params = params[:-2]  # 去掉limit和offset参数
        count_result = execute_query_one(count_sql, count_params)
        total = count_result['total'] if count_result else 0
        
        return {
            'users': results,
            'total': total,
            'page': page,
            'limit': limit
        }
        
    except Exception as e:
        logger.error(f"获取用户列表失败: {e}")
        raise

def update_user(user_id, username=None, email=None, role=None, status=None, password=None):
    """
    更新用户信息（管理员功能）
    """
    try:
        # 构建更新字段
        update_fields = []
        params = []
        
        if username is not None:
            # 检查用户名是否已被其他用户使用
            existing_user = get_user_by_username(username)
            if existing_user and existing_user.user_id != user_id:
                logger.warning(f"用户名已被其他用户使用: {username}")
                return False
            
            update_fields.append("username = ?")
            params.append(username)
        
        if email is not None:
            update_fields.append("email = ?")
            params.append(email)
        
        if role is not None:
            update_fields.append("role = ?")
            params.append(role)
        
        if status is not None:
            update_fields.append("status = ?")
            params.append(status)
        
        if password is not None:
            update_fields.append("password = ?")
            params.append(hash_password(password))
        
        if not update_fields:
            return True  # 没有需要更新的字段
        
        params.append(user_id)
        
        sql = f"""
        UPDATE users 
        SET {', '.join(update_fields)}
        WHERE user_id = ?
        """
        
        affected_rows = execute_update(sql, params)
        logger.info(f"更新用户 {user_id} 信息成功")
        return affected_rows > 0
        
    except Exception as e:
        logger.error(f"更新用户信息失败: {e}")
        raise

def update_user_status(user_id, status):
    """
    更新用户状态（管理员功能）
    """
    try:
        sql = """
        UPDATE users 
        SET status = ?
        WHERE user_id = ?
        """
        
        affected_rows = execute_update(sql, (status, user_id))
        logger.info(f"更新用户 {user_id} 状态为 {status} 成功")
        return affected_rows > 0
        
    except Exception as e:
        logger.error(f"更新用户状态失败: {e}")
        raise

def delete_user(user_id):
    """
    删除用户（真删除，管理员功能）
    """
    try:
        # 删除关联的批注记录
        delete_annotations_sql = """
        DELETE FROM annotations 
        WHERE user_id = ?
        """
        execute_update(delete_annotations_sql, (user_id,))
        
        # 删除关联的AI对话记录
        delete_conversations_sql = """
        DELETE FROM ai_conversations 
        WHERE user_id = ?
        """
        execute_update(delete_conversations_sql, (user_id,))
        
        # 删除关联的文献记录
        delete_papers_sql = """
        DELETE FROM papers 
        WHERE upload_user_id = ?
        """
        execute_update(delete_papers_sql, (user_id,))
        
        # 删除用户记录
        sql = """
        DELETE FROM users 
        WHERE user_id = ?
        """
        
        affected_rows = execute_update(sql, (user_id,))
        logger.info(f"删除用户 {user_id} 成功")
        return affected_rows > 0
        
    except Exception as e:
        logger.error(f"删除用户失败: {e}")
        raise

def get_user_statistics():
    """
    Get user statistics information (admin function)
    """
    try:
        # Total users
        total_sql = "SELECT COUNT(*) as total FROM users WHERE status = 1"
        total_result = execute_query_one(total_sql, ())
        total_users = total_result['total'] if total_result else 0

        # Active users (logged in within last 30 days)
        active_sql = """
        SELECT COUNT(*) as active
        FROM users
        WHERE status = 1 AND last_login >= datetime('now', '-30 days')
        """
        active_result = execute_query_one(active_sql, ())
        active_users = active_result['active'] if active_result else 0

        # Admin count
        admin_sql = "SELECT COUNT(*) as admin_count FROM users WHERE status = 1 AND role = 'admin'"
        admin_result = execute_query_one(admin_sql, ())
        admin_count = admin_result['admin_count'] if admin_result else 0

        # New users this month
        month_sql = """
        SELECT COUNT(*) as this_month
        FROM users
        WHERE status = 1 AND create_time >= date('now', 'start of month')
        """
        month_result = execute_query_one(month_sql, ())
        users_this_month = month_result['this_month'] if month_result else 0

        return {
            'total_users': total_users,
            'active_users': active_users,
            'admin_count': admin_count,
            'users_this_month': users_this_month
        }

    except Exception as e:
        logger.error(f"Get user statistics failed: {e}")
        raise