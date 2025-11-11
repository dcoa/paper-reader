import PyPDF2
import io
import re
import json
from typing import Dict, Optional, Tuple
from utils.deepseek_client import DeepSeekClient
from models.database import execute_query, execute_update
import logging

logger = logging.getLogger(__name__)

class PDFAnalyzer:
    """PDF文献分析器"""
    
    def __init__(self):
        self.deepseek_client = DeepSeekClient()
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """从PDF文件提取文本"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
                
                # 清理文本
                text = self.clean_text(text)
                return text
                
        except Exception as e:
            logger.error(f"PDF文本提取失败: {e}")
            return ""
    
    def clean_text(self, text: str) -> str:
        """清理PDF提取的文本"""
        # 移除多余空行
        text = re.sub(r'\n\s*\n', '\n\n', text)
        # 移除页眉页脚常见模式
        text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
        # 移除非ASCII字符中的控制字符
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        # 合并断行
        text = re.sub(r'([a-z])-\n([a-z])', r'\1\2', text)
        
        return text.strip()
    
    def create_analysis_prompt(self, text: str) -> str:
        """创建分析提示词"""
        prompt = f"""
Please conduct an in-depth analysis of the following academic literature and output structured results in the specified format.

Literature content:
{text[:8000]}  # Limit length to avoid exceeding token limit

Please analyze and output results in JSON format, including the following fields:
1. summary: Literature summary (200-300 words)
2. methodology: Methodology analysis (300-500 words)
3. experiments: Experiment summary (300-500 words)
4. key_findings: Key findings (200-300 words)

Requirements:
- Respond in English
- Focus on technical innovations and experimental validation
- Ensure the output is valid JSON format
- Each field content should be complete and logical

