/**
 * 字幕核对工具 - 主 JavaScript 文件
 * 处理文件选择、文本比对、高亮显示和实时编辑功能
 */

// 全局变量：存储当前文件状态
let currentFile1 = null;
let currentFile2 = null;
let isComparing = false;
let scrollSyncEnabled = true;
let isScrolling = false; // 用于防止滚动同步时的循环触发

/**
 * 选择文件
 * @param {number} fileIndex - 文件索引 (1 或 2)
 */
async function selectFile(fileIndex) {
    const fileInput = document.getElementById('file-input');
    fileInput.setAttribute('data-file-index', fileIndex);
    fileInput.click();
}

/**
 * 处理文件选择事件
 * @param {Event} event - 文件选择事件
 */
async function handleFileSelect(event) {
    const fileInput = event.target;
    const fileIndex = parseInt(fileInput.getAttribute('data-file-index'));
    const file = fileInput.files[0];
    
    if (!file) {
        return;
    }
    
    updateStatus('正在加载文件...', 'info');
    
    try {
        // 获取文件扩展名
        const fileName = file.name;
        const fileExtension = fileName.substring(fileName.lastIndexOf('.')).toLowerCase();
        
        // 检查文件类型
        if (fileExtension !== '.txt' && fileExtension !== '.docx') {
            updateStatus('不支持的文件格式，请选择 TXT 或 DOCX 文件', 'error');
            fileInput.value = '';
            return;
        }
        
        // 使用 FileReader 读取文件
        const reader = new FileReader();
        
        if (fileExtension === '.txt') {
            // 文本文件使用文本方式读取
            reader.onload = async function(e) {
                try {
                    const fileContent = e.target.result;
                    // 将文本内容转换为 base64 编码
                    const base64Content = btoa(unescape(encodeURIComponent(fileContent)));
                    
                    // 调用 Python 后端加载文件
                    const result = await eel.load_file_from_content(fileName, base64Content, fileExtension, fileIndex)();
                    
                    handleFileLoadResult(result, fileIndex, fileName);
                } catch (error) {
                    updateStatus(`错误: ${error.message}`, 'error');
                    console.error('加载文件错误:', error);
                    alert(`加载文件时发生错误: ${error.message}`);
                }
                fileInput.value = '';
            };
            reader.readAsText(file, 'UTF-8');
        } else {
            // Word 文件使用二进制方式读取
            reader.onload = async function(e) {
                try {
                    const arrayBuffer = e.target.result;
                    // 将 ArrayBuffer 转换为 base64 编码
                    const bytes = new Uint8Array(arrayBuffer);
                    const binary = String.fromCharCode.apply(null, bytes);
                    const base64Content = btoa(binary);
                    
                    // 调用 Python 后端加载文件
                    const result = await eel.load_file_from_content(fileName, base64Content, fileExtension, fileIndex)();
                    
                    handleFileLoadResult(result, fileIndex, fileName);
                } catch (error) {
                    updateStatus(`错误: ${error.message}`, 'error');
                    console.error('加载文件错误:', error);
                    alert(`加载文件时发生错误: ${error.message}`);
                }
                fileInput.value = '';
            };
            reader.readAsArrayBuffer(file);
        }
        
        reader.onerror = function() {
            updateStatus('读取文件失败', 'error');
            fileInput.value = '';
        };
        
    } catch (error) {
        updateStatus(`错误: ${error.message}`, 'error');
        console.error('文件选择错误:', error);
        fileInput.value = '';
    }
}

/**
 * 处理文件加载结果
 * @param {Object} result - 文件加载结果
 * @param {number} fileIndex - 文件索引
 * @param {string} fileName - 文件名
 */
