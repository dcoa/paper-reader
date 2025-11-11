#!/usr/bin/env python3
"""
AI对话模型
处理AI对话相关的数据操作
"""
import logging
from datetime import datetime
from .database import execute_query_one, execute_query, execute_insert, execute_update

logger = logging.getLogger(__name__)

class AIConversation:
    """AI对话模型类"""
    
    def __init__(self, conversation_id=None, paper_id=None, user_id=None, question=None,
                 answer=None, context=None, model='deepseek-chat', create_time=None, status=1):
        self.conversation_id = conversation_id
        self.paper_id = paper_id
        self.user_id = user_id
        self.question = question
        self.answer = answer
        self.context = context
        self.model = model
        self.create_time = create_time
        self.status = status
    
    def to_dict(self):
        """转换为字典"""
        return {
            'conversation_id': self.conversation_id,
            'paper_id': self.paper_id,
            'user_id': self.user_id,
            'question': self.question,
            'answer': self.answer,
            'context': self.context,
            'model': self.model,
            'create_time': self.create_time.isoformat() if self.create_time else None,
            'status': self.status
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建AI对话对象"""
        return cls(
            conversation_id=data.get('conversation_id'),
            paper_id=data.get('paper_id'),
            user_id=data.get('user_id'),
            question=data.get('question'),
            answer=data.get('answer'),
            context=data.get('context'),
            model=data.get('model', 'deepseek-chat'),
            create_time=data.get('create_time'),
            status=data.get('status', 1)
        )

def create_conversation(user_id, question, answer, paper_id=None, context=None, 
                       model='deepseek-chat', tokens_used=0, conversation_id=None):
    """
    创建对话记录函数（对应API 4.1）
    """
    try:
        sql = """
        INSERT INTO ai_conversations (paper_id, user_id, question, answer, context, 
                                    model, create_time, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (paper_id, user_id, question, answer, context, model, 
                 datetime.now(), 1)
        
        new_conversation_id = execute_insert(sql, params)
        logger.info(f"创建AI对话记录成功，对话ID: {new_conversation_id}")
        
        # 返回创建的对话信息
        created_conversation = get_conversation_by_id(new_conversation_id)
        created_conversation['conversation_id'] = new_conversation_id
        created_conversation['create_time'] = datetime.now().isoformat()
        
        return created_conversation
        
    except Exception as e:
        logger.error(f"创建AI对话记录失败: {e}")
        raise

def get_conversation_history(conversation_id, user_id=None, limit=10):
    """
    获取对话历史函数（对应API 4.2）
    基于conversation_id获取对话历史（实际这里简化为单轮对话）
    """
    try:
        # 构建查询条件
        where_conditions = ["ac.status = 1", "ac.conversation_id = ?"]
        params = [conversation_id]
        
        if user_id:
            where_conditions.append("ac.user_id = ?")
            params.append(user_id)
        
        where_clause = " AND ".join(where_conditions)
        
        sql = f"""
        SELECT ac.conversation_id, ac.paper_id, ac.user_id, ac.question, ac.answer,
               ac.context, ac.model, ac.create_time,
               p.title as paper_title, u.username
        FROM ai_conversations ac
        LEFT JOIN papers p ON ac.paper_id = p.paper_id
        LEFT JOIN users u ON ac.user_id = u.user_id
        WHERE {where_clause}
        ORDER BY ac.create_time DESC
        LIMIT ?
        """
        params.append(limit)
        
        results = execute_query(sql, params)
        
        conversations = []
        for result in results:
            conversation_data = {
                'conversation_id': result['conversation_id'],
                'paper_id': result['paper_id'],
                'paper_title': result['paper_title'],
                'user_id': result['user_id'],
                'username': result['username'],
                'question': result['question'],
                'answer': result['answer'],
                'context': result['context'],
                'model': result['model'],
                'create_time': result['create_time'].isoformat() if result['create_time'] else None
            }
            conversations.append(conversation_data)
        
        logger.info(f"查询对话历史成功，返回 {len(conversations)} 条记录")
        return conversations
        
    except Exception as e:
        logger.error(f"查询对话历史失败: {e}")
        raise

def get_user_conversations(user_id, page=1, limit=10, paper_id=None):
    """
    获取用户的所有对话
    """
    try:
        # 计算偏移量
        offset = (page - 1) * limit
        
        # 构建查询条件
        where_conditions = ["ac.user_id = ?", "ac.status = 1"]
        params = [user_id]
        
        if paper_id:
            where_conditions.append("ac.paper_id = ?")
            params.append(paper_id)
        
        where_clause = " AND ".join(where_conditions)
        
        sql = f"""
        SELECT ac.conversation_id, ac.paper_id, ac.question, ac.answer,
               ac.context, ac.model, ac.create_time,
               p.title as paper_title
        FROM ai_conversations ac
        LEFT JOIN papers p ON ac.paper_id = p.paper_id
        WHERE {where_clause}
        ORDER BY ac.create_time DESC
        LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])
        
        results = execute_query(sql, params)
        
        # 获取总数
        count_sql = f"""
        SELECT COUNT(*) as total
        FROM ai_conversations ac
        WHERE {where_clause}
        """
        count_params = params[:-2]  # 去掉 limit 和 offset
        count_result = execute_query_one(count_sql, count_params)
        total = count_result['total'] if count_result else 0
        
        conversations = []
        for result in results:
            conversation_data = {
                'conversation_id': result['conversation_id'],
                'paper_id': result['paper_id'],
                'paper_title': result['paper_title'],
                'question': result['question'],
                'answer': result['answer'],
                'context': result['context'],
                'model': result['model'],
                'create_time': result['create_time'].isoformat() if result['create_time'] else None
            }
            conversations.append(conversation_data)
        
        logger.info(f"查询用户 {user_id} 对话成功，返回 {len(conversations)} 条记录，总数: {total}")
        return {
            'conversations': conversations,
            'total': total,
            'page': page,
            'limit': limit
        }
        
    except Exception as e:
        logger.error(f"查询用户对话失败: {e}")
        raise

def get_user_conversations_count(user_id):
    """
    获取用户对话数量
    """
    try:
        sql = """
        SELECT COUNT(*) as total
        FROM ai_conversations
        WHERE user_id = ? AND status = 1
        """
        result = execute_query_one(sql, (user_id,))
        return result['total'] if result else 0
        
    except Exception as e:
        logger.error(f"获取用户对话数量失败: {e}")
        return 0

def get_conversation_by_id(conversation_id):
    """
    根据ID获取对话记录
    """
    try:
        sql = """
        SELECT ac.conversation_id, ac.paper_id, ac.user_id, ac.question, ac.answer,
               ac.context, ac.model, ac.create_time, ac.status,
               p.title as paper_title, u.username
        FROM ai_conversations ac
        LEFT JOIN papers p ON ac.paper_id = p.paper_id
        LEFT JOIN users u ON ac.user_id = u.user_id
        WHERE ac.conversation_id = ? AND ac.status = 1
        """
        result = execute_query_one(sql, (conversation_id,))
        
        if result:
            conversation_data = {
                'conversation_id': result['conversation_id'],
                'paper_id': result['paper_id'],
                'paper_title': result['paper_title'],
                'user_id': result['user_id'],
                'username': result['username'],
                'question': result['question'],
                'answer': result['answer'],
                'context': result['context'],
                'model': result['model'],
                'create_time': result['create_time'].isoformat() if result['create_time'] else None
            }
            logger.info(f"查询对话记录成功: {conversation_id}")
            return conversation_data
        else:
            logger.info(f"对话记录不存在: {conversation_id}")
            return None
            
    except Exception as e:
        logger.error(f"查询对话记录失败: {e}")
        raise

def get_paper_conversation_history(paper_id, limit=10):
    """
    获取特定文献的AI对话历史（对应API 4.2）
    """
    try:
        return get_conversation_history(paper_id=paper_id, limit=limit)
    except Exception as e:
        logger.error(f"获取文献对话历史失败: {e}")
        raise

def get_user_conversation_history(user_id, page=1, limit=10):
    """
    获取用户的AI对话历史
    """
    try:
        # 计算偏移量
        offset = (page - 1) * limit
        
        sql = """
        SELECT ac.conversation_id, ac.paper_id, ac.question, ac.answer,
               ac.context, ac.model, ac.create_time,
               p.title as paper_title
        FROM ai_conversations ac
        LEFT JOIN papers p ON ac.paper_id = p.paper_id
        WHERE ac.user_id = ? AND ac.status = 1
        ORDER BY ac.create_time DESC
        LIMIT ? OFFSET ?
        """
        params = [user_id, limit, offset]
        
        results = execute_query(sql, params)
        
        # 获取总数
        count_sql = """
        SELECT COUNT(*) as total
        FROM ai_conversations ac
        WHERE ac.user_id = ? AND ac.status = 1
        """
        count_result = execute_query_one(count_sql, (user_id,))
        total = count_result['total'] if count_result else 0
        
        conversations = []
        for result in results:
            conversation_data = {
                'conversation_id': result['conversation_id'],
                'paper_id': result['paper_id'],
                'paper_title': result['paper_title'],
                'question': result['question'],
                'answer': result['answer'],
                'context': result['context'],
                'model': result['model'],
                'create_time': result['create_time'].isoformat() if result['create_time'] else None
            }
            conversations.append(conversation_data)
        
        logger.info(f"查询用户 {user_id} 对话历史成功，返回 {len(conversations)} 条记录，总数: {total}")
        return {
            'conversations': conversations,
            'total': total,
            'page': page,
            'limit': limit
        }
        
    except Exception as e:
        logger.error(f"查询用户对话历史失败: {e}")
        raise

def delete_conversation(conversation_id, user_id=None):
    """
    删除对话记录（软删除）
    只能删除自己的对话
    """
    try:
        # 如果指定了user_id，检查是否是本人的对话
        if user_id:
            sql_check = """
            SELECT user_id FROM ai_conversations 
            WHERE conversation_id = ? AND status = 1
            """
            result = execute_query_one(sql_check, (conversation_id,))
            
            if not result:
                logger.warning(f"对话记录不存在: {conversation_id}")
                return False
            
            if result['user_id'] != user_id:
                logger.warning(f"用户 {user_id} 无权删除对话记录 {conversation_id}")
                return False
        
        # 软删除对话记录
        sql = "UPDATE ai_conversations SET status = 0 WHERE conversation_id = ?"
        affected_rows = execute_update(sql, (conversation_id,))
        
        logger.info(f"删除对话记录 {conversation_id} 成功")
        return affected_rows > 0
        
    except Exception as e:
        logger.error(f"删除对话记录失败: {e}")
        raise

def search_conversations(keyword, user_id=None, page=1, limit=10):
    """
    搜索对话记录
    """
    try:
        # 计算偏移量
        offset = (page - 1) * limit
        
        # 构建查询条件
        where_conditions = ["ac.status = 1"]
        where_conditions.append("(ac.question LIKE ? OR ac.answer LIKE ?)")
        params = [f"%{keyword}%", f"%{keyword}%"]
        
        if user_id:
            where_conditions.append("ac.user_id = ?")
            params.append(user_id)
        
        where_clause = " AND ".join(where_conditions)
        
        sql = f"""
        SELECT ac.conversation_id, ac.paper_id, ac.question, ac.answer,
               ac.context, ac.model, ac.create_time,
               p.title as paper_title, u.username
        FROM ai_conversations ac
        LEFT JOIN papers p ON ac.paper_id = p.paper_id
        LEFT JOIN users u ON ac.user_id = u.user_id
        WHERE {where_clause}
        ORDER BY ac.create_time DESC
        LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])
        
        results = execute_query(sql, params)
        
        # 获取总数
        count_sql = f"""
        SELECT COUNT(*) as total
        FROM ai_conversations ac
        WHERE {where_clause}
        """
        count_params = params[:-2]  # 去掉 limit 和 offset
        count_result = execute_query_one(count_sql, count_params)
        total = count_result['total'] if count_result else 0
        
        conversations = []
        for result in results:
            conversation_data = {
                'conversation_id': result['conversation_id'],
                'paper_id': result['paper_id'],
                'paper_title': result['paper_title'],
                'username': result['username'],
                'question': result['question'],
                'answer': result['answer'],
                'context': result['context'],
                'model': result['model'],
                'create_time': result['create_time'].isoformat() if result['create_time'] else None
            }
            conversations.append(conversation_data)
        
        logger.info(f"搜索对话记录成功，关键词: {keyword}，返回 {len(conversations)} 条记录，总数: {total}")
        return {
            'conversations': conversations,
            'total': total,
            'page': page,
            'limit': limit,
            'keyword': keyword
        }
        
    except Exception as e:
        logger.error(f"搜索对话记录失败: {e}")
        raise

