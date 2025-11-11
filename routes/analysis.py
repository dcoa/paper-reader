from flask import Blueprint, request, jsonify
from utils.auth import token_required
from utils.response import success_response, error_response
from utils.pdf_analyzer import PDFAnalyzer
from models.paper import get_paper_by_id
import os
import logging
import threading

# 创建蓝图
analysis_bp = Blueprint('analysis', __name__)

# 日志配置
logger = logging.getLogger(__name__)

# 创建PDF分析器实例
pdf_analyzer = PDFAnalyzer()

@analysis_bp.route('/<int:paper_id>/analysis', methods=['GET'])
@token_required
def get_paper_analysis(paper_id, current_user):
    """获取文献分析结果"""
    try:
        # 检查文献是否存在
        paper = get_paper_by_id(paper_id)
        if not paper:
            return error_response("文献不存在", 404)
        
        # 获取分析结果
        analysis_result = pdf_analyzer.get_analysis_result(paper_id)
        
        if not analysis_result:
            return error_response("暂无分析结果", 404)
        
        return success_response(analysis_result)
        
    except Exception as e:
        logger.error(f"获取文献分析失败: {e}")
        return error_response("获取分析结果失败")

@analysis_bp.route('/<int:paper_id>/analysis', methods=['POST'])
@token_required
def create_paper_analysis(paper_id, current_user):
    """创建文献分析"""
    try:
        # 检查文献是否存在
        paper = get_paper_by_id(paper_id)
        if not paper:
            return error_response("文献不存在", 404)
        
        # 检查文件是否存在
        file_path = paper['file_path']
        # 如果file_path已经包含uploads/前缀，直接使用；否则添加前缀
        if file_path.startswith('uploads/'):
            pdf_path = file_path
        else:
            pdf_path = os.path.join('uploads', file_path)
            
        if not os.path.exists(pdf_path):
            return error_response("PDF文件不存在", 404)
        
        # 检查是否正在分析
        existing_analysis = pdf_analyzer.get_analysis_result(paper_id)
        if existing_analysis and existing_analysis['analysis_status'] == 'processing':
            return error_response("文献正在分析中，请稍后再试", 400)
        
        # 获取请求参数
        data = request.get_json() or {}
        force_reanalysis = data.get('force', False)
        
        # 如果已有分析结果且不强制重新分析
        if existing_analysis and existing_analysis['analysis_status'] == 'completed' and not force_reanalysis:
            return success_response(existing_analysis)
        
        # 异步启动分析任务
        analysis_thread = threading.Thread(
            target=async_analyze_paper,
            args=(paper_id, pdf_path)
        )
        analysis_thread.daemon = True
        analysis_thread.start()
        
        return success_response({
            'message': '分析任务已启动',
            'paper_id': paper_id,
            'status': 'processing'
        })
        
    except Exception as e:
        logger.error(f"创建文献分析失败: {e}")
        return error_response("启动分析任务失败")

@analysis_bp.route('/<int:paper_id>/analysis/status', methods=['GET'])
@token_required
def get_analysis_status(paper_id, current_user):
    """获取分析状态"""
    try:
        # 检查文献是否存在
        paper = get_paper_by_id(paper_id)
        if not paper:
            return error_response("文献不存在", 404)
        
        # 获取分析结果
        analysis_result = pdf_analyzer.get_analysis_result(paper_id)
        
        if not analysis_result:
            return success_response({
                'paper_id': paper_id,
                'status': 'not_started',
                'message': '未开始分析'
            })
        
        status_info = {
            'paper_id': paper_id,
            'status': analysis_result['analysis_status'],
            'create_time': analysis_result['create_time'],
            'update_time': analysis_result['update_time']
        }
        
        # 根据状态返回不同信息
        if analysis_result['analysis_status'] == 'completed':
            status_info['message'] = '分析已完成'
            status_info['has_result'] = True
        elif analysis_result['analysis_status'] == 'processing':
            status_info['message'] = '正在分析中...'
            status_info['has_result'] = False
        elif analysis_result['analysis_status'] == 'failed':
            status_info['message'] = '分析失败'
            status_info['has_result'] = False
        else:
            status_info['message'] = '等待分析'
            status_info['has_result'] = False
        
        return success_response(status_info)
        
    except Exception as e:
        logger.error(f"获取分析状态失败: {e}")
        return error_response("获取分析状态失败")