function handleFileLoadResult(result, fileIndex, fileName) {
    if (result.success) {
        // 更新文件路径显示
        document.getElementById(`file${fileIndex}-path`).value = result.file_name;
        document.getElementById(`file${fileIndex}-name`).textContent = result.file_name;
        
        // 显示规范化后的文本（去除标点、空格、换行，便于对齐）
        const editor = document.getElementById(`editor${fileIndex}`);
        editor.textContent = result.normalized_text;
        
        // 存储当前文件信息
        if (fileIndex === 1) {
            currentFile1 = {
                path: fileName,
                original: result.original_text,
                normalized: result.normalized_text
            };
        } else {
            currentFile2 = {
                path: fileName,
                original: result.original_text,
                normalized: result.normalized_text
            };
        }
        
        updateStatus(`文件 ${fileIndex} 加载成功: ${result.file_name}（已去除标点、空格、换行）`, 'success');
        
        // 如果两个文件都已加载，自动进行比对
        if (currentFile1 && currentFile2) {
            setTimeout(() => performCompare(), 500);
        }
    } else {
        updateStatus(`加载文件失败: ${result.message}`, 'error');
        alert(`加载文件失败: ${result.message}`);
    }
}

/**
 * 执行文本比对
 */
async function performCompare() {
    if (!currentFile1 || !currentFile2) {
        updateStatus('请先加载两个文件', 'error');
        alert('请先加载两个文件才能进行比对');
        return;
    }
    
    isComparing = true;
    updateStatus('正在比对文件...', 'info');
    
    try {
        // 获取当前编辑器内容（规范化文本，可能已被用户编辑）
        const normalized1 = document.getElementById('editor1').textContent;
        const normalized2 = document.getElementById('editor2').textContent;
        
        // 更新后端规范化内容（用户编辑的是规范化文本）
        await eel.update_file_content(1, normalized1)();
        await eel.update_file_content(2, normalized2)();
        
        // 更新本地存储
        currentFile1.normalized = normalized1;
        currentFile2.normalized = normalized2;
        
        // 执行比对（使用规范化文本直接比对，因为显示的就是规范化文本）
        const result = await eel.compare_files()();
        
        if (result.success) {
            // 应用高亮显示（比对结果直接对应规范化文本）
            applyHighlights('editor1', result.diffs1);
            applyHighlights('editor2', result.diffs2);
            
            updateStatus('比对完成，差异已高亮显示', 'success');
        } else {
            updateStatus(`比对失败: ${result.message}`, 'error');
            alert(`比对失败: ${result.message}`);
        }
    } catch (error) {
        updateStatus(`错误: ${error.message}`, 'error');
        console.error('比对错误:', error);
        alert(`比对时发生错误: ${error.message}`);
    } finally {
        isComparing = false;
    }
}

/**
 * 应用文本高亮显示
 * @param {string} editorId - 编辑器元素 ID
 * @param {Array} diffs - 差异数组
 */
function applyHighlights(editorId, diffs) {
    const editor = document.getElementById(editorId);
    const content = editor.textContent;
    
    // 保存当前光标位置和滚动位置
    const selection = window.getSelection();
    const range = selection.rangeCount > 0 ? selection.getRangeAt(0) : null;
    let cursorOffset = 0;
    if (range && editor.contains(range.commonAncestorContainer)) {
        cursorOffset = range.startOffset;
    }
    const scrollTop = editor.scrollTop;
    
    // 构建 HTML 内容
    let html = '';
    let position = 0;
    
    for (const diff of diffs) {
        const text = diff.text || '';
        const status = diff.status || 'equal';
        
        // 转义 HTML 特殊字符
        const escapedText = escapeHtml(text);
        
        // 根据状态添加不同的 CSS 类
        let className = 'highlight-equal';
        if (status === 'delete') {
            className = 'highlight-missing';
        } else if (status === 'insert') {
            className = 'highlight-added';
        } else if (status === 'replace') {
            className = 'highlight-different';
        }
        
        // 包装在 span 标签中
        html += `<span class="${className}">${escapedText}</span>`;
        
        position += text.length;
    }
    
    // 应用 HTML（这会移除 contenteditable 的编辑能力，所以我们需要重新设置）
    editor.innerHTML = html;
    
    // 恢复光标位置（简化实现）
    editor.scrollTop = scrollTop;
}

/**
 * HTML 转义函数
 * @param {string} text - 要转义的文本
 * @returns {string} 转义后的文本
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * 编辑器内容输入事件处理
 * @param {number} fileIndex - 文件索引 (1 或 2)
 */
