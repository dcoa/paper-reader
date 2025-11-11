#!/usr/bin/env python3
"""
批注模型
处理批注相关的数据操作
"""
import logging
from datetime import datetime
from .database import execute_query_one, execute_query, execute_insert, execute_update

logger = logging.getLogger(__name__)

class Annotation:
    """批注模型类"""
    
    def __init__(self, annotation_id=None, paper_id=None, user_id=None, section=None,
                 page_number=None, position_x=None, position_y=None, content=None,
                 create_time=None, update_time=None, status=1):
        self.annotation_id = annotation_id
        self.paper_id = paper_id
        self.user_id = user_id
        self.section = section
        self.page_number = page_number
        self.position_x = position_x
        self.position_y = position_y
        self.content = content
        self.create_time = create_time
        self.update_time = update_time
        self.status = status
    
    def to_dict(self):
        """转换为字典"""
        return {
            'annotation_id': self.annotation_id,
            'paper_id': self.paper_id,
            'user_id': self.user_id,
            'section': self.section,
            'page_number': self.page_number,
            'position': {
                'x': self.position_x,
                'y': self.position_y
            } if self.position_x is not None and self.position_y is not None else None,
            'content': self.content,
            'create_time': self.create_time.isoformat() if self.create_time else None,
            'update_time': self.update_time.isoformat() if self.update_time else None,
            'status': self.status
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建批注对象"""
        position = data.get('position', {})
        return cls(
            annotation_id=data.get('annotation_id'),
            paper_id=data.get('paper_id'),
            user_id=data.get('user_id'),
            section=data.get('section'),
            page_number=data.get('page_number'),
            position_x=position.get('x') if position else data.get('position_x'),
            position_y=position.get('y') if position else data.get('position_y'),
            content=data.get('content'),
            create_time=data.get('create_time'),
            update_time=data.get('update_time'),
            status=data.get('status', 1)
        )

def create_annotation(paper_id, user_id, content, section=None, page_number=None, 
                     position_x=None, position_y=None):
    """
    创建批注函数（对应API 3.1）
    """
    try:
        sql = """
        INSERT INTO annotations (paper_id, user_id, section, page_number, 
                               position_x, position_y, content, create_time, 
                               update_time, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        now = datetime.now()
        params = (paper_id, user_id, section, page_number, position_x, position_y,
                 content, now, now, 1)
        
        annotation_id = execute_insert(sql, params)
        logger.info(f"创建批注成功，批注ID: {annotation_id}")
        
        # 返回创建的批注信息
        return get_annotation_by_id(annotation_id)
        
    except Exception as e:
        logger.error(f"创建批注失败: {e}")
        raise

def get_annotations_by_paper(paper_id):
    """
    获取特定文献的所有批注（对应API 3.2）
    """
    try:
        sql = """
        SELECT a.annotation_id, a.paper_id, a.user_id, a.section, a.page_number,
               a.position_x, a.position_y, a.content, a.create_time, a.update_time,
               a.status, u.username
        FROM annotations a
        LEFT JOIN users u ON a.user_id = u.user_id
        WHERE a.paper_id = ? AND a.status = 1
        ORDER BY a.create_time DESC
        """
        results = execute_query(sql, (paper_id,))
        
        annotations = []
        for result in results:
            annotation_data = {
                'annotation_id': result['annotation_id'],
                'user_id': result['user_id'],
                'username': result['username'],
                'section': result['section'],
                'page_number': result['page_number'],
                'position': {
                    'x': result['position_x'],
                    'y': result['position_y']
                } if result['position_x'] is not None and result['position_y'] is not None else None,
                'content': result['content'],
                'create_time': result['create_time'].isoformat() if result['create_time'] else None,
                'update_time': result['update_time'].isoformat() if result['update_time'] else None
            }
            annotations.append(annotation_data)
        
        logger.info(f"查询文献 {paper_id} 批注成功，返回 {len(annotations)} 条记录")
        return annotations
        
    except Exception as e:
        logger.error(f"查询文献批注失败: {e}")
        raise

def get_annotation_by_id(annotation_id):
    """
    根据ID获取批注
    """
    try:
        sql = """
        SELECT a.annotation_id, a.paper_id, a.user_id, a.section, a.page_number,
               a.position_x, a.position_y, a.content, a.create_time, a.update_time,
               a.status, u.username
        FROM annotations a
        LEFT JOIN users u ON a.user_id = u.user_id
        WHERE a.annotation_id = ? AND a.status = 1
        """
        result = execute_query_one(sql, (annotation_id,))
        
        if result:
            annotation_data = {
                'annotation_id': result['annotation_id'],
                'paper_id': result['paper_id'],
                'user_id': result['user_id'],
                'username': result['username'],
                'section': result['section'],
                'page_number': result['page_number'],
                'position': {
                    'x': result['position_x'],
                    'y': result['position_y']
                } if result['position_x'] is not None and result['position_y'] is not None else None,
                'content': result['content'],
                'create_time': result['create_time'].isoformat() if result['create_time'] else None,
                'update_time': result['update_time'].isoformat() if result['update_time'] else None
            }
            logger.info(f"查询批注成功: {annotation_id}")
            return annotation_data
        else:
            logger.info(f"批注不存在: {annotation_id}")
            return None
            
    except Exception as e:
        logger.error(f"查询批注失败: {e}")
        raise

def delete_annotation(annotation_id, user_id=None):
    """
    删除批注函数（对应API 3.3）
    只能删除自己的批注
    """
    try:
        # 如果指定了user_id，检查是否是本人的批注
        if user_id:
            sql_check = """
            SELECT user_id FROM annotations 
            WHERE annotation_id = ? AND status = 1
            """
            result = execute_query_one(sql_check, (annotation_id,))
            
            if not result:
                logger.warning(f"批注不存在: {annotation_id}")
                return False
            
            if result['user_id'] != user_id:
                logger.warning(f"用户 {user_id} 无权删除批注 {annotation_id}")
                return False
        
        # 软删除批注
        sql = "UPDATE annotations SET status = 0 WHERE annotation_id = ?"
        affected_rows = execute_update(sql, (annotation_id,))
        
        logger.info(f"删除批注 {annotation_id} 成功")
        return affected_rows > 0
        
    except Exception as e:
        logger.error(f"删除批注失败: {e}")
        raise

def update_annotation(annotation_id, content, user_id=None, section=None, 
                     page_number=None, position_x=None, position_y=None):
    """
    更新批注
    """
    try:
        # 如果指定了user_id，检查是否是本人的批注
        if user_id:
            sql_check = """
            SELECT user_id FROM annotations 
            WHERE annotation_id = ? AND status = 1
            """
            result = execute_query_one(sql_check, (annotation_id,))
            
            if not result:
                logger.warning(f"批注不存在: {annotation_id}")
                return False
            
            if result['user_id'] != user_id:
                logger.warning(f"用户 {user_id} 无权更新批注 {annotation_id}")
                return False
        
        # 构建更新字段
        update_fields = ["content = ?", "update_time = ?"]
        params = [content, datetime.now()]
        
        if section is not None:
            update_fields.append("section = ?")
            params.append(section)
        
        if page_number is not None:
            update_fields.append("page_number = ?")
            params.append(page_number)
        
        if position_x is not None:
            update_fields.append("position_x = ?")
            params.append(position_x)
        
        if position_y is not None:
            update_fields.append("position_y = ?")
            params.append(position_y)
        
        params.append(annotation_id)
        
        sql = f"""
        UPDATE annotations 
        SET {', '.join(update_fields)}
        WHERE annotation_id = ?
        """
        
        affected_rows = execute_update(sql, params)
        logger.info(f"更新批注 {annotation_id} 成功")
        return affected_rows > 0
        
    except Exception as e:
        logger.error(f"更新批注失败: {e}")
        raise

def get_user_annotations(user_id, page=1, limit=10):
    """
    获取用户的所有批注
    """
    try:
        # 计算偏移量
        offset = (page - 1) * limit
        
        sql = """
        SELECT a.annotation_id, a.paper_id, a.section, a.page_number,
               a.position_x, a.position_y, a.content, a.create_time, a.update_time,
               p.title as paper_title
        FROM annotations a
        LEFT JOIN papers p ON a.paper_id = p.paper_id
        WHERE a.user_id = ? AND a.status = 1
        ORDER BY a.create_time DESC
        LIMIT ? OFFSET ?
        """
        params = [user_id, limit, offset]
        
        results = execute_query(sql, params)
        
        # 获取总数
        count_sql = """
        SELECT COUNT(*) as total
        FROM annotations a
        WHERE a.user_id = ? AND a.status = 1
        """
        count_result = execute_query_one(count_sql, (user_id,))
        total = count_result['total'] if count_result else 0
        
        annotations = []
        for result in results:
            annotation_data = {
                'annotation_id': result['annotation_id'],
                'paper_id': result['paper_id'],
                'paper_title': result['paper_title'],
                'section': result['section'],
                'page_number': result['page_number'],
                'position': {
                    'x': result['position_x'],
                    'y': result['position_y']
                } if result['position_x'] is not None and result['position_y'] is not None else None,
                'content': result['content'],
                'create_time': result['create_time'].isoformat() if result['create_time'] else None,
                'update_time': result['update_time'].isoformat() if result['update_time'] else None
            }
            annotations.append(annotation_data)
        
        logger.info(f"查询用户 {user_id} 批注成功，返回 {len(annotations)} 条记录，总数: {total}")
        return {
            'annotations': annotations,
            'total': total,
            'page': page,
            'limit': limit
        }
        
    except Exception as e:
        logger.error(f"查询用户批注失败: {e}")
        raise

def get_user_annotations_count(user_id):
    """
    获取用户批注数量
    """
    try:
        sql = """
        SELECT COUNT(*) as total
        FROM annotations
        WHERE user_id = ? AND status = 1
        """
        result = execute_query_one(sql, (user_id,))
        return result['total'] if result else 0
        
    except Exception as e:
        logger.error(f"获取用户批注数量失败: {e}")
        return 0

def get_annotation_statistics():
    """
    获取批注统计信息
    """
    try:
        # 总批注数
        total_sql = "SELECT COUNT(*) as total FROM annotations WHERE status = 1"
        total_result = execute_query_one(total_sql)
        total_annotations = total_result['total'] if total_result else 0
        
        # 按用户统计
        user_sql = """
        SELECT u.username, COUNT(a.annotation_id) as count
        FROM users u
        LEFT JOIN annotations a ON u.user_id = a.user_id AND a.status = 1
        GROUP BY u.user_id, u.username
        HAVING count > 0
        ORDER BY count DESC
        LIMIT 10
        """
        user_results = execute_query(user_sql)
        
        # 按文献统计
        paper_sql = """
        SELECT p.title, COUNT(a.annotation_id) as count
        FROM papers p
        LEFT JOIN annotations a ON p.paper_id = a.paper_id AND a.status = 1
        GROUP BY p.paper_id, p.title
        HAVING count > 0
        ORDER BY count DESC
        LIMIT 10
        """
        paper_results = execute_query(paper_sql)
        
        statistics = {
            'total_annotations': total_annotations,
            'by_user': [dict(result) for result in user_results],
            'by_paper': [dict(result) for result in paper_results]
        }
        
        logger.info(f"获取批注统计信息成功，总批注数: {total_annotations}")
        return statistics
        
    except Exception as e:
        logger.error(f"获取批注统计信息失败: {e}")
        raise

def search_annotations(keyword, user_id=None, page=1, limit=10):
    """
    搜索批注
    """
    try:
        # 计算偏移量
        offset = (page - 1) * limit
        
        # 构建查询条件
        where_conditions = ["a.status = 1", "a.content LIKE ?"]
        params = [f"%{keyword}%"]
        
        if user_id:
            where_conditions.append("a.user_id = ?")
            params.append(user_id)
        
        where_clause = " AND ".join(where_conditions)
        
        sql = f"""
        SELECT a.annotation_id, a.paper_id, a.section, a.page_number,
               a.position_x, a.position_y, a.content, a.create_time, a.update_time,
               p.title as paper_title, u.username
        FROM annotations a
        LEFT JOIN papers p ON a.paper_id = p.paper_id
        LEFT JOIN users u ON a.user_id = u.user_id
        WHERE {where_clause}
        ORDER BY a.create_time DESC
        LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])
        
        results = execute_query(sql, params)
        
        # 获取总数
        count_sql = f"""
        SELECT COUNT(*) as total
        FROM annotations a
        WHERE {where_clause}
        """
        count_params = params[:-2]  # 去掉 limit 和 offset
        count_result = execute_query_one(count_sql, count_params)
        total = count_result['total'] if count_result else 0
        
        annotations = []
        for result in results:
            annotation_data = {
                'annotation_id': result['annotation_id'],
                'paper_id': result['paper_id'],
                'paper_title': result['paper_title'],
                'username': result['username'],
                'section': result['section'],
                'page_number': result['page_number'],
                'position': {
                    'x': result['position_x'],
                    'y': result['position_y']
                } if result['position_x'] is not None and result['position_y'] is not None else None,
                'content': result['content'],
                'create_time': result['create_time'].isoformat() if result['create_time'] else None,
                'update_time': result['update_time'].isoformat() if result['update_time'] else None
            }
            annotations.append(annotation_data)
        
        logger.info(f"搜索批注成功，关键词: {keyword}，返回 {len(annotations)} 条记录，总数: {total}")
        return {
            'annotations': annotations,
            'total': total,
            'page': page,
            'limit': limit,
            'keyword': keyword
        }
        
    except Exception as e:
        logger.error(f"搜索批注失败: {e}")
        raise 