Output format:
```json
{{
    "summary": "Literature summary content...",
    "methodology": "Methodology analysis content...",
    "experiments": "Experiment summary content...",
    "key_findings": "Key findings content..."
}}
```
"""
        return prompt
    
    def analyze_paper(self, paper_id: int, pdf_path: str) -> Dict:
        """分析文献并返回结果"""
        try:
            # 1. 更新状态为处理中
            self.update_analysis_status(paper_id, 'processing')
            
            # 2. 提取PDF文本
            logger.info(f"开始提取PDF文本: {pdf_path}")
            text = self.extract_text_from_pdf(pdf_path)
            
            if not text:
                self.update_analysis_status(paper_id, 'failed')
                raise Exception("PDF文本提取失败")
            
            # 3. 调用AI分析
            logger.info(f"开始AI分析，文本长度: {len(text)}")
            prompt = self.create_analysis_prompt(text)

            response = self.deepseek_client.ask_question_with_model(
                question=prompt,
                context="",
                conversation_history=None,
                model="deepseek-reasoner"
            )
            
            # 检查响应是否有answer字段
            if not response or not response.get('answer'):
                self.update_analysis_status(paper_id, 'failed')
                raise Exception(f"AI分析失败: 响应格式错误")
            
            # 4. 解析AI返回的结果
            ai_response = response['answer']
            logger.info(f"AI分析完成，响应长度: {len(ai_response)}")
            print(f"🤖 AI分析完成，响应长度: {len(ai_response)}")

            # 尝试从回答中提取JSON
            analysis_result = self.parse_ai_response(ai_response)
            print(f"📊 解析结果: summary={len(analysis_result.get('summary', ''))}, methodology={len(analysis_result.get('methodology', ''))}, experiments={len(analysis_result.get('experiments', ''))}, key_findings={len(analysis_result.get('key_findings', ''))}")

            # 5. 保存分析结果
            self.save_analysis_result(paper_id, analysis_result, text)
            print(f"✅ 分析结果已保存")
            
            # 6. 更新状态为完成
            self.update_analysis_status(paper_id, 'completed')
            
            return {
                'success': True,
                'data': analysis_result
            }
            
        except Exception as e:
            logger.error(f"文献分析失败: {e}")
            # 确保在所有异常情况下都更新状态为失败
            try:
                self.update_analysis_status(paper_id, 'failed')
            except Exception as status_error:
                logger.error(f"更新状态失败: {status_error}")
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def parse_ai_response(self, response: str) -> Dict:
        """解析AI返回的结果"""
        try:
            logger.info(f"开始解析AI响应，长度: {len(response)}")
            logger.info(f"响应前500字符: {response[:500]}")

            # 尝试直接解析JSON
            if response.strip().startswith('{'):
                logger.info("检测到JSON格式，直接解析")
                result = json.loads(response)
                logger.info(f"JSON解析成功: {list(result.keys())}")
                return result

            # 从markdown代码块中提取JSON
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                logger.info("从markdown代码块中提取JSON")
                result = json.loads(json_match.group(1))
                logger.info(f"JSON解析成功: {list(result.keys())}")
                return result

            # 从代码块中提取JSON
            json_match = re.search(r'```\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                logger.info("从代码块中提取JSON")
                result = json.loads(json_match.group(1))
                logger.info(f"JSON解析成功: {list(result.keys())}")
                return result

            # 如果无法解析JSON，使用文本解析
            logger.info("AI返回非JSON格式，使用文本解析")
            print("ℹ️  AI返回非JSON格式，使用文本解析（这是正常的）")
            return self.parse_text_response(response)

        except json.JSONDecodeError as e:
            logger.info(f"AI返回非JSON格式: {e}，使用文本解析")
            print(f"ℹ️  AI返回非JSON格式，使用文本解析（这是正常的）")
            return self.parse_text_response(response)
    
    def parse_text_response(self, response: str) -> Dict:
        """解析文本格式的AI响应"""
        result = {
            'summary': '',
            'methodology': '',
            'experiments': '',
            'key_findings': ''
        }

        logger.info("使用文本解析模式")
        print(f"文本解析 - 响应长度: {len(response)}")
        print(f"文本解析 - 前1000字符: {response[:1000]}")

        # 尝试按照标题分割
        lines = response.split('\n')
        current_section = None
        section_content = {
            'summary': [],
            'methodology': [],
            'experiments': [],
            'key_findings': []
        }

        for line in lines:
            line_lower = line.lower()

            # 检测章节标题
            if '摘要' in line_lower or 'summary' in line_lower:
                current_section = 'summary'
                logger.info(f"检测到摘要章节: {line[:50]}")
            elif '方法' in line_lower or 'methodology' in line_lower or 'method' in line_lower:
                current_section = 'methodology'
                logger.info(f"检测到方法章节: {line[:50]}")
            elif '实验' in line_lower or 'experiment' in line_lower:
                current_section = 'experiments'
                logger.info(f"检测到实验章节: {line[:50]}")
            elif '发现' in line_lower or 'finding' in line_lower or 'conclusion' in line_lower:
                current_section = 'key_findings'
                logger.info(f"检测到发现章节: {line[:50]}")
            elif current_section and line.strip():
                # 添加内容到当前章节
                section_content[current_section].append(line.strip())

        # 合并每个章节的内容
        for key in section_content:
            if section_content[key]:
                result[key] = '\n'.join(section_content[key])
                logger.info(f"章节 {key} 内容长度: {len(result[key])}")

        # 如果所有字段都为空，尝试简单分割
        if not any(result.values()):
            logger.warning("所有章节都为空，使用简单分割")
            print("所有章节都为空，使用简单分割")
            sections = response.split('\n\n')
            if len(sections) >= 1:
                result['summary'] = sections[0][:500]
            if len(sections) >= 2:
                result['methodology'] = sections[1][:800]
            if len(sections) >= 3:
                result['experiments'] = sections[2][:800]
            if len(sections) >= 4:
                result['key_findings'] = sections[3][:500]

        logger.info(f"文本解析完成: summary={len(result['summary'])}, methodology={len(result['methodology'])}, experiments={len(result['experiments'])}, key_findings={len(result['key_findings'])}")
        print(f"文本解析完成: summary={len(result['summary'])}, methodology={len(result['methodology'])}, experiments={len(result['experiments'])}, key_findings={len(result['key_findings'])}")

        return result
    
    def save_analysis_result(self, paper_id: int, analysis_result: Dict, full_text: str):
        """保存分析结果到数据库"""
        try:
            from datetime import datetime
            current_time = datetime.now().isoformat()

            # 确保所有字段都有值，避免NULL
            summary = analysis_result.get('summary', '') or ''
            methodology = analysis_result.get('methodology', '') or ''
            experiments = analysis_result.get('experiments', '') or ''
            key_findings = analysis_result.get('key_findings', '') or ''

            # 记录日志用于调试
            logger.info(f"保存分析结果 - paper_id={paper_id}")
            logger.info(f"  summary length: {len(summary)}")
            logger.info(f"  methodology length: {len(methodology)}")
            logger.info(f"  experiments length: {len(experiments)}")
            logger.info(f"  key_findings length: {len(key_findings)}")

            # 添加控制台输出
            print(f"💾 保存分析结果 - paper_id={paper_id}")
            print(f"   summary: {len(summary)} 字符")
            print(f"   methodology: {len(methodology)} 字符")
            print(f"   experiments: {len(experiments)} 字符")
            print(f"   key_findings: {len(key_findings)} 字符")

            # 首先检查是否存在旧记录
            check_sql = "SELECT create_time FROM paper_analysis WHERE paper_id = ?"
            existing = execute_query(check_sql, (paper_id,))
            create_time = existing[0]['create_time'] if existing else current_time

            # SQLite 使用 INSERT OR REPLACE 替代 ON DUPLICATE KEY UPDATE
            sql = """
            INSERT OR REPLACE INTO paper_analysis
            (paper_id, summary, methodology, experiments, key_findings, full_content, analysis_status, model_used, create_time, update_time)
            VALUES (?, ?, ?, ?, ?, ?, 'completed', 'deepseek-reasoner', ?, ?)
            """

            execute_update(sql, (
                paper_id,
                summary,
                methodology,
                experiments,
                key_findings,
                full_text[:10000],  # 限制长度
                create_time,  # 保留原有的 create_time
                current_time  # update_time
            ))

            logger.info(f"分析结果已保存: paper_id={paper_id}")

        except Exception as e:
            logger.error(f"保存分析结果失败: {e}")
            raise
    
    def update_analysis_status(self, paper_id: int, status: str):
        """更新分析状态"""
        try:
            from datetime import datetime
            current_time = datetime.now().isoformat()

            # 首先检查记录是否存在
            check_sql = "SELECT paper_id FROM paper_analysis WHERE paper_id = ?"
            existing = execute_query(check_sql, (paper_id,))

            if existing:
                # 如果存在，只更新状态和时间
                sql = """
                UPDATE paper_analysis
                SET analysis_status = ?, update_time = ?
                WHERE paper_id = ?
                """
                execute_update(sql, (status, current_time, paper_id))
            else:
                # 如果不存在，插入新记录
                sql = """
                INSERT INTO paper_analysis
                (paper_id, analysis_status, create_time, update_time)
                VALUES (?, ?, ?, ?)
                """
                execute_update(sql, (paper_id, status, current_time, current_time))

        except Exception as e:
            logger.error(f"更新分析状态失败: {e}")
    
    def get_analysis_result(self, paper_id: int) -> Optional[Dict]:
        """获取分析结果"""
        try:
            sql = """
            SELECT paper_id, summary, methodology, experiments, key_findings,
                   analysis_status, model_used, create_time, update_time
            FROM paper_analysis
            WHERE paper_id = ?
            """

            result = execute_query(sql, (paper_id,))

            if result:
                row = result[0]
                # 处理时间戳 - 可能是字符串或datetime对象
                create_time = row['create_time']
                update_time = row['update_time']

                if create_time and hasattr(create_time, 'isoformat'):
                    create_time = create_time.isoformat()
                if update_time and hasattr(update_time, 'isoformat'):
                    update_time = update_time.isoformat()

                # 确保所有字段都返回字符串，避免NULL值
                return {
                    'paper_id': row['paper_id'],
                    'summary': row['summary'] or '',
                    'methodology': row['methodology'] or '',
                    'experiments': row['experiments'] or '',
                    'key_findings': row['key_findings'] or '',
                    'analysis_status': row['analysis_status'],
                    'model_used': row['model_used'],
                    'create_time': create_time,
                    'update_time': update_time
                }

            return None

        except Exception as e:
            logger.error(f"获取分析结果失败: {e}")
            return None