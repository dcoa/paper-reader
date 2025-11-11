#!/usr/bin/env python3
"""
AI问答路由
处理AI问答相关的API请求
"""
from flask import Blueprint, request
from models.ai_conversation import (
    create_conversation, get_conversation_history,
    get_user_conversations, get_conversation_by_id
)
from models.paper import get_paper_by_id
from utils.auth import token_required, get_user_from_request
from utils.response import success_response, error_response, validation_error_response
from utils.deepseek_client import ask_ai_question, ask_ai_question_with_model, translate_ai_text, get_ai_key_insights, get_ai_related_work
from utils.pdf_analyzer import PDFAnalyzer

# 创建蓝图
ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/ask', methods=['POST'])
@token_required
def ask_ai(current_user):
    """
    AI问答路由函数（对应API 4.1）
    POST /api/ai/ask
    """
    try:
        # 当前用户已通过装饰器传递
        
        # 获取请求数据
        data = request.get_json()
        if not data:
            return validation_error_response("请求数据格式错误")
        
        question = data.get('question')
        paper_id = data.get('paper_id')
        context = data.get('context', '')
        conversation_id = data.get('conversation_id')
        model = data.get('model', 'deepseek-chat')  # Model selection

        # Parameter validation
        if not question:
            return validation_error_response("Question cannot be empty")

        # Validate model type
        supported_models = ['deepseek-chat', 'deepseek-reasoner']
        if model not in supported_models:
            return validation_error_response(f"Unsupported model type. Supported: {', '.join(supported_models)}")
        
        # 获取文献内容作为上下文
        paper_context = ""
        if paper_id:
            paper = get_paper_by_id(paper_id)
            if paper:
                paper_context = f"文献标题: {paper['title']}\n"
                paper_context += f"作者: {paper['authors']}\n"
                if paper.get('abstract'):
                    paper_context += f"摘要: {paper['abstract']}\n"
                if paper.get('keywords'):
                    paper_context += f"关键词: {paper['keywords']}\n"
                # 可以在这里添加文献文本内容的提取逻辑
        
        # Merge context
        full_context = paper_context + "\n" + context if context else paper_context

        # Get conversation history
        conversation_history = []
        if conversation_id:
            # Get conversation history
            history = get_conversation_history(conversation_id, current_user.user_id)
            conversation_history = [
                {
                    'question': item['question'],
                    'answer': item['answer']
                }
                for item in history
            ]

        # Call AI Q&A - Support model selection
        ai_response = ask_ai_question_with_model(
            question=question,
            context=full_context,
            conversation_history=conversation_history,
            model=model
        )
        
        # 保存对话记录
        conversation = create_conversation(
            user_id=current_user.user_id,
            paper_id=paper_id,
            question=question,
            answer=ai_response['answer'],
            context=full_context,
            tokens_used=ai_response.get('tokens_used', 0),
            model=ai_response.get('model', 'deepseek-chat'),
            conversation_id=conversation_id
        )
        
        if not conversation:
            return error_response(
                error="Failed to save conversation record",
                code=500
            )

        response_data = {
            'conversation_id': conversation['conversation_id'],
            'answer': ai_response['answer'],
            'tokens_used': ai_response.get('tokens_used', 0),
            'model': ai_response.get('model', 'deepseek-chat'),
            'create_time': conversation['create_time']
        }

        # If reasoning model, add reasoning content
        if ai_response.get('reasoning_content'):
            response_data['reasoning_content'] = ai_response['reasoning_content']

        return success_response(
            data=response_data,
            message="AI Q&A successful"
        )

    except Exception as e:
        return error_response(
            error=f"AI Q&A failed: {str(e)}",
            code=500
        )

@ai_bp.route('/history/<int:paper_id>', methods=['GET'])
@token_required
def get_ai_history(paper_id, current_user):
    """
    Get AI conversation history for a paper (API 4.2)
    GET /api/ai/history/{paper_id}
    """
    try:
        # Current user passed through decorator

        # Get all conversations for this paper
        result = get_user_conversations(
            user_id=current_user.user_id,
            page=1,
            limit=50,  # Get last 50 conversations
            paper_id=paper_id
        )

        conversations = result.get('conversations', [])

        return success_response(
            data=conversations,
            message="Conversation history retrieved successfully"
        )

    except Exception as e:
        return error_response(
            error=f"Failed to get conversation history: {str(e)}",
            code=500
        )

