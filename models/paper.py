#!/usr/bin/env python3
"""
文献模型
处理文献相关的数据操作
"""
import os
import logging
from datetime import datetime
from .database import execute_query_one, execute_query, execute_insert, execute_update

logger = logging.getLogger(__name__)

class Paper:
    """文献模型类"""
    
    def __init__(self, paper_id=None, title=None, authors=None, publication_type_id=None,
                 publication_name=None, year=None, abstract=None, keywords=None,
                 file_path=None, file_name=None, file_size=None, file_type=None,
                 upload_user_id=None, upload_time=None, status=1):
        self.paper_id = paper_id
        self.title = title
        self.authors = authors
        self.publication_type_id = publication_type_id
        self.publication_name = publication_name
        self.year = year
        self.abstract = abstract
        self.keywords = keywords
        self.file_path = file_path
        self.file_name = file_name
        self.file_size = file_size
        self.file_type = file_type
        self.upload_user_id = upload_user_id
        self.upload_time = upload_time
        self.status = status
    
    def to_dict(self):
        """转换为字典"""
        return {
            'paper_id': self.paper_id,
            'title': self.title,
            'authors': self.authors,
            'publication_type_id': self.publication_type_id,
            'publication_name': self.publication_name,
            'year': self.year,
            'abstract': self.abstract,
            'keywords': self.keywords,
            'file_path': self.file_path,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'upload_user_id': self.upload_user_id,
            'upload_time': self.upload_time.isoformat() if self.upload_time else None,
            'status': self.status
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建文献对象"""
        return cls(
            paper_id=data.get('paper_id'),
            title=data.get('title'),
            authors=data.get('authors'),
            publication_type_id=data.get('publication_type_id'),
            publication_name=data.get('publication_name'),
            year=data.get('year'),
            abstract=data.get('abstract'),
            keywords=data.get('keywords'),
            file_path=data.get('file_path'),
            file_name=data.get('file_name'),
            file_size=data.get('file_size'),
            file_type=data.get('file_type'),
            upload_user_id=data.get('upload_user_id'),
            upload_time=data.get('upload_time'),
            status=data.get('status', 1)
        )

def create_paper(title, authors, file_path, file_name, file_size, file_type,
                upload_user_id, publication_type_id=None, publication_name=None,
                year=None, abstract=None, keywords=None):
    """
    Create paper function (corresponding to API 2.1)
    """
    try:
        sql = """
        INSERT INTO papers (title, authors, publication_type_id, publication_name,
                          year, abstract, keywords, file_path, file_name, file_size,
                          file_type, upload_user_id, upload_time, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (title, authors, publication_type_id, publication_name, year,
                 abstract, keywords, file_path, file_name, file_size, file_type,
                 upload_user_id, datetime.now(), 1)

        paper_id = execute_insert(sql, params)
        logger.info(f"Create paper successful, paper ID: {paper_id}")

        # Return created paper information
        return get_paper_by_id(paper_id)

    except Exception as e:
        logger.error(f"Create paper failed: {e}")
        raise

def get_papers_list(publication_type_id=None, publication_name=None, page=1, limit=10):
    """
    Get papers list function (corresponding to API 2.2)
    """
    try:
        # Build query conditions
        where_conditions = ["p.status = 1"]
        params = []

        if publication_type_id:
            where_conditions.append("p.publication_type_id = ?")
            params.append(publication_type_id)

        if publication_name:
            where_conditions.append("p.publication_name LIKE ?")
            params.append(f"%{publication_name}%")

        where_clause = " AND ".join(where_conditions)

        # Calculate offset
        offset = (page - 1) * limit

        # Query papers list
        sql = f"""
        SELECT p.paper_id, p.title, p.authors, p.publication_type_id, p.publication_name,
               p.year, p.upload_time, p.file_name, p.file_size, p.file_type,
               pt.type_name as publication_type, u.username as upload_user
        FROM papers p
        LEFT JOIN publication_types pt ON p.publication_type_id = pt.type_id
        LEFT JOIN users u ON p.upload_user_id = u.user_id
        WHERE {where_clause}
        ORDER BY p.upload_time DESC
        LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])

        results = execute_query(sql, params)

        # Get total count
        count_sql = f"""
        SELECT COUNT(*) as total
        FROM papers p
        WHERE {where_clause}
        """
        count_params = params[:-2]  # Remove limit and offset
        count_result = execute_query_one(count_sql, count_params)
        total = count_result['total'] if count_result else 0

        papers = []
        for result in results:
            paper_data = dict(result) if isinstance(result, dict) else result
            papers.append(paper_data)

        logger.info(f"Query papers list successful, returned {len(papers)} records, total: {total}")
        return {
            'papers': papers,
            'total': total,
            'page': page,
            'limit': limit
        }

    except Exception as e:
        logger.error(f"Query papers list failed: {e}")
        raise

def get_paper_by_id(paper_id):
    """
    获取文献详情函数（对应API 2.3）
    """
    try:
        sql = """
        SELECT p.paper_id, p.title, p.authors, p.publication_type_id, p.publication_name, 
               p.year, p.abstract, p.keywords, p.file_path, p.file_name, p.file_size, 
               p.file_type, p.upload_user_id, p.upload_time, p.status,
               pt.type_name as publication_type, u.username as upload_user
        FROM papers p
        LEFT JOIN publication_types pt ON p.publication_type_id = pt.type_id
        LEFT JOIN users u ON p.upload_user_id = u.user_id
        WHERE p.paper_id = ? AND p.status = 1
        """
        result = execute_query_one(sql, (paper_id,))
        
        if result:
            logger.info(f"查询文献详情成功: {paper_id}")
            return dict(result)
        else:
            logger.info(f"文献不存在: {paper_id}")
            return None
            
    except Exception as e:
        logger.error(f"查询文献详情失败: {e}")
        raise

def get_papers_by_publication_type(publication_type_id, page=1, limit=10):
    """
    按文献类型检索函数（对应API 2.2）
    """
    try:
        return get_papers_list(publication_type_id=publication_type_id, page=page, limit=limit)
    except Exception as e:
        logger.error(f"按文献类型检索失败: {e}")
        raise

def update_paper(paper_id, **kwargs):
    """
    更新文献信息
    """
    try:
        # 构建更新字段
        update_fields = []
        params = []
        
        allowed_fields = ['title', 'authors', 'publication_type_id', 'publication_name',
                         'year', 'abstract', 'keywords']
        
        for field in allowed_fields:
            if field in kwargs:
                update_fields.append(f"{field} = ?")
                params.append(kwargs[field])
        
        if not update_fields:
            logger.warning("没有要更新的字段")
            return False
        
        params.append(paper_id)
        
        sql = f"""
        UPDATE papers 
        SET {', '.join(update_fields)}
        WHERE paper_id = ?
        """
        
        affected_rows = execute_update(sql, params)
        logger.info(f"更新文献 {paper_id} 成功")
        return affected_rows > 0
        
    except Exception as e:
        logger.error(f"更新文献失败: {e}")
        raise

def delete_paper(paper_id):
    """
    删除文献（软删除）
    """
    try:
        sql = "UPDATE papers SET status = 0 WHERE paper_id = ?"
        affected_rows = execute_update(sql, (paper_id,))
        logger.info(f"删除文献 {paper_id} 成功")
        return affected_rows > 0
        
    except Exception as e:
        logger.error(f"删除文献失败: {e}")
        raise

def search_papers(keyword, page=1, limit=10):
    """
    搜索文献
    """
    try:
        # 计算偏移量
        offset = (page - 1) * limit
        
        # 搜索文献
        sql = """
        SELECT p.paper_id, p.title, p.authors, p.publication_type_id, p.publication_name, 
               p.year, p.upload_time, p.file_name, p.file_size, p.file_type,
               pt.type_name as publication_type, u.username as upload_user
        FROM papers p
        LEFT JOIN publication_types pt ON p.publication_type_id = pt.type_id
        LEFT JOIN users u ON p.upload_user_id = u.user_id
        WHERE p.status = 1 AND (
            p.title LIKE ? OR p.authors LIKE ? OR p.abstract LIKE ? OR p.keywords LIKE ?
        )
        ORDER BY p.upload_time DESC
        LIMIT ? OFFSET ?
        """
        search_param = f"%{keyword}%"
        params = [search_param, search_param, search_param, search_param, limit, offset]
        
        results = execute_query(sql, params)
        
        # 获取总数
        count_sql = """
        SELECT COUNT(*) as total
        FROM papers p
        WHERE p.status = 1 AND (
            p.title LIKE ? OR p.authors LIKE ? OR p.abstract LIKE ? OR p.keywords LIKE ?
        )
        """
        count_params = [search_param, search_param, search_param, search_param]
        count_result = execute_query_one(count_sql, count_params)
        total = count_result['total'] if count_result else 0
        
        papers = []
        for result in results:
            paper_data = dict(result)
            papers.append(paper_data)
        
        logger.info(f"搜索文献成功，关键词: {keyword}，返回 {len(papers)} 条记录，总数: {total}")
        return {
            'papers': papers,
            'total': total,
            'page': page,
            'limit': limit,
            'keyword': keyword
        }
        
    except Exception as e:
        logger.error(f"搜索文献失败: {e}")
        raise

def get_user_papers(user_id, page=1, limit=10):
    """
    获取用户上传的文献
    """
    try:
        # 计算偏移量
        offset = (page - 1) * limit
        
        # 查询用户文献
        sql = """
        SELECT p.paper_id, p.title, p.authors, p.publication_type_id, p.publication_name, 
               p.year, p.upload_time, p.file_name, p.file_size, p.file_type,
               pt.type_name as publication_type
        FROM papers p
        LEFT JOIN publication_types pt ON p.publication_type_id = pt.type_id
        WHERE p.upload_user_id = ? AND p.status = 1
        ORDER BY p.upload_time DESC
        LIMIT ? OFFSET ?
        """
        params = [user_id, limit, offset]
        
        results = execute_query(sql, params)
        
        # 获取总数
        count_sql = """
        SELECT COUNT(*) as total
        FROM papers p
        WHERE p.upload_user_id = ? AND p.status = 1
        """
        count_result = execute_query_one(count_sql, (user_id,))
        total = count_result['total'] if count_result else 0
        
        papers = []
        for result in results:
            paper_data = dict(result)
            papers.append(paper_data)
        
        logger.info(f"查询用户 {user_id} 文献成功，返回 {len(papers)} 条记录，总数: {total}")
        return {
            'papers': papers,
            'total': total,
            'page': page,
            'limit': limit
        }
        
    except Exception as e:
        logger.error(f"查询用户文献失败: {e}")
        raise

def get_paper_statistics():
    """
    Get paper statistics information
    """
    try:
        # Total papers
        total_sql = "SELECT COUNT(*) as total FROM papers WHERE status = 1"
        total_result = execute_query_one(total_sql, ())
        total_papers = total_result['total'] if total_result else 0

        # Papers uploaded this month
        month_sql = """
        SELECT COUNT(*) as this_month
        FROM papers
        WHERE status = 1 AND upload_time >= date('now', 'start of month')
        """
        month_result = execute_query_one(month_sql, ())
        papers_this_month = month_result['this_month'] if month_result else 0

        # Statistics by publication type
        type_sql = """
        SELECT pt.type_name, COUNT(p.paper_id) as count
        FROM publication_types pt
        LEFT JOIN papers p ON pt.type_id = p.publication_type_id AND p.status = 1
        GROUP BY pt.type_id, pt.type_name
        ORDER BY count DESC
        """
        type_results = execute_query(type_sql, ())
        paper_types = [dict(result) if isinstance(result, dict) else result for result in type_results]

        # File size statistics
        size_sql = "SELECT SUM(file_size) as total_size FROM papers WHERE status = 1"
        size_result = execute_query_one(size_sql, ())
        total_size = size_result['total_size'] if size_result else 0

        logger.info("Get paper statistics successful")
        return {
            'total_papers': total_papers,
            'papers_this_month': papers_this_month,
            'paper_types': paper_types,
            'total_size': total_size
        }

    except Exception as e:
        logger.error(f"Get paper statistics failed: {e}")
        raise

# ================ 管理员功能 ================

def get_all_papers_admin(page=1, limit=10, search=None, publication_type_id=None, user_id=None, status=None):
    """
    管理员获取所有文献列表（对应API 6.2.1）
    """
    try:
        offset = (page - 1) * limit
        
        # 构建查询条件
        conditions = []
        params = []
        
        if search:
            conditions.append("(p.title LIKE ? OR p.authors LIKE ? OR p.keywords LIKE ?)")
            search_pattern = f"%{search}%"
            params.extend([search_pattern, search_pattern, search_pattern])
        
        if publication_type_id:
            conditions.append("p.publication_type_id = ?")
            params.append(publication_type_id)
        
        if user_id:
            conditions.append("p.upload_user_id = ?")
            params.append(user_id)
        
        if status is not None:
            conditions.append("p.status = ?")
            params.append(status)
        else:
            # 默认只显示正常状态的文献，但管理员可以看到所有状态
            pass
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        # 查询文献列表
        sql = f"""
        SELECT p.paper_id, p.title, p.authors, p.publication_type_id, p.publication_name, 
               p.year, p.abstract, p.keywords, p.file_path, p.file_name, p.file_size, 
               p.file_type, p.upload_user_id, p.upload_time, p.status,
               pt.type_name as publication_type, u.username as upload_user,
               COUNT(a.annotation_id) as annotation_count
        FROM papers p
        LEFT JOIN publication_types pt ON p.publication_type_id = pt.type_id
        LEFT JOIN users u ON p.upload_user_id = u.user_id
        LEFT JOIN annotations a ON p.paper_id = a.paper_id AND a.status = 1
        WHERE {where_clause}
        GROUP BY p.paper_id
        ORDER BY p.upload_time DESC
        LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])
        
        results = execute_query(sql, params)
        
        # 查询总数
        count_sql = f"""
        SELECT COUNT(*) as total
        FROM papers p
        WHERE {where_clause}
        """
        count_params = params[:-2]  # 去掉limit和offset参数
        count_result = execute_query_one(count_sql, count_params)
        total = count_result['total'] if count_result else 0
        
        papers = [dict(result) for result in results]
        
        logger.info(f"管理员查询文献列表成功，返回 {len(papers)} 条记录，总数: {total}")
        return {
            'papers': papers,
            'total': total,
            'page': page,
            'limit': limit
        }
        
    except Exception as e:
        logger.error(f"管理员查询文献列表失败: {e}")
        raise