def get_conversation_statistics():
    """
    获取对话统计信息
    """
    try:
        # 总对话数
        total_sql = "SELECT COUNT(*) as total FROM ai_conversations WHERE status = 1"
        total_result = execute_query_one(total_sql)
        total_conversations = total_result['total'] if total_result else 0
        
        # 按用户统计
        user_sql = """
        SELECT u.username, COUNT(ac.conversation_id) as count
        FROM users u
        LEFT JOIN ai_conversations ac ON u.user_id = ac.user_id AND ac.status = 1
        GROUP BY u.user_id, u.username
        HAVING count > 0
        ORDER BY count DESC
        LIMIT 10
        """
        user_results = execute_query(user_sql)
        
        # 按文献统计
        paper_sql = """
        SELECT p.title, COUNT(ac.conversation_id) as count
        FROM papers p
        LEFT JOIN ai_conversations ac ON p.paper_id = ac.paper_id AND ac.status = 1
        GROUP BY p.paper_id, p.title
        HAVING count > 0
        ORDER BY count DESC
        LIMIT 10
        """
        paper_results = execute_query(paper_sql)
        
        # 按模型统计
        model_sql = """
        SELECT model, COUNT(*) as count
        FROM ai_conversations
        WHERE status = 1
        GROUP BY model
        ORDER BY count DESC
        """
        model_results = execute_query(model_sql)
        
        # 按日期统计（最近7天）
        date_sql = """
        SELECT DATE(create_time) as date, COUNT(*) as count
        FROM ai_conversations
        WHERE status = 1 AND create_time >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        GROUP BY DATE(create_time)
        ORDER BY date DESC
        """
        date_results = execute_query(date_sql)
        
        statistics = {
            'total_conversations': total_conversations,
            'by_user': [dict(result) for result in user_results],
            'by_paper': [dict(result) for result in paper_results],
            'by_model': [dict(result) for result in model_results],
            'by_date': [dict(result) for result in date_results]
        }
        
        logger.info(f"获取对话统计信息成功，总对话数: {total_conversations}")
        return statistics
        
    except Exception as e:
        logger.error(f"获取对话统计信息失败: {e}")
        raise

def build_conversation_context(paper_id=None, user_id=None, limit=5):
    """
    构建对话上下文（用于多轮对话）
    """
    try:
        # 获取最近的对话记录作为上下文
        recent_conversations = get_conversation_history(
            paper_id=paper_id, 
            user_id=user_id, 
            limit=limit
        )
        
        context_messages = []
        for conv in reversed(recent_conversations):  # 按时间正序
            context_messages.extend(conv['messages'])
        
        logger.info(f"构建对话上下文成功，包含 {len(context_messages)} 条消息")
        return context_messages
        
    except Exception as e:
        logger.error(f"构建对话上下文失败: {e}")
        raise 