@ai_bp.route('/conversation/<int:conversation_id>', methods=['GET'])
@token_required
def get_conversation_history_route(conversation_id, current_user):
    """
    Get detailed history of a specific conversation
    GET /api/ai/conversation/{conversation_id}
    """
    try:
        # Current user passed through decorator

        # Get conversation history
        from models.ai_conversation import get_conversation_history
        history = get_conversation_history(conversation_id, current_user.user_id)

        return success_response(
            data=history,
            message="Conversation history retrieved successfully"
        )

    except Exception as e:
        return error_response(
            error=f"Failed to get conversation history: {str(e)}",
            code=500
        )

@ai_bp.route('/conversations', methods=['GET'])
@token_required
def get_user_conversations_route(current_user):
    """
    Get all user conversations
    GET /api/ai/conversations?page=1&limit=10
    """
    try:
        # Current user passed through decorator

        # Get query parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        paper_id = request.args.get('paper_id')

        # Convert data types
        if paper_id:
            paper_id = int(paper_id)

        # Get user conversations
        result = get_user_conversations(
            user_id=current_user.user_id,
            page=page,
            limit=limit,
            paper_id=paper_id
        )

        return success_response(
            data=result,
            message="User conversations retrieved successfully"
        )

    except ValueError:
        return validation_error_response("Page and limit must be numbers")
    except Exception as e:
        return error_response(
            error=f"Failed to get user conversations: {str(e)}",
            code=500
        )



@ai_bp.route('/summary', methods=['POST'])
@token_required
def generate_summary(current_user):
    """
    Generate paper summary
    POST /api/ai/summary
    """
    try:
        # Current user passed through decorator

        # Get request data
        data = request.get_json()
        if not data:
            return validation_error_response("Invalid request data format")

        paper_id = data.get('paper_id')
        content = data.get('content', '')
        max_length = data.get('max_length', 500)

        # Parameter validation
        if not paper_id and not content:
            return validation_error_response("Paper ID or content cannot be empty")

        # Get paper content
        paper_content = content
        if paper_id:
            paper = get_paper_by_id(paper_id)
            if not paper:
                return error_response(
                    error="Paper not found",
                    code=404
                )

            # Build paper content
            paper_content = f"Title: {paper['title']}\n"
            paper_content += f"Authors: {paper['authors']}\n"
            if paper.get('abstract'):
                paper_content += f"Abstract: {paper['abstract']}\n"
            if paper.get('keywords'):
                paper_content += f"Keywords: {paper['keywords']}\n"
            if content:
                paper_content += f"Additional content: {content}\n"

        # Generate summary
        from utils.deepseek_client import get_ai_summary
        summary = get_ai_summary(paper_content, max_length)

        return success_response(
            data={
                'summary': summary,
                'paper_id': paper_id,
                'max_length': max_length
            },
            message="Summary generated successfully"
        )

    except Exception as e:
        return error_response(
            error=f"Failed to generate summary: {str(e)}",
            code=500
        )

@ai_bp.route('/keywords', methods=['POST'])
@token_required
def extract_keywords(current_user):
    """
    Extract keywords
    POST /api/ai/keywords
    """
    try:
        # Current user passed through decorator

        # Get request data
        data = request.get_json()
        if not data:
            return validation_error_response("Invalid request data format")

        paper_id = data.get('paper_id')
        content = data.get('content', '')
        num_keywords = data.get('num_keywords', 8)

        # Parameter validation
        if not paper_id and not content:
            return validation_error_response("Paper ID or content cannot be empty")

        # Get paper content
        paper_content = content
        if paper_id:
            paper = get_paper_by_id(paper_id)
            if not paper:
                return error_response(
                    error="Paper not found",
                    code=404
                )

            # Build paper content
            paper_content = f"Title: {paper['title']}\n"
            paper_content += f"Authors: {paper['authors']}\n"
            if paper.get('abstract'):
                paper_content += f"Abstract: {paper['abstract']}\n"
            if content:
                paper_content += f"Additional content: {content}\n"

        # Extract keywords
        from utils.deepseek_client import get_ai_keywords
        keywords = get_ai_keywords(paper_content, num_keywords)

        return success_response(
            data={
                'keywords': keywords,
                'paper_id': paper_id,
                'num_keywords': num_keywords
            },
            message="Keywords extracted successfully"
        )

    except Exception as e:
        return error_response(
            error=f"Failed to extract keywords: {str(e)}",
            code=500
        )