def update_paper_admin(paper_id, title=None, authors=None, publication_type_id=None, 
                      publication_name=None, year=None, abstract=None, keywords=None, status=None):
    """
    管理员更新文献信息（对应API 6.2.2）
    """
    try:
        # 构建更新字段
        update_fields = []
        params = []
        
        if title is not None:
            update_fields.append("title = ?")
            params.append(title)
        
        if authors is not None:
            update_fields.append("authors = ?")
            params.append(authors)
        
        if publication_type_id is not None:
            update_fields.append("publication_type_id = ?")
            params.append(publication_type_id)
        
        if publication_name is not None:
            update_fields.append("publication_name = ?")
            params.append(publication_name)
        
        if year is not None:
            update_fields.append("year = ?")
            params.append(year)
        
        if abstract is not None:
            update_fields.append("abstract = ?")
            params.append(abstract)
        
        if keywords is not None:
            update_fields.append("keywords = ?")
            params.append(keywords)
        
        if status is not None:
            update_fields.append("status = ?")
            params.append(status)
        
        if not update_fields:
            return True  # 没有需要更新的字段
        
        params.append(paper_id)
        
        sql = f"""
        UPDATE papers 
        SET {', '.join(update_fields)}
        WHERE paper_id = ?
        """
        
        affected_rows = execute_update(sql, params)
        logger.info(f"管理员更新文献 {paper_id} 信息成功")
        return affected_rows > 0
        
    except Exception as e:
        logger.error(f"管理员更新文献信息失败: {e}")
        raise

