"""
文件处理模块
负责读取和处理 TXT 和 Word 文件，并规范化文本内容（移除标点、空格、换行等）
"""

import re
import os
from pathlib import Path
from typing import Tuple, List, Optional

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    print("警告: python-docx 未安装，Word 文件功能将不可用")


def normalize_text(text: str) -> str:
    """
    规范化文本：移除所有标点符号、空格和换行符
    
    Args:
        text: 原始文本内容
        
    Returns:
        规范化后的文本（仅保留中英文字符和数字）
    """
    if not text:
        return ""
    
    # 使用正则表达式移除所有标点符号、空格、换行等
    # 只保留中文字符、英文字母和数字
    normalized = re.sub(r'[^\w\u4e00-\u9fff]', '', text)
    
    return normalized


def read_txt_file(file_path: str) -> Tuple[str, str]:
    """
    读取 TXT 文件
    
    Args:
        file_path: TXT 文件路径
        
    Returns:
        Tuple[原始文本, 规范化文本]
    """
    try:
        # 尝试使用 UTF-8 编码读取
        with open(file_path, 'r', encoding='utf-8') as f:
            original_text = f.read()
    except UnicodeDecodeError:
        # 如果 UTF-8 失败，尝试使用 GBK 编码（常见的中文编码）
        try:
            with open(file_path, 'r', encoding='gbk') as f:
                original_text = f.read()
        except UnicodeDecodeError:
            # 最后尝试 latin-1（几乎不会失败，但可能产生乱码）
            with open(file_path, 'r', encoding='latin-1', errors='ignore') as f:
                original_text = f.read()
    
    normalized_text = normalize_text(original_text)
    return original_text, normalized_text


def read_docx_file(file_path: str) -> Tuple[str, str]:
    """
    读取 Word (.docx) 文件
    
    Args:
        file_path: Word 文件路径
        
    Returns:
        Tuple[原始文本, 规范化文本]
    """
    if not DOCX_AVAILABLE:
        raise ImportError("python-docx 未安装，无法读取 Word 文件")
    
    try:
        doc = Document(file_path)
        # 提取所有段落文本
        paragraphs = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():  # 忽略空段落
                paragraphs.append(paragraph.text)
        
        # 合并所有段落，用换行符连接
        original_text = '\n'.join(paragraphs)
        normalized_text = normalize_text(original_text)
        
        return original_text, normalized_text
    except Exception as e:
        raise Exception(f"读取 Word 文件时出错: {str(e)}")


def read_file(file_path: str) -> Tuple[str, str]:
    """
    根据文件扩展名自动选择读取方式
    
    Args:
        file_path: 文件路径
        
    Returns:
        Tuple[原始文本, 规范化文本]
    """
    file_path_obj = Path(file_path)
    
    if not file_path_obj.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    extension = file_path_obj.suffix.lower()
    
    if extension == '.txt':
        return read_txt_file(file_path)
    elif extension in ['.docx', '.doc']:
        if extension == '.doc':
            raise ValueError("不支持 .doc 格式，请使用 .docx 格式")
        return read_docx_file(file_path)
    else:
        raise ValueError(f"不支持的文件格式: {extension}")


def split_text_into_chunks(text: str, chunk_size: int = 100) -> List[str]:
    """
    将文本分割成较小的块，用于比对和显示
    
    Args:
        text: 原始文本
        chunk_size: 每个块的大小（字符数）
        
    Returns:
        文本块列表
    """
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])
    return chunks
