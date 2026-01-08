"""
文本比对模块
负责比较两个文本文件的内容，识别差异并生成高亮信息
"""

from typing import List, Dict, Tuple, Optional
import difflib


class TextDiff:
    """
    文本差异类，用于存储单个差异片段的信息
    """
    def __init__(self, text: str, status: str, start_pos: int, end_pos: int):
        """
        Args:
            text: 差异文本内容
            status: 差异状态 ('equal', 'delete', 'insert', 'replace')
            start_pos: 在原始文本中的起始位置
            end_pos: 在原始文本中的结束位置
        """
        self.text = text
        self.status = status  # 'equal', 'delete', 'insert', 'replace'
        self.start_pos = start_pos
        self.end_pos = end_pos
    
    def to_dict(self) -> Dict:
        """转换为字典格式，用于 JSON 序列化"""
        return {
            'text': self.text,
            'status': self.status,
            'start_pos': self.start_pos,
            'end_pos': self.end_pos
        }


def compare_texts(text1: str, text2: str) -> Tuple[List[TextDiff], List[TextDiff]]:
    """
    比较两个文本，返回差异信息列表
    
    使用 difflib 的 SequenceMatcher 来找出两个文本的差异
    
    Args:
        text1: 第一个文本
        text2: 第二个文本
        
    Returns:
        Tuple[文本1的差异列表, 文本2的差异列表]
    """
    # 使用 difflib 进行文本比对
    matcher = difflib.SequenceMatcher(None, text1, text2)
    
    diffs1 = []
    diffs2 = []
    pos1 = 0
    pos2 = 0
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            # 相同的部分
            text1_segment = text1[i1:i2]
            text2_segment = text2[j1:j2]
            diffs1.append(TextDiff(text1_segment, 'equal', pos1, pos1 + len(text1_segment)))
            diffs2.append(TextDiff(text2_segment, 'equal', pos2, pos2 + len(text2_segment)))
            pos1 += len(text1_segment)
            pos2 += len(text2_segment)
        elif tag == 'delete':
            # 文本1中删除的部分（文本2中没有）
            text1_segment = text1[i1:i2]
            diffs1.append(TextDiff(text1_segment, 'delete', pos1, pos1 + len(text1_segment)))
            pos1 += len(text1_segment)
        elif tag == 'insert':
            # 文本2中插入的部分（文本1中没有）
            text2_segment = text2[j1:j2]
            diffs2.append(TextDiff(text2_segment, 'insert', pos2, pos2 + len(text2_segment)))
            pos2 += len(text2_segment)
        elif tag == 'replace':
            # 替换的部分（两个文本都有，但内容不同）
            text1_segment = text1[i1:i2]
            text2_segment = text2[j1:j2]
            diffs1.append(TextDiff(text1_segment, 'replace', pos1, pos1 + len(text1_segment)))
            diffs2.append(TextDiff(text2_segment, 'replace', pos2, pos2 + len(text2_segment)))
            pos1 += len(text1_segment)
            pos2 += len(text2_segment)
    
    return diffs1, diffs2


def build_char_mapping(original: str, normalized: str) -> List[int]:
    """
    建立规范化文本字符到原始文本位置的映射
    
    返回一个列表，其中 result[i] 表示规范化文本中第 i 个字符在原始文本中的位置
    
    Args:
        original: 原始文本
        normalized: 规范化文本
        
    Returns:
        位置映射列表，长度为规范化文本的长度
    """
    mapping = []
    orig_pos = 0
    norm_pos = 0
    
    # 遍历原始文本，找到每个规范化字符对应的位置
    while orig_pos < len(original) and norm_pos < len(normalized):
        orig_char = original[orig_pos]
        norm_char = normalized[norm_pos]
        
        # 如果字符匹配，记录映射关系
        if orig_char == norm_char:
            mapping.append(orig_pos)
            norm_pos += 1
            orig_pos += 1
        else:
            # 如果字符不匹配，原始文本中的字符可能是被规范化的字符（标点、空格等）
            # 检查原始字符是否应该被跳过
            import re
            # 如果原始字符是标点、空格等（不在规范化文本中的字符），跳过它
            if not (orig_char.isalnum() or ('\u4e00' <= orig_char <= '\u9fff')):
                orig_pos += 1
            else:
                # 如果原始字符是字母数字，但规范化字符不匹配，可能是编码问题
                # 尝试继续匹配
                mapping.append(orig_pos)
                norm_pos += 1
                orig_pos += 1
    
    # 如果还有剩余的规范化字符，使用最后一个位置
    while norm_pos < len(normalized):
        if mapping:
            mapping.append(mapping[-1] + 1)
        else:
            mapping.append(0)
        norm_pos += 1
    
    return mapping


