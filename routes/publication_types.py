#!/usr/bin/env python3
"""
文献类型路由
处理文献类型相关的API请求
"""
from flask import Blueprint
from models.publication_type import get_all_publication_types
from utils.response import success_response, error_response

# 创建蓝图
publication_types_bp = Blueprint('publication_types', __name__)

@publication_types_bp.route('', methods=['GET'])
def get_publication_types():
    """
    获取文献类型列表路由函数（对应API 5.1）
    GET /api/publication-types
    """
    try:
        # 获取所有文献类型
        publication_types = get_all_publication_types()
        
        return success_response(
            data=publication_types,
            message="获取文献类型列表成功"
        )
        
    except Exception as e:
        return error_response(
            error=f"获取文献类型列表失败: {str(e)}",
            code=500
        )

@publication_types_bp.route('/<int:type_id>', methods=['GET'])
def get_publication_type_by_id(type_id):
    """
    根据ID获取文献类型详情
    GET /api/publication-types/{type_id}
    """
    try:
        from models.publication_type import get_publication_type_by_id
        
        publication_type = get_publication_type_by_id(type_id)
        
        if not publication_type:
            return error_response(
                error="文献类型不存在",
                code=404
            )
        
        return success_response(
            data=publication_type.to_dict(),
            message="获取文献类型详情成功"
        )
        
    except Exception as e:
        return error_response(
            error=f"获取文献类型详情失败: {str(e)}",
            code=500
        ) 