@analysis_bp.route('/<int:paper_id>/analysis', methods=['DELETE'])
@token_required
def delete_paper_analysis(paper_id, current_user):
    """删除文献分析结果"""
    try:
        # 检查文献是否存在
        paper = get_paper_by_id(paper_id)
        if not paper:
            return error_response("文献不存在", 404)
        
        # 删除分析结果
        from models.database import execute_update
        sql = "DELETE FROM paper_analysis WHERE paper_id = ?"
        execute_update(sql, (paper_id,))
        
        return success_response({
            'message': '分析结果已删除',
            'paper_id': paper_id
        })
        
    except Exception as e:
        logger.error(f"删除文献分析失败: {e}")
        return error_response("删除分析结果失败")

def async_analyze_paper(paper_id: int, pdf_path: str):
    """异步分析文献"""
    try:
        logger.info(f"开始异步分析文献: paper_id={paper_id}, pdf_path={pdf_path}")
        result = pdf_analyzer.analyze_paper(paper_id, pdf_path)
        
        if result['success']:
            logger.info(f"文献分析完成: paper_id={paper_id}")
        else:
            logger.error(f"文献分析失败: paper_id={paper_id}, error={result['error']}")
            
    except Exception as e:
        logger.error(f"异步分析文献异常: {e}")
        # 确保状态更新为失败
        pdf_analyzer.update_analysis_status(paper_id, 'failed')

# 批量分析接口（可选）
@analysis_bp.route('/analysis/batch', methods=['POST'])
@token_required
def batch_analyze_papers(current_user):
    """批量分析文献"""
    try:
        data = request.get_json() or {}
        paper_ids = data.get('paper_ids', [])
        
        if not paper_ids:
            return error_response("请提供要分析的文献ID列表", 400)
        
        # 验证文献ID并启动分析任务
        success_count = 0
        failed_papers = []
        
        for paper_id in paper_ids:
            try:
                paper = get_paper_by_id(paper_id)
                if not paper:
                    failed_papers.append({'paper_id': paper_id, 'error': '文献不存在'})
                    continue
                
                file_path = paper['file_path']
                # 如果file_path已经包含uploads/前缀，直接使用；否则添加前缀
                if file_path.startswith('uploads/'):
                    pdf_path = file_path
                else:
                    pdf_path = os.path.join('uploads', file_path)
                    
                if not os.path.exists(pdf_path):
                    failed_papers.append({'paper_id': paper_id, 'error': 'PDF文件不存在'})
                    continue
                
                # 检查是否正在分析
                existing_analysis = pdf_analyzer.get_analysis_result(paper_id)
                if existing_analysis and existing_analysis['analysis_status'] == 'processing':
                    failed_papers.append({'paper_id': paper_id, 'error': '正在分析中'})
                    continue
                
                # 启动异步分析
                analysis_thread = threading.Thread(
                    target=async_analyze_paper,
                    args=(paper_id, pdf_path)
                )
                analysis_thread.daemon = True
                analysis_thread.start()
                
                success_count += 1
                
            except Exception as e:
                failed_papers.append({'paper_id': paper_id, 'error': str(e)})
        
        return success_response({
            'message': f'批量分析任务已启动',
            'success_count': success_count,
            'failed_count': len(failed_papers),
            'failed_papers': failed_papers
        })
        
    except Exception as e:
        logger.error(f"批量分析文献失败: {e}")
        return error_response("批量分析任务启动失败") 