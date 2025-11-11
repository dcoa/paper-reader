#!/usr/bin/env python3
"""
数据模型包
包含用户、文献、批注、AI对话等数据模型
"""

__version__ = "1.0.0"
__author__ = "PaperReader Team"

from .database import *
from .user import *
from .paper import *
from .annotation import *
from .publication_type import *
from .ai_conversation import * 