def delete_paper_admin(paper_id):
    """
    管理员删除文献（对应API 6.2.3）
    """
    try:
        # 软删除：将状态设置为0
        sql = """
        UPDATE papers 
        SET status = 0
        WHERE paper_id = ?
        """
        
        affected_rows = execute_update(sql, (paper_id,))
        
        if affected_rows > 0:
            # 同时删除相关的批注
            annotation_sql = """
            UPDATE annotations 
            SET status = 0
            WHERE paper_id = ?
            """
            execute_update(annotation_sql, (paper_id,))
            
            logger.info(f"管理员删除文献 {paper_id} 成功")
            return True
        else:
            logger.warning(f"文献 {paper_id} 不存在或已删除")
            return False
        
    except Exception as e:
        logger.error(f"管理员删除文献失败: {e}")
        raise

def restore_paper_admin(paper_id):
    """
    管理员恢复文献（对应API 6.2.4）
    """
    try:
        # 恢复文献：将状态设置为1
        sql = """
        UPDATE papers 
        SET status = 1
        WHERE paper_id = ?
        """
        
        affected_rows = execute_update(sql, (paper_id,))
        
        if affected_rows > 0:
            # 同时恢复相关的批注
            annotation_sql = """
            UPDATE annotations 
            SET status = 1
            WHERE paper_id = ?
            """
            execute_update(annotation_sql, (paper_id,))
            
            logger.info(f"管理员恢复文献 {paper_id} 成功")
            return True
        else:
            logger.warning(f"文献 {paper_id} 不存在")
            return False
        
    except Exception as e:
        logger.error(f"管理员恢复文献失败: {e}")
        raise

