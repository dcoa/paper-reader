#!/usr/bin/env python3
"""
通用响应函数
提供统一的API响应格式
"""
from flask import jsonify

def success_response(data=None, message="操作成功", code=200):
    """
    成功响应函数
    """
    response = {
        "success": True,
        "code": code,
        "message": message
    }
    
    if data is not None:
        response["data"] = data
    
    return jsonify(response), code

def error_response(error="操作失败", code=400, details=None):
    """
    错误响应函数
    """
    response = {
        "success": False,
        "code": code,
        "error": error
    }
    
    if details:
        response["details"] = details
    
    return jsonify(response), code

def pagination_response(data, total, page, limit, message="查询成功"):
    """
    分页响应函数
    """
    response_data = {
        "items": data,
        "pagination": {
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit if limit > 0 else 1
        }
    }
    
    return success_response(data=response_data, message=message)

def validation_error_response(errors):
    """
    参数验证错误响应
    """
    return error_response(
        error="参数验证失败",
        code=400,
        details=errors
    )

def unauthorized_response(message="未授权访问"):
    """
    未授权响应
    """
    return error_response(error=message, code=401)

def forbidden_response(message="权限不足"):
    """
    权限不足响应
    """
    return error_response(error=message, code=403)

def not_found_response(message="资源不存在"):
    """
    资源不存在响应
    """
    return error_response(error=message, code=404)

def server_error_response(message="服务器内部错误"):
    """
    服务器错误响应
    """
    return error_response(error=message, code=500) 