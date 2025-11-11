#!/usr/bin/env python3
"""
DeepSeek AI客户端
处理与DeepSeek API的交互
"""
import json
import time
import logging
from config import DEEPSEEK_CONFIG

# 使用openai库来调用DeepSeek API
try:
    from openai import OpenAI
except ImportError:
    raise ImportError("请安装openai库: pip install openai")

logger = logging.getLogger(__name__)

class DeepSeekClient:
    """DeepSeek AI客户端类"""
    
    def __init__(self):
        self.api_key = DEEPSEEK_CONFIG['api_key']
        self.base_url = DEEPSEEK_CONFIG['base_url']
        self.model = DEEPSEEK_CONFIG['model']
        self.timeout = DEEPSEEK_CONFIG['timeout']
        
        # 初始化OpenAI客户端
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
    def ask_question(self, question, context="", conversation_history=None):
        """
        问答函数 - 根据DeepSeek官方文档实现多轮对话
        
        Args:
            question: 用户问题
            context: 上下文（如文献内容）
            conversation_history: 对话历史
        
        Returns:
            AI回答
        """
        return self.ask_question_with_model(question, context, conversation_history, model=self.model)
    
    def ask_question_with_model(self, question, context="", conversation_history=None, model="deepseek-chat"):
        """
        问答函数 - 支持模型选择
        
        Args:
            question: 用户问题
            context: 上下文（如文献内容）
            conversation_history: 对话历史
            model: 模型名称 (deepseek-chat 或 deepseek-reasoner)
        
        Returns:
            AI回答
        """
        try:
            # 构建消息列表
            messages = self.build_messages(question, context, conversation_history, model)
            
            logger.info(f"发送DeepSeek API请求，模型: {model}，消息数量: {len(messages)}")
            
            # 设置请求参数
            request_params = {
                'model': model,
                'messages': messages,
                'temperature': 0.7,
                'max_tokens': 2048 if model == 'deepseek-chat' else 8192
            }
            
            # 如果是推理模型，删除不支持的参数
            if model == 'deepseek-reasoner':
                request_params.pop('temperature', None)
                request_params['max_tokens'] = 32768  # 推理模型支持更大的输出
            
            # 使用OpenAI客户端发送请求
            response = self.client.chat.completions.create(**request_params)
            
            # 解析响应
            answer = response.choices[0].message.content
            reasoning_content = getattr(response.choices[0].message, 'reasoning_content', None)
            tokens_used = response.usage.total_tokens if response.usage else 0
            
            logger.info(f"DeepSeek API响应成功，使用token: {tokens_used}")
            
            result = {
                'answer': answer,
                'tokens_used': tokens_used,
                'model': model
            }
            
            # 如果是推理模型，添加推理过程
            if reasoning_content:
                result['reasoning_content'] = reasoning_content
            
            return result
            
        except Exception as e:
            logger.error(f"DeepSeek API请求失败: {str(e)}")
            raise Exception(f"AI问答失败: {str(e)}")
    
    def translate_text(self, text, target_language='zh', source_language='auto'):
        """
        翻译文本 - 使用deepseek-chat模型快速翻译
        
        Args:
            text: 待翻译文本
            target_language: 目标语言 (zh/en)
            source_language: 源语言 (auto自动检测)
        
        Returns:
            翻译结果
        """
        try:
            # 构建翻译提示
            if target_language == 'zh':
                prompt = f"请将以下文本翻译成中文，保持原文的专业性和准确性：\n\n{text}"
            elif target_language == 'en':
                prompt = f"Please translate the following text to English, maintaining professionalism and accuracy:\n\n{text}"
            else:
                prompt = f"请将以下文本翻译成{target_language}：\n\n{text}"
            
            messages = [
                {
                    'role': 'system',
                    'content': '你是一个专业的翻译助手，擅长学术文献和技术文档的翻译。请保持翻译的准确性和专业性。'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
            
            response = self.client.chat.completions.create(
                model='deepseek-chat',  # 使用快速模型进行翻译
                messages=messages,
                temperature=0.3,  # 较低温度确保翻译稳定
                max_tokens=2048
            )
            
            translation = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else 0
            
            logger.info(f"翻译成功，使用token: {tokens_used}")
            
            return {
                'translation': translation,
                'original': text,
                'target_language': target_language,
                'source_language': source_language,
                'tokens_used': tokens_used,
                'model': 'deepseek-chat'
            }
            
        except Exception as e:
            logger.error(f"翻译失败: {str(e)}")
            raise Exception(f"翻译失败: {str(e)}")
    
    def build_messages(self, question, context="", conversation_history=None, model="deepseek-chat"):
        """
        构建消息列表（支持多轮对话）- 按照DeepSeek官方文档格式
        
        Args:
            question: 当前问题
            context: 上下文
            conversation_history: 对话历史
            model: 模型名称
        
        Returns:
            消息列表
        """
        messages = []
        
        # 根据模型类型构建不同的系统消息
        if model == 'deepseek-reasoner':
            system_prompt = """You are a professional research assistant specialized in helping users deeply understand and analyze academic literature.
Please carefully consider the user's question, conduct in-depth reasoning and analysis, and provide accurate and comprehensive answers.
If the question involves specific literature content, please cite relevant passages and provide detailed explanations and analysis.
If the question requires reasoning or calculation, please show your thought process.
Always respond in English."""
        else:
            system_prompt = """You are a professional research assistant specialized in helping users understand and analyze academic literature.
Based on the provided literature content and user questions, please provide accurate and professional answers.
If the question involves specific literature content, please cite relevant passages and provide explanations.
If the question is beyond the scope of the literature, please state it honestly.
Always respond in English."""

        if context:
            system_prompt += f"\n\nCurrent literature context:\n{context}"
        
        messages.append({
            'role': 'system',
            'content': system_prompt
        })
        
        # 添加历史对话 - 按照DeepSeek文档的格式
        if conversation_history:
            for item in conversation_history:
                if item.get('question'):
                    messages.append({
                        'role': 'user',
                        'content': item['question']
                    })
                if item.get('answer'):
                    messages.append({
                        'role': 'assistant',
                        'content': item['answer']
                    })
        
        # 添加当前问题
        messages.append({
            'role': 'user',
            'content': question
        })
        
        logger.info(f"构建消息列表完成，模型: {model}，共{len(messages)}条消息")
        return messages
    
    def get_paper_summary(self, paper_content, max_length=500):
        """
        获取文献摘要
        
        Args:
            paper_content: 文献内容
            max_length: 摘要最大长度
            
        Returns:
            文献摘要
        """
        try:
            prompt = f"""Please generate a concise summary (no more than {max_length} characters) for the following literature content:

{paper_content[:2000]}

The summary should include:
1. Main research objectives and questions
2. Methods used
3. Main findings and conclusions
4. Research significance and value

Please summarize in clear and concise language in English."""

            messages = [
                {
                    'role': 'system',
                    'content': 'You are a professional academic summary generation assistant. Always respond in English.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1024
            )
            
            summary = response.choices[0].message.content
            logger.info("生成文献摘要成功")
            return summary
            
        except Exception as e:
            logger.error(f"生成摘要失败: {str(e)}")
            return f"生成摘要失败: {str(e)}"
    
    def get_paper_keywords(self, paper_content, num_keywords=8):
        """
        提取文献关键词
        
        Args:
            paper_content: 文献内容
            num_keywords: 关键词数量
            
        Returns:
            关键词列表
        """
        try:
            prompt = f"""Please extract {num_keywords} most important keywords from the following literature content:

{paper_content[:1500]}

Please return a keyword list separated by commas. Keywords should be professional terms that accurately summarize the main content of the literature."""

            messages = [
                {
                    'role': 'system',
                    'content': 'You are a professional keyword extraction assistant. Always respond in English.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=512
            )
            
            keywords_text = response.choices[0].message.content
            
            # 解析关键词
            keywords = [kw.strip() for kw in keywords_text.split(',')]
            logger.info(f"提取关键词成功，共{len(keywords)}个")
            return keywords[:num_keywords]
            
        except Exception as e:
            logger.error(f"提取关键词失败: {str(e)}")
            return [f"提取关键词失败: {str(e)}"]
    
    def translate_abstract(self, abstract, target_language='zh'):
        """
        翻译摘要
        
        Args:
            abstract: 原文摘要
            target_language: 目标语言（zh: 中文, en: 英文）
            
        Returns:
            翻译后的摘要
        """
        try:
            lang_name = '中文' if target_language == 'zh' else '英文'
            prompt = f"请将以下摘要翻译成{lang_name}，保持学术性和准确性：\n\n{abstract}"
            
            messages = [
                {
                    'role': 'system',
                    'content': f'你是一个专业的学术翻译助手，专门翻译学术文献。'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1024
            )
            
            translation = response.choices[0].message.content
            logger.info("翻译成功")
            return translation
            
        except Exception as e:
            logger.error(f"翻译失败: {str(e)}")
            return f"翻译失败: {str(e)}"
    
    def get_paper_key_insights(self, full_text):
        """
        基于PDF全文生成文章核心看点
        
        Args:
            full_text: PDF全文内容
            
        Returns:
            核心看点内容
        """
        try:
            prompt = f"""Based on the full text of the following academic literature, extract and generate the key insights of the article.

Full text content:
{full_text[:8000]}  # Limit length to avoid exceeding token limit

Please generate a key insights analysis covering the following aspects:
1. Main innovations and contributions
2. Highlights of research methods
3. Key findings from experimental results
4. Theoretical or practical significance
5. Technical advantages and breakthroughs

Requirements:
- Express in clear and concise English
- Highlight the core value and innovation of the article
- Each insight should have substantial content, avoiding empty descriptions
- Keep the overall length between 300-500 words

Please output the key insights content directly without additional format markers."""

            messages = [
                {
                    'role': 'system',
                    'content': 'You are a professional academic analyst skilled at extracting core viewpoints and innovative highlights from academic literature. Always respond in English.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
            
            response = self.client.chat.completions.create(
                model='deepseek-reasoner',  # 使用推理模型进行深度分析
                messages=messages,
                max_tokens=2048
            )
            
            insights = response.choices[0].message.content
            logger.info("核心看点生成成功")
            return insights
            
        except Exception as e:
            logger.error(f"核心看点生成失败: {str(e)}")
            return f"核心看点生成失败: {str(e)}"
    
    def get_related_work_description(self, full_text):
        """
        基于PDF全文生成Related Work风格的描述
        
        Args:
            full_text: PDF全文内容
            
        Returns:
            包含中英文描述的字典
        """
        try:
            prompt = f"""Based on the full text of the following academic literature, generate a research-style Related Work description.

Full text content:
{full_text[:8000]}  # Limit length to avoid exceeding token limit

Requirements:
1. The description should conform to the writing style of the Related Work section in academic papers
2. Format: XXX used XXX method/technique to study/solve XXX problem, achieving XXX effect/result
3. Should reflect the core method, problem solved, and main achievements of the research
4. Provide both Chinese and English versions
5. Language should be professional, accurate, and concise

Please output in the following JSON format:
{{
    "chinese_description": "Chinese description...",
    "english_description": "English description..."
}}

Ensure the output is valid JSON format."""

            messages = [
                {
                    'role': 'system',
                    'content': 'You are a professional academic writing assistant specialized in generating high-quality Related Work descriptions. Always respond in valid JSON format.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
            
            response = self.client.chat.completions.create(
                model='deepseek-reasoner',  # 使用推理模型进行深度分析
                messages=messages,
                max_tokens=4096  # 增加 max_tokens 以确保完整输出
            )
            
            result = response.choices[0].message.content

            # 尝试解析JSON
            try:
                import json
                import re

                logger.info(f"Related Work原始响应长度: {len(result)}")
                logger.info(f"Related Work原始响应前500字符: {result[:500]}")

                # 尝试多种JSON提取方式
                json_text = None

                # 1. 从```json代码块中提取
                json_match = re.search(r'```json\s*(.*?)\s*```', result, re.DOTALL)
                if json_match:
                    json_text = json_match.group(1)
                    logger.info("从```json代码块中提取JSON")
                # 2. 从```代码块中提取
                elif re.search(r'```\s*(.*?)\s*```', result, re.DOTALL):
                    json_match = re.search(r'```\s*(.*?)\s*```', result, re.DOTALL)
                    json_text = json_match.group(1)
                    logger.info("从```代码块中提取JSON")
                # 3. 直接解析（如果以{开头）
                elif result.strip().startswith('{'):
                    json_text = result.strip()
                    logger.info("直接解析JSON")
                # 4. 查找第一个{到最后一个}之间的内容
                else:
                    first_brace = result.find('{')
                    last_brace = result.rfind('}')
                    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                        json_text = result[first_brace:last_brace+1]
                        logger.info("从文本中提取JSON对象")

                if json_text:
                    parsed_result = json.loads(json_text)
                    logger.info("Related Work描述生成成功（JSON解析）")

                    # 确保返回的字段名正确
                    return {
                        'description': parsed_result.get('english_description', parsed_result.get('description', '')),
                        'chinese_description': parsed_result.get('chinese_description', ''),
                        'english_description': parsed_result.get('english_description', parsed_result.get('description', ''))
                    }
                else:
                    raise json.JSONDecodeError("No JSON found", result, 0)

            except json.JSONDecodeError as e:
                # 如果解析失败，使用文本解析
                logger.info(f"AI返回非JSON格式，使用文本解析: {e}")
                print(f"ℹ️  AI返回非JSON格式，使用文本解析（这是正常的）")

                # 尝试从文本中提取描述
                lines = result.split('\n')
                chinese_desc = ""
                english_desc = ""

                for i, line in enumerate(lines):
                    line_lower = line.lower()
                    if 'chinese' in line_lower or '中文' in line_lower:
                        # 下一行可能是中文描述
                        if i + 1 < len(lines):
                            chinese_desc = lines[i + 1].strip()
                    elif 'english' in line_lower or '英文' in line_lower:
                        # 下一行可能是英文描述
                        if i + 1 < len(lines):
                            english_desc = lines[i + 1].strip()

                # 如果没有找到，使用整个文本作为描述
                if not english_desc:
                    english_desc = result[:500] if len(result) > 500 else result

                logger.info("Related Work描述生成成功（文本解析）")
                return {
                    'description': english_desc,
                    'chinese_description': chinese_desc,
                    'english_description': english_desc
                }
            
        except Exception as e:
            logger.error(f"Related Work描述生成失败: {str(e)}")
            return {
                'chinese_description': f"Related Work描述生成失败: {str(e)}",
                'english_description': f"Related work description generation failed: {str(e)}"
            }

# 创建全局客户端实例
deepseek_client = DeepSeekClient()

# 便捷函数
def ask_ai_question(question, context="", conversation_history=None):
    """便捷的AI问答函数"""
    return deepseek_client.ask_question(question, context, conversation_history)

def get_ai_summary(paper_content, max_length=500):
    """便捷的摘要生成函数"""
    return deepseek_client.get_paper_summary(paper_content, max_length)

def get_ai_keywords(paper_content, num_keywords=8):
    """便捷的关键词提取函数"""
    return deepseek_client.get_paper_keywords(paper_content, num_keywords)

def translate_ai_text(text, target_language='zh', source_language='auto'):
    """便捷的翻译函数"""
    return deepseek_client.translate_text(text, target_language, source_language)

def ask_ai_question_with_model(question, context="", conversation_history=None, model="deepseek-chat"):
    """便捷的AI问答函数 - 支持模型选择"""
    return deepseek_client.ask_question_with_model(question, context, conversation_history, model)

def get_ai_key_insights(full_text):
    """便捷的核心看点生成函数"""
    return deepseek_client.get_paper_key_insights(full_text)

def get_ai_related_work(full_text):
    """便捷的Related Work描述生成函数"""
    return deepseek_client.get_related_work_description(full_text) 