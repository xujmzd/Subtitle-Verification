"""
字幕核对桌面应用程序 - 主程序入口
使用 Eel 框架创建桌面应用，支持 TXT 和 Word 文件的字幕比对
"""

import eel
import os
import sys
import atexit
import signal
from pathlib import Path

# 导入自定义模块
from app.file_handler import read_file, normalize_text
from app.text_compare import simple_compare_original_texts, compare_normalized_texts

# 初始化 Eel，指定前端文件目录
eel.init('web')


# 全局变量：存储当前加载的文件内容（不保存到源文件）
current_files = {
    'file1': {
        'path': None,
        'original': '',
        'normalized': ''
    },
    'file2': {
        'path': None,
        'original': '',
        'normalized': ''
    }
}


def cleanup_resources():
    """
    清理所有资源：释放内存、关闭连接
    
    这个函数会在程序退出时被调用，确保所有资源都被正确释放
    """
    global current_files
    
    try:
        # 1. 清理全局变量，释放内存
        current_files['file1'] = {
            'path': None,
            'original': '',
            'normalized': ''
        }
        current_files['file2'] = {
            'path': None,
            'original': '',
            'normalized': ''
        }
        
        # 2. 强制垃圾回收
        import gc
        gc.collect()
        
        print('资源已清理')
        
    except Exception as e:
        print(f'清理资源时出错: {e}')
    finally:
        # 3. 强制退出进程
        try:
            os._exit(0)  # 使用 os._exit 强制退出，不执行清理钩子
        except:
            try:
                sys.exit(0)
            except:
                pass


def close_callback(path, sockets):
    """
    Eel 关闭回调函数
    当浏览器窗口关闭时调用
    """
    print('应用窗口已关闭，正在清理资源...')
    cleanup_resources()


def signal_handler(signum, frame):
    """
    信号处理器（用于 Ctrl+C 等）
    """
    print('\n收到退出信号，正在清理资源...')
    cleanup_resources()


# 注册退出时的清理函数
atexit.register(cleanup_resources)

# 注册信号处理器
try:
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
except:
    pass


@eel.expose
def load_file_from_path(file_path: str, file_index: int) -> dict:
    """
    从文件路径加载文件（TXT 或 Word）
    
    Args:
        file_path: 文件路径
        file_index: 文件索引（1 或 2）
        
    Returns:
        包含文件内容和状态信息的字典
    """
    try:
        # 读取文件
        original_text, normalized_text = read_file(file_path)
        
        # 存储到全局变量（用于后续编辑和比对）
        file_key = f'file{file_index}'
        current_files[file_key]['path'] = file_path
        current_files[file_key]['original'] = original_text
        current_files[file_key]['normalized'] = normalized_text
        
        return {
            'success': True,
            'original_text': original_text,
            'normalized_text': normalized_text,
            'file_name': os.path.basename(file_path),
            'message': '文件加载成功'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f'加载文件失败: {str(e)}'
        }


@eel.expose
def load_file_from_content(file_name: str, file_content: bytes, file_extension: str, file_index: int) -> dict:
    """
    从文件内容加载文件（用于浏览器文件选择）
    
    Args:
        file_name: 文件名
        file_content: 文件内容的 base64 编码字符串或字节
        file_extension: 文件扩展名（.txt 或 .docx）
        file_index: 文件索引（1 或 2）
        
    Returns:
        包含文件内容和状态信息的字典
    """
    try:
        import base64
        import io
        
        # 如果 file_content 是字符串，尝试 base64 解码
        if isinstance(file_content, str):
            try:
                file_bytes = base64.b64decode(file_content)
            except:
                # 如果不是 base64，尝试直接使用字符串
                file_bytes = file_content.encode('utf-8')
        else:
            file_bytes = file_content
        
        # 根据扩展名处理文件
        if file_extension.lower() == '.txt':
            # 尝试不同的编码
            try:
                original_text = file_bytes.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    original_text = file_bytes.decode('gbk')
                except UnicodeDecodeError:
                    original_text = file_bytes.decode('latin-1', errors='ignore')
        elif file_extension.lower() == '.docx':
            # 对于 Word 文件，需要保存到临时文件或使用内存中的文件
            from docx import Document
            doc_file = io.BytesIO(file_bytes)
            doc = Document(doc_file)
            paragraphs = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    paragraphs.append(paragraph.text)
            original_text = '\n'.join(paragraphs)
        else:
            raise ValueError(f"不支持的文件格式: {file_extension}")
        
        # 规范化文本
        from app.file_handler import normalize_text
        normalized_text = normalize_text(original_text)
        
        # 存储到全局变量
        file_key = f'file{file_index}'
        current_files[file_key]['path'] = file_name  # 使用文件名作为标识
        current_files[file_key]['original'] = original_text
        current_files[file_key]['normalized'] = normalized_text
        
        return {
            'success': True,
            'original_text': original_text,
            'normalized_text': normalized_text,
            'file_name': file_name,
            'message': '文件加载成功'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f'加载文件失败: {str(e)}'
        }


