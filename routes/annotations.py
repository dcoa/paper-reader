#!/usr/bin/env python3
"""
批注管理路由
处理批注相关的API请求
"""
from flask import Blueprint, request
from models.annotation import (
    create_annotation, get_annotations_by_paper, 
    delete_annotation, get_annotation_by_id
)
from utils.auth import token_required, get_user_from_request, check_user_permission
from utils.response import success_response, error_response, validation_error_response

# 创建蓝图
annotations_bp = Blueprint('annotations', __name__)

@annotations_bp.route('', methods=['POST'])
@token_required
def create_annotation_route():
    """
    创建批注路由函数（对应API 3.1）
    POST /api/annotations
    """
    try:
        # 获取当前用户
        current_user = get_user_from_request()
        
        # 获取请求数据
        data = request.get_json()
        if not data:
            return validation_error_response("请求数据格式错误")
        
        paper_id = data.get('paper_id')
        content = data.get('content')
        section = data.get('section')
        page_number = data.get('page_number')
        position = data.get('position', {})
        
        # 参数验证
        errors = []
        if not paper_id:
            errors.append("文献ID不能为空")
        if not content:
            errors.append("批注内容不能为空")
        
        if errors:
            return validation_error_response(errors)
        
        # 提取位置信息
        position_x = position.get('x') if position else None
        position_y = position.get('y') if position else None
        
        # 创建批注
        annotation = create_annotation(
            paper_id=paper_id,
            user_id=current_user.user_id,
            content=content,
            section=section,
            page_number=page_number,
            position_x=position_x,
            position_y=position_y
        )
        
        if not annotation:
            return error_response(
                error="创建批注失败",
                code=500
            )
        
        return success_response(
            data={
                'annotation_id': annotation['annotation_id'],
                'create_time': annotation['create_time']
            },
            message="批注创建成功"
        )
        
    except Exception as e:
        return error_response(
            error=f"创建批注失败: {str(e)}",
            code=500
        )

@annotations_bp.route('/<int:paper_id>', methods=['GET'])
def get_annotations_route(paper_id):
    """
    获取批注列表路由函数（对应API 3.2）
    GET /api/annotations/{paper_id}
    """
    try:
        # 获取特定文献的所有批注
        annotations = get_annotations_by_paper(paper_id)
        
        return success_response(
            data=annotations,
            message="获取批注列表成功"
        )
        
    except Exception as e:
        return error_response(
            error=f"获取批注列表失败: {str(e)}",
            code=500
        )

@annotations_bp.route('/<int:annotation_id>', methods=['DELETE'])
@token_required
def delete_annotation_route(annotation_id):
    """
    删除批注路由函数（对应API 3.3）
    DELETE /api/annotations/{annotation_id}
    """
    try:
        # 获取当前用户
        current_user = get_user_from_request()
        
        # 检查批注是否存在以及权限
        annotation = get_annotation_by_id(annotation_id)
        if not annotation:
            return error_response(
                error="批注不存在",
                code=404
            )
        
        # 检查权限（只能删除自己的批注）
        if not check_user_permission(current_user.user_id, annotation['user_id']):
            return error_response(
                error="无权删除该批注",
                code=403
            )
        
        # 删除批注
        success = delete_annotation(annotation_id, current_user.user_id)
        
        if not success:
            return error_response(
                error="删除批注失败",
                code=500
            )
        
        return success_response(
            message="批注删除成功"
        )
        
    except Exception as e:
        return error_response(
            error=f"删除批注失败: {str(e)}",
            code=500
        )

@annotations_bp.route('/update/<int:annotation_id>', methods=['PUT'])
@token_required
def update_annotation_route(annotation_id):
    """
    更新批注
    PUT /api/annotations/update/{annotation_id}
    """
    try:
        # 获取当前用户
        current_user = get_user_from_request()
        
        # 获取请求数据
        data = request.get_json()
        if not data:
            return validation_error_response("请求数据格式错误")
        
        # 检查批注是否存在以及权限
        annotation = get_annotation_by_id(annotation_id)
        if not annotation:
            return error_response(
                error="批注不存在",
                code=404
            )
        
        # 检查权限（只能更新自己的批注）
        if not check_user_permission(current_user.user_id, annotation['user_id']):
            return error_response(
                error="无权更新该批注",
                code=403
            )
        
        content = data.get('content')
        section = data.get('section')
        page_number = data.get('page_number')
        position = data.get('position')
        
        # 参数验证
        if not content:
            return validation_error_response("批注内容不能为空")
        
        # 提取位置信息
        position_x = position.get('x') if position else None
        position_y = position.get('y') if position else None
        
        # 更新批注
        from models.annotation import update_annotation
        success = update_annotation(
            annotation_id=annotation_id,
            content=content,
            user_id=current_user.user_id,
            section=section,
            page_number=page_number,
            position_x=position_x,
            position_y=position_y
        )
        
        if not success:
            return error_response(
                error="更新批注失败",
                code=500
            )
        
        return success_response(
            message="批注更新成功"
        )
        
    except Exception as e:
        return error_response(
            error=f"更新批注失败: {str(e)}",
            code=500
        )

@annotations_bp.route('/search', methods=['GET'])
def search_annotations_route():
    """
    搜索批注
    GET /api/annotations/search?keyword=xxx&page=1&limit=10
    """
    try:
        # 获取查询参数
        keyword = request.args.get('keyword', '')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        
        if not keyword:
            return validation_error_response("搜索关键词不能为空")
        
        # 搜索批注
        from models.annotation import search_annotations
        result = search_annotations(keyword, page=page, limit=limit)
        
        return success_response(
            data=result,
            message="搜索批注成功"
        )
        
    except ValueError:
        return validation_error_response("页码和限制数量必须是数字")
    except Exception as e:
        return error_response(
            error=f"搜索批注失败: {str(e)}",
            code=500
        )

@annotations_bp.route('/user/<int:user_id>', methods=['GET'])
@token_required
def get_user_annotations_route(user_id):
    """
    获取用户的所有批注
    GET /api/annotations/user/{user_id}?page=1&limit=10
    """
    try:
        # 获取当前用户
        current_user = get_user_from_request()
        
        # 检查权限（只能查看自己的批注）
        if not check_user_permission(current_user.user_id, user_id):
            return error_response(
                error="无权查看该用户的批注",
                code=403
            )
        
        # 获取查询参数
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        
        # 获取用户批注
        from models.annotation import get_user_annotations
        result = get_user_annotations(user_id, page=page, limit=limit)
        
        return success_response(
            data=result,
            message="获取用户批注成功"
        )
        
    except ValueError:
        return validation_error_response("页码和限制数量必须是数字")
    except Exception as e:
        return error_response(
            error=f"获取用户批注失败: {str(e)}",
            code=500
        ) 