function onEditorInput(fileIndex) {
    // 如果正在比对，不处理输入事件
    if (isComparing) {
        return;
    }
    
    // 清除高亮（用户编辑后需要重新比对）
    const editor = document.getElementById(`editor${fileIndex}`);
    const text = editor.textContent || editor.innerText;
    
    // 更新后端内容
    eel.update_file_content(fileIndex, text)();
    
    // 自动重新比对（延迟执行，避免频繁比对）
    if (currentFile1 && currentFile2) {
        clearTimeout(window.autoCompareTimeout);
        window.autoCompareTimeout = setTimeout(() => {
            performCompare();
        }, 1000); // 1秒延迟
    }
}

/**
 * 同步滚动（使两个编辑器容器同步滚动）
 * @param {number} editorIndex - 编辑器索引 (1 或 2)
 */
function syncScroll(editorIndex) {
    if (!scrollSyncEnabled || isScrolling) {
        return;
    }
    
    const container = document.getElementById(`editor-container${editorIndex}`);
    const otherIndex = editorIndex === 1 ? 2 : 1;
    const otherContainer = document.getElementById(`editor-container${otherIndex}`);
    
    if (!container || !otherContainer) {
        return;
    }
    
    // 设置滚动标志，防止循环触发
    isScrolling = true;
    
    // 计算滚动比例，确保两个容器内容高度不同时也能正确同步
    const containerScrollHeight = container.scrollHeight - container.clientHeight;
    const otherContainerScrollHeight = otherContainer.scrollHeight - otherContainer.clientHeight;
    
    if (containerScrollHeight > 0 && otherContainerScrollHeight > 0) {
        // 计算滚动比例
        const scrollRatio = container.scrollTop / containerScrollHeight;
        // 应用到另一个容器
        otherContainer.scrollTop = scrollRatio * otherContainerScrollHeight;
    } else {
        // 如果内容高度相同，直接同步
        otherContainer.scrollTop = container.scrollTop;
    }
    
    // 同步水平滚动
    otherContainer.scrollLeft = container.scrollLeft;
    
    // 恢复滚动同步标志
    requestAnimationFrame(() => {
        isScrolling = false;
    });
}

/**
 * 更新状态栏
 * @param {string} message - 状态消息
 * @param {string} type - 状态类型 ('info', 'success', 'error')
 */
function updateStatus(message, type = 'info') {
    const statusBar = document.getElementById('status-bar');
    const statusText = document.getElementById('status-text');
    
    statusText.textContent = message;
    
    // 移除所有状态类
    statusBar.classList.remove('success', 'error');
    
    // 添加新的状态类
    if (type === 'success') {
        statusBar.classList.add('success');
    } else if (type === 'error') {
        statusBar.classList.add('error');
    }
}

/**
 * 清空所有内容
 */
function clearAll() {
    if (confirm('确定要清空所有内容吗？')) {
        currentFile1 = null;
        currentFile2 = null;
        
        document.getElementById('file1-path').value = '';
        document.getElementById('file2-path').value = '';
        document.getElementById('file1-name').textContent = '未加载';
        document.getElementById('file2-name').textContent = '未加载';
        
        document.getElementById('editor1').textContent = '';
        document.getElementById('editor2').textContent = '';
        
        updateStatus('已清空所有内容', 'info');
    }
}

// 页面加载完成后的初始化
document.addEventListener('DOMContentLoaded', function() {
    updateStatus('请选择要比对的文件', 'info');
    
    // 监听编辑器粘贴事件，移除格式
    const editors = document.querySelectorAll('.editor');
    editors.forEach(editor => {
        editor.addEventListener('paste', function(e) {
            e.preventDefault();
            const text = e.clipboardData.getData('text/plain');
            document.execCommand('insertText', false, text);
        });
    });
});

// 页面卸载前的清理
window.addEventListener('beforeunload', function() {
    // 清理前端资源
    currentFile1 = null;
    currentFile2 = null;
    
    // 清除定时器
    if (window.autoCompareTimeout) {
        clearTimeout(window.autoCompareTimeout);
    }
    
    // 清理所有事件监听器
    const editors = document.querySelectorAll('.editor');
    editors.forEach(editor => {
        editor.oninput = null;
        editor.onscroll = null;
    });
});