# 保持向后兼容
@eel.expose
def load_file(file_path: str, file_index: int) -> dict:
    """
    加载文件（兼容旧接口，内部调用 load_file_from_path）
    """
    return load_file_from_path(file_path, file_index)


@eel.expose
def compare_files() -> dict:
    """
    比较两个文件的内容（使用规范化文本进行比对，忽略标点、空格、换行）
    
    由于前端显示的是规范化文本，这里直接比较规范化文本
    
    Returns:
        包含比对结果的字典
    """
    try:
        file1_normalized = current_files['file1']['normalized']
        file2_normalized = current_files['file2']['normalized']
        
        # 检查是否已加载两个文件
        if not file1_normalized and not file2_normalized:
            return {
                'success': False,
                'error': '请先加载两个文件',
                'message': '需要加载两个文件才能进行比对'
            }
        
        # 如果只有一个文件，返回空比对结果
        if not file1_normalized or not file2_normalized:
            return {
                'success': True,
                'diffs1': [],
                'diffs2': [],
                'message': '需要加载两个文件才能进行比对'
            }
        
        # 直接比较规范化文本（因为前端显示的就是规范化文本）
        from app.text_compare import compare_texts, TextDiff
        diffs1, diffs2 = compare_texts(file1_normalized, file2_normalized)
        
        # 转换为字典列表
        diffs1_dict = [diff.to_dict() for diff in diffs1]
        diffs2_dict = [diff.to_dict() for diff in diffs2]
        
        return {
            'success': True,
            'diffs1': diffs1_dict,
            'diffs2': diffs2_dict,
            'message': '比对完成（已忽略标点、空格、换行）'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f'比对失败: {str(e)}'
        }


@eel.expose
def update_file_content(file_index: int, new_content: str) -> dict:
    """
    更新文件内容（实时编辑，不保存到源文件）
    
    注意：前端传入的是规范化文本内容
    
    Args:
        file_index: 文件索引（1 或 2）
        new_content: 新的文件内容（规范化文本）
        
    Returns:
        包含更新状态的字典
    """
    try:
        file_key = f'file{file_index}'
        # 更新规范化文本（前端显示和编辑的就是规范化文本）
        current_files[file_key]['normalized'] = new_content
        
        return {
            'success': True,
            'message': '内容已更新'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f'更新失败: {str(e)}'
        }


@eel.expose
def get_file_content(file_index: int) -> dict:
    """
    获取当前文件内容
    
    Args:
        file_index: 文件索引（1 或 2）
        
    Returns:
        包含文件内容的字典
    """
    try:
        file_key = f'file{file_index}'
        # 返回规范化文本（因为前端显示的就是规范化文本）
        content = current_files[file_key]['normalized']
        
        return {
            'success': True,
            'content': content
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'content': ''
        }


@eel.expose
def compare_with_normalization() -> dict:
    """
    使用规范化文本进行比较（忽略标点、空格、换行）
    
    Returns:
        包含比对结果的字典
    """
    try:
        file1_original = current_files['file1']['original']
        file1_normalized = current_files['file1']['normalized']
        file2_original = current_files['file2']['original']
        file2_normalized = current_files['file2']['normalized']
        
        # 检查是否已加载两个文件
        if not file1_original and not file2_original:
            return {
                'success': False,
                'error': '请先加载两个文件',
                'message': '需要加载两个文件才能进行比对'
            }
        
        if not file1_original or not file2_original:
            return {
                'success': True,
                'diffs1': [],
                'diffs2': [],
                'message': '需要加载两个文件才能进行比对'
            }
        
        # 使用规范化文本进行比较，但返回原始文本的差异
        diffs1, diffs2 = compare_normalized_texts(file1_original, file1_normalized, file2_original, file2_normalized)
        
        return {
            'success': True,
            'diffs1': diffs1,
            'diffs2': diffs2,
            'normalized1': file1_normalized,
            'normalized2': file2_normalized,
            'message': '比对完成'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f'比对失败: {str(e)}'
        }


def main():
    """
    主函数：启动 Eel 应用
    """
    # 启动 Eel 应用
    # start() 方法会启动一个本地 Web 服务器并打开浏览器
    # mode='chrome' 表示以 Chrome 应用模式运行（桌面应用）
    # size=(1400, 900) 设置窗口大小
    # port=0 表示自动选择可用端口
    try:
        eel.start('index.html', 
                 mode='chrome',  # 使用 Chrome 浏览器
                 size=(1400, 900),
                 port=0,
                 close_callback=close_callback)
        
    except KeyboardInterrupt:
        print('\n用户中断，正在清理资源...')
        cleanup_resources()
    except SystemExit:
        cleanup_resources()
    except Exception as e:
        print(f'应用启动错误: {e}')
        cleanup_resources()
    finally:
        # 确保资源被清理
        cleanup_resources()


if __name__ == '__main__':
    main()