def map_diff_to_original_improved(original: str, normalized: str, normalized_diffs: List[TextDiff]) -> List[TextDiff]:
    """
    将规范化文本的差异映射回原始文本（改进版本）
    
    通过建立字符位置映射关系，准确地将规范化文本的差异位置映射到原始文本
    
    Args:
        original: 原始文本
        normalized: 规范化文本
        normalized_diffs: 规范化文本的差异列表
        
    Returns:
        原始文本的差异列表
    """
    if not normalized or not original:
        # 如果规范化文本或原始文本为空，返回空差异列表
        return []
    
    # 建立位置映射：规范化文本位置 -> 原始文本位置
    char_mapping = build_char_mapping(original, normalized)
    
    # 将规范化文本的差异映射到原始文本
    original_diffs = []
    
    for diff in normalized_diffs:
        norm_start = diff.start_pos
        norm_end = diff.end_pos
        
        # 查找对应的原始文本位置
        if norm_start < len(char_mapping):
            orig_start = char_mapping[norm_start]
        else:
            # 如果超出范围，使用最后一个映射位置
            orig_start = char_mapping[-1] if char_mapping else 0
        
        if norm_end > 0 and norm_end - 1 < len(char_mapping):
            # 找到结束位置的最后一个字符对应的原始位置，然后加1
            orig_end = char_mapping[norm_end - 1] + 1
        else:
            # 如果超出范围，使用最后一个映射位置加1
            orig_end = (char_mapping[-1] + 1) if char_mapping else len(original)
        
        # 确保位置在有效范围内
        orig_start = max(0, min(orig_start, len(original)))
        orig_end = max(orig_start, min(orig_end, len(original)))
        
        # 获取原始文本片段
        orig_text = original[orig_start:orig_end]
        
        # 创建差异对象
        original_diffs.append(TextDiff(orig_text, diff.status, orig_start, orig_end))
    
    return original_diffs


def compare_normalized_texts(original1: str, normalized1: str, 
                            original2: str, normalized2: str) -> Tuple[List[Dict], List[Dict]]:
    """
    基于规范化文本进行比较，但返回原始文本的差异信息
    
    比对时会忽略标点符号、空格、换行符等，只在字母数字和中文字符层面进行比较
    
    Args:
        original1: 文本1的原始内容
        normalized1: 文本1的规范化内容（已去除标点、空格、换行）
        original2: 文本2的原始内容
        normalized2: 文本2的规范化内容（已去除标点、空格、换行）
        
    Returns:
        Tuple[文本1的差异字典列表, 文本2的差异字典列表]
    """
    # 比较规范化文本
    diffs_norm1, diffs_norm2 = compare_texts(normalized1, normalized2)
    
    # 将规范化文本的差异映射回原始文本
    diffs_orig1 = map_diff_to_original_improved(original1, normalized1, diffs_norm1)
    diffs_orig2 = map_diff_to_original_improved(original2, normalized2, diffs_norm2)
    
    # 转换为字典列表
    return [diff.to_dict() for diff in diffs_orig1], [diff.to_dict() for diff in diffs_orig2]


def simple_compare_original_texts(text1: str, text2: str) -> Tuple[List[Dict], List[Dict]]:
    """
    直接比较原始文本（不进行规范化处理）
    
    这个方法用于在界面上直接比较和显示原始文本的差异
    
    Args:
        text1: 第一个文本
        text2: 第二个文本
        
    Returns:
        Tuple[文本1的差异字典列表, 文本2的差异字典列表]
    """
    diffs1, diffs2 = compare_texts(text1, text2)
    return [diff.to_dict() for diff in diffs1], [diff.to_dict() for diff in diffs2]