// 页面卸载时的清理
window.addEventListener('unload', function() {
    // 确保所有资源被释放
    currentFile1 = null;
    currentFile2 = null;
    
    if (window.autoCompareTimeout) {
        clearTimeout(window.autoCompareTimeout);
    }
});

/**
 * 处理拖拽悬停事件
 * @param {Event} event - 拖拽事件
 */
function handleDragOver(event) {
    event.preventDefault();
    event.stopPropagation();
    
    // 检查是否是文件拖拽
    if (event.dataTransfer.types.includes('Files')) {
        event.dataTransfer.dropEffect = 'copy';
        // 添加拖拽悬停样式
        event.currentTarget.classList.add('drag-over');
    }
}

/**
 * 处理拖拽离开事件
 * @param {Event} event - 拖拽事件
 */
function handleDragLeave(event) {
    event.preventDefault();
    event.stopPropagation();
    
    // 移除拖拽悬停样式
    event.currentTarget.classList.remove('drag-over');
}

/**
 * 处理文件拖拽放置事件
 * @param {Event} event - 拖拽事件
 * @param {number} fileIndex - 文件索引 (1 或 2)
 */
async function handleDrop(event, fileIndex) {
    event.preventDefault();
    event.stopPropagation();
    
    // 移除拖拽悬停样式
    event.currentTarget.classList.remove('drag-over');
    
    // 获取拖拽的文件
    const files = event.dataTransfer.files;
    
    if (!files || files.length === 0) {
        updateStatus('未检测到文件', 'error');
        return;
    }
    
    // 只处理第一个文件
    const file = files[0];
    
    // 检查文件类型
    const fileName = file.name;
    const fileExtension = fileName.substring(fileName.lastIndexOf('.')).toLowerCase();
    
    if (fileExtension !== '.txt' && fileExtension !== '.docx') {
        updateStatus('不支持的文件格式，请拖拽 TXT 或 DOCX 文件', 'error');
        return;
    }
    
    updateStatus(`正在加载文件 ${fileIndex}...`, 'info');
    
    try {
        // 使用 FileReader 读取文件
        const reader = new FileReader();
        
        if (fileExtension === '.txt') {
            // 文本文件使用文本方式读取
            reader.onload = async function(e) {
                try {
                    const fileContent = e.target.result;
                    // 将文本内容转换为 base64 编码
                    const base64Content = btoa(unescape(encodeURIComponent(fileContent)));
                    
                    // 调用 Python 后端加载文件
                    const result = await eel.load_file_from_content(fileName, base64Content, fileExtension, fileIndex)();
                    
                    handleFileLoadResult(result, fileIndex, fileName);
                } catch (error) {
                    updateStatus(`错误: ${error.message}`, 'error');
                    console.error('加载文件错误:', error);
                    alert(`加载文件时发生错误: ${error.message}`);
                }
            };
            reader.readAsText(file, 'UTF-8');
        } else {
            // Word 文件使用二进制方式读取
            reader.onload = async function(e) {
                try {
                    const arrayBuffer = e.target.result;
                    // 将 ArrayBuffer 转换为 base64 编码
                    const bytes = new Uint8Array(arrayBuffer);
                    const binary = String.fromCharCode.apply(null, bytes);
                    const base64Content = btoa(binary);
                    
                    // 调用 Python 后端加载文件
                    const result = await eel.load_file_from_content(fileName, base64Content, fileExtension, fileIndex)();
                    
                    handleFileLoadResult(result, fileIndex, fileName);
                } catch (error) {
                    updateStatus(`错误: ${error.message}`, 'error');
                    console.error('加载文件错误:', error);
                    alert(`加载文件时发生错误: ${error.message}`);
                }
            };
            reader.readAsArrayBuffer(file);
        }
        
        reader.onerror = function() {
            updateStatus('读取文件失败', 'error');
        };
        
    } catch (error) {
        updateStatus(`错误: ${error.message}`, 'error');
        console.error('文件拖拽错误:', error);
        alert(`加载文件时发生错误: ${error.message}`);
    }
}