def get_admin_paper_statistics():
    """
    获取管理员文献统计信息（对应API 6.4.1）
    """
    try:
        # 总文献数（包括已删除的）
        total_sql = "SELECT COUNT(*) as total FROM papers"
        total_result = execute_query_one(total_sql, ())
        total_papers = total_result['total'] if total_result else 0
        
        # 正常状态文献数
        active_sql = "SELECT COUNT(*) as active FROM papers WHERE status = 1"
        active_result = execute_query_one(active_sql, ())
        active_papers = active_result['active'] if active_result else 0
        
        # 已删除文献数
        deleted_sql = "SELECT COUNT(*) as deleted FROM papers WHERE status = 0"
        deleted_result = execute_query_one(deleted_sql, ())
        deleted_papers = deleted_result['deleted'] if deleted_result else 0
        
        # Papers uploaded this month
        month_sql = """
        SELECT COUNT(*) as this_month
        FROM papers
        WHERE upload_time >= date('now', 'start of month')
        """
        month_result = execute_query_one(month_sql, ())
        papers_this_month = month_result['this_month'] if month_result else 0
        
        # 总批注数
        annotation_sql = "SELECT COUNT(*) as total FROM annotations WHERE status = 1"
        annotation_result = execute_query_one(annotation_sql, ())
        total_annotations = annotation_result['total'] if annotation_result else 0
        
        # AI对话数
        ai_sql = "SELECT COUNT(*) as total FROM ai_conversations WHERE status = 1"
        ai_result = execute_query_one(ai_sql, ())
        ai_conversations = ai_result['total'] if ai_result else 0
        
        # 文件存储统计
        size_sql = "SELECT SUM(file_size) as total_size FROM papers WHERE status = 1"
        size_result = execute_query_one(size_sql, ())
        total_size = size_result['total_size'] if size_result else 0
        
        # 按文献类型统计
        type_sql = """
        SELECT pt.type_name, COUNT(p.paper_id) as count
        FROM publication_types pt
        LEFT JOIN papers p ON pt.type_id = p.publication_type_id AND p.status = 1
        GROUP BY pt.type_id, pt.type_name
        ORDER BY count DESC
        """
        type_results = execute_query(type_sql, ())
        paper_types = [dict(result) for result in type_results]
        
        # 最活跃用户统计
        user_sql = """
        SELECT u.username, COUNT(p.paper_id) as paper_count, 
               COUNT(a.annotation_id) as annotation_count
        FROM users u
        LEFT JOIN papers p ON u.user_id = p.upload_user_id AND p.status = 1
        LEFT JOIN annotations a ON u.user_id = a.user_id AND a.status = 1
        WHERE u.status = 1
        GROUP BY u.user_id, u.username
        HAVING paper_count > 0 OR annotation_count > 0
        ORDER BY paper_count DESC, annotation_count DESC
        LIMIT 10
        """
        user_results = execute_query(user_sql, ())
        active_users = [dict(result) for result in user_results]
        
        logger.info("获取管理员统计信息成功")
        return {
            'total_papers': total_papers,
            'active_papers': active_papers,
            'deleted_papers': deleted_papers,
            'papers_this_month': papers_this_month,
            'total_annotations': total_annotations,
            'ai_conversations': ai_conversations,
            'disk_usage': f"{total_size / (1024*1024*1024):.2f}GB" if total_size and total_size > 0 else "0GB",
            'paper_types': paper_types,
            'active_users': active_users
        }
        
    except Exception as e:
        logger.error(f"获取管理员统计信息失败: {e}")
        raise 