@ai_bp.route('/translate', methods=['POST'])
@token_required
def translate_text(current_user):
    """
    Translate text - Using DeepSeek for fast translation
    POST /api/ai/translate
    """
    try:
        # Current user passed through decorator

        # Get request data
        data = request.get_json()
        if not data:
            return validation_error_response("Invalid request data format")

        text = data.get('text')
        target_language = data.get('target_language', 'en')
        source_language = data.get('source_language', 'auto')

        # Parameter validation
        if not text:
            return validation_error_response("Text to translate cannot be empty")

        # Translate text - Using DeepSeek for fast translation
        translation_result = translate_ai_text(text, target_language, source_language)

        return success_response(
            data={
                'original': translation_result['original'],
                'translation': translation_result['translation'],
                'target_language': translation_result['target_language'],
                'source_language': translation_result['source_language'],
                'tokens_used': translation_result.get('tokens_used', 0),
                'model': translation_result.get('model', 'deepseek-chat')
            },
            message="Translation successful"
        )

    except Exception as e:
        return error_response(
            error=f"Translation failed: {str(e)}",
            code=500
        )

@ai_bp.route('/key-insights', methods=['POST'])
@token_required
def generate_key_insights(current_user):
    """
    Generate key insights from paper (based on full PDF text)
    POST /api/ai/key-insights
    """
    try:
        # Current user passed through decorator

        # Get request data
        data = request.get_json()
        if not data:
            return validation_error_response("Invalid request data format")

        paper_id = data.get('paper_id')

        # Parameter validation
        if not paper_id:
            return validation_error_response("Paper ID cannot be empty")

        # Get paper info
        paper = get_paper_by_id(paper_id)
        if not paper:
            return error_response(
                error="Paper not found",
                code=404
            )

        # Get PDF file path
        file_path = paper['file_path']
        if file_path.startswith('uploads/'):
            pdf_path = file_path
        else:
            pdf_path = os.path.join('uploads', file_path)

        # Check if file exists
        import os
        if not os.path.exists(pdf_path):
            return error_response(
                error="PDF file not found",
                code=404
            )

        # Extract full PDF text
        pdf_analyzer = PDFAnalyzer()
        full_text = pdf_analyzer.extract_text_from_pdf(pdf_path)

        if not full_text:
            return error_response(
                error="PDF text extraction failed",
                code=500
            )

        # Generate key insights
        insights = get_ai_key_insights(full_text)

        return success_response(
            data={
                'insights': insights,
                'paper_id': paper_id
            },
            message="Key insights generated successfully"
        )

    except Exception as e:
        return error_response(
            error=f"Failed to generate key insights: {str(e)}",
            code=500
        )

@ai_bp.route('/related-work', methods=['POST'])
@token_required
def generate_related_work(current_user):
    """
    Generate Related Work description (based on full PDF text)
    POST /api/ai/related-work
    """
    try:
        # Current user passed through decorator

        # Get request data
        data = request.get_json()
        if not data:
            return validation_error_response("Invalid request data format")

        paper_id = data.get('paper_id')

        # Parameter validation
        if not paper_id:
            return validation_error_response("Paper ID cannot be empty")

        # Get paper info
        paper = get_paper_by_id(paper_id)
        if not paper:
            return error_response(
                error="Paper not found",
                code=404
            )

        # Get PDF file path
        file_path = paper['file_path']
        if file_path.startswith('uploads/'):
            pdf_path = file_path
        else:
            pdf_path = os.path.join('uploads', file_path)

        # Check if file exists
        import os
        if not os.path.exists(pdf_path):
            return error_response(
                error="PDF file not found",
                code=404
            )

        # Extract full PDF text
        pdf_analyzer = PDFAnalyzer()
        full_text = pdf_analyzer.extract_text_from_pdf(pdf_path)

        if not full_text:
            return error_response(
                error="PDF text extraction failed",
                code=500
            )

        # Generate Related Work description
        related_work_result = get_ai_related_work(full_text)

        return success_response(
            data={
                'description': related_work_result.get('description', ''),
                'chinese_description': related_work_result.get('chinese_description', ''),
                'english_description': related_work_result.get('english_description', ''),
                'paper_id': paper_id
            },
            message="Related work description generated successfully"
        )

    except Exception as e:
        return error_response(
            error=f"Failed to generate related work description: {str(e)}",
            code=500
        )