#!/usr/bin/env python3
"""
文献类型模型
处理文献类型相关的数据操作
"""
import logging
from datetime import datetime
from .database import execute_query_one, execute_query, execute_insert, execute_update

logger = logging.getLogger(__name__)

class PublicationType:
    """文献类型模型类"""
    
    def __init__(self, type_id=None, type_name=None, create_time=None):
        self.type_id = type_id
        self.type_name = type_name
        self.create_time = create_time
    
    def to_dict(self):
        """转换为字典"""
        return {
            'type_id': self.type_id,
            'type_name': self.type_name,
            'create_time': self.create_time.isoformat() if self.create_time else None
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建文献类型对象"""
        return cls(
            type_id=data.get('type_id'),
            type_name=data.get('type_name'),
            create_time=data.get('create_time')
        )

def get_all_publication_types():
    """
    获取所有文献类型列表（对应API 5.1）
    """
    try:
        sql = """
        SELECT pt.type_id, pt.type_name, pt.create_time,
               COUNT(p.paper_id) as paper_count
        FROM publication_types pt
        LEFT JOIN papers p ON pt.type_id = p.publication_type_id AND p.status = 1
        GROUP BY pt.type_id, pt.type_name, pt.create_time
        ORDER BY pt.type_name
        """
        results = execute_query(sql)
        
        publication_types = []
        for result in results:
            type_data = {
                'type_id': result['type_id'],
                'type_name': result['type_name'],
                'create_time': result['create_time'],
                'paper_count': result['paper_count']
            }
            publication_types.append(type_data)
        
        logger.info(f"查询文献类型列表成功，返回 {len(publication_types)} 条记录")
        return publication_types
        
    except Exception as e:
        logger.error(f"查询文献类型列表失败: {e}")
        raise

def get_publication_type_by_id(type_id):
    """
    根据ID获取文献类型
    """
    try:
        sql = """
        SELECT type_id, type_name, create_time
        FROM publication_types 
        WHERE type_id = ?
        """
        result = execute_query_one(sql, (type_id,))
        
        if result:
            logger.info(f"查询文献类型成功: {type_id}")
            return PublicationType.from_dict(result)
        else:
            logger.info(f"文献类型不存在: {type_id}")
            return None
            
    except Exception as e:
        logger.error(f"查询文献类型失败: {e}")
        raise

def get_publication_type_by_name(type_name):
    """
    根据名称获取文献类型
    """
    try:
        sql = """
        SELECT type_id, type_name, create_time
        FROM publication_types 
        WHERE type_name = ?
        """
        result = execute_query_one(sql, (type_name,))
        
        if result:
            logger.info(f"查询文献类型成功: {type_name}")
            return PublicationType.from_dict(result)
        else:
            logger.info(f"文献类型不存在: {type_name}")
            return None
            
    except Exception as e:
        logger.error(f"查询文献类型失败: {e}")
        raise

def create_publication_type(type_name):
    """
    创建文献类型
    """
    try:
        # 检查类型名称是否已存在
        existing_type = get_publication_type_by_name(type_name)
        if existing_type:
            logger.warning(f"文献类型 {type_name} 已存在")
            return existing_type
        
        # 创建新文献类型
        sql = """
        INSERT INTO publication_types (type_name, create_time)
        VALUES (?, ?)
        """
        params = (type_name, datetime.now())
        
        type_id = execute_insert(sql, params)
        logger.info(f"创建文献类型成功，类型ID: {type_id}")
        
        # 返回创建的文献类型信息
        return get_publication_type_by_id(type_id)
        
    except Exception as e:
        logger.error(f"创建文献类型失败: {e}")
        raise

def get_publication_type_by_id(type_id):
    """
    根据ID获取文献类型详情
    """
    try:
        sql = """
        SELECT publication_type_id, type_name, description, create_time
        FROM publication_types
        WHERE publication_type_id = ?
        """
        result = execute_query_one(sql, (type_id,))
        
        if result:
            publication_type = PublicationType(
                publication_type_id=result['publication_type_id'],
                type_name=result['type_name'],
                description=result['description'],
                create_time=result['create_time']
            )
            logger.info(f"查询文献类型成功: ID={type_id}, Name={result['type_name']}")
            return publication_type
        else:
            logger.info(f"文献类型不存在: {type_id}")
            return None
            
    except Exception as e:
        logger.error(f"查询文献类型失败: {e}")
        raise

def update_publication_type(type_id, type_name):
    """
    更新文献类型
    """
    try:
        sql = """
        UPDATE publication_types 
        SET type_name = ? 
        WHERE type_id = ?
        """
        params = (type_name, type_id)
        
        affected_rows = execute_update(sql, params)
        logger.info(f"更新文献类型 {type_id} 成功")
        return affected_rows > 0
        
    except Exception as e:
        logger.error(f"更新文献类型失败: {e}")
        raise

def delete_publication_type(type_id):
    """
    删除文献类型（检查是否有关联的文献）
    """
    try:
        # 检查是否有关联的文献
        sql_check = """
        SELECT COUNT(*) as count 
        FROM papers 
        WHERE publication_type_id = ? AND status = 1
        """
        result = execute_query_one(sql_check, (type_id,))
        
        if result and result['count'] > 0:
            logger.warning(f"文献类型 {type_id} 有关联的文献，不能删除")
            return False
        
        # 删除文献类型
        sql_delete = "DELETE FROM publication_types WHERE type_id = ?"
        affected_rows = execute_update(sql_delete, (type_id,))
        
        logger.info(f"删除文献类型 {type_id} 成功")
        return affected_rows > 0
        
    except Exception as e:
        logger.error(f"删除文献类型失败: {e}")
        raise

def get_publication_type_statistics():
    """
    获取文献类型统计信息
    """
    try:
        sql = """
        SELECT pt.type_id, pt.type_name,
               COUNT(p.paper_id) as paper_count,
               COUNT(DISTINCT p.upload_user_id) as user_count
        FROM publication_types pt
        LEFT JOIN papers p ON pt.type_id = p.publication_type_id AND p.status = 1
        GROUP BY pt.type_id, pt.type_name
        ORDER BY paper_count DESC, pt.type_name
        """
        results = execute_query(sql)
        
        statistics = []
        for result in results:
            stat_data = {
                'type_id': result['type_id'],
                'type_name': result['type_name'],
                'paper_count': result['paper_count'],
                'user_count': result['user_count']
            }
            statistics.append(stat_data)
        
        logger.info(f"获取文献类型统计信息成功，返回 {len(statistics)} 条记录")
        return statistics
        
    except Exception as e:
        logger.error(f"获取文献类型统计信息失败: {e}")
        raise 