# 字幕核对工具 - 技术文档

## 项目概述

字幕核对工具是一个基于 Python 和 Eel 框架开发的桌面应用程序，用于比对 TXT 和 Word 文档的字幕内容。该工具支持实时编辑、差异高亮显示，并且可以忽略标点符号、空格和换行符进行比对。

## 技术栈

### 后端技术
- **Python 3.7+**: 主要编程语言
- **Eel 0.16.0+**: 用于创建桌面应用程序的轻量级框架
  - 基于 Chrome 浏览器运行，提供类似原生应用的体验
  - 允许 Python 作为后端，HTML/CSS/JavaScript 作为前端
- **python-docx 1.1.0+**: 用于读取和处理 Word (.docx) 文件
- **difflib**: Python 标准库，用于文本比对和差异分析
- **re**: Python 标准库，用于正则表达式处理（文本规范化）

### 前端技术
- **HTML5**: 页面结构
- **CSS3**: 样式设计，包括渐变、响应式布局、自定义滚动条
- **JavaScript (ES6+)**: 前端交互逻辑
- **Eel.js**: Eel 框架提供的 JavaScript 库，用于前后端通信

## 项目结构

```
TxtTest/
├── main.py                 # 主程序入口，Eel 服务器启动文件
├── requirements.txt        # Python 依赖包列表
├── README.md              # 技术文档（本文件）
├── app/                   # 应用程序核心模块
│   ├── __init__.py        # Python 包初始化文件
│   ├── file_handler.py    # 文件处理模块（读取 TXT 和 Word 文件）
│   └── text_compare.py    # 文本比对模块（差异分析和高亮）
└── web/                   # 前端文件目录
    ├── index.html         # 主页面 HTML
    ├── css/
    │   └── style.css      # 样式表文件
    └── js/
        └── main.js        # 前端 JavaScript 逻辑
```

## 核心功能模块

### 1. 文件处理模块 (`app/file_handler.py`)

#### 主要函数

##### `normalize_text(text: str) -> str`
- **功能**: 规范化文本，移除所有标点符号、空格和换行符
- **参数**: 
  - `text`: 原始文本内容
- **返回**: 规范化后的文本（仅保留中英文字符和数字）
- **实现原理**: 使用正则表达式 `r'[^\w\u4e00-\u9fff]'` 匹配并移除所有非字母数字字符
- **用途**: 在比对 Word 文件时，忽略格式差异，只比较实际内容

##### `read_txt_file(file_path: str) -> Tuple[str, str]`
- **功能**: 读取 TXT 文件
- **参数**: 
  - `file_path`: TXT 文件路径
- **返回**: `(原始文本, 规范化文本)` 元组
- **编码支持**: 依次尝试 UTF-8、GBK、latin-1 编码，确保兼容性

##### `read_docx_file(file_path: str) -> Tuple[str, str]`
- **功能**: 读取 Word (.docx) 文件
- **参数**: 
  - `file_path`: Word 文件路径
- **返回**: `(原始文本, 规范化文本)` 元组
- **实现原理**: 使用 `python-docx` 库提取所有段落文本，用换行符连接
- **注意事项**: 仅支持 .docx 格式，不支持旧的 .doc 格式

##### `read_file(file_path: str) -> Tuple[str, str]`
- **功能**: 根据文件扩展名自动选择读取方式
- **参数**: 
  - `file_path`: 文件路径
- **返回**: `(原始文本, 规范化文本)` 元组
- **支持格式**: .txt、.docx

### 2. 文本比对模块 (`app/text_compare.py`)

#### 核心类

##### `TextDiff`
- **功能**: 表示文本差异的数据类
- **属性**:
  - `text`: 差异文本内容
  - `status`: 差异状态 (`'equal'`, `'delete'`, `'insert'`, `'replace'`)
  - `start_pos`: 在原始文本中的起始位置
  - `end_pos`: 在原始文本中的结束位置
- **方法**:
  - `to_dict()`: 转换为字典格式，用于 JSON 序列化

#### 主要函数

##### `compare_texts(text1: str, text2: str) -> Tuple[List[TextDiff], List[TextDiff]]`
- **功能**: 比较两个文本，返回差异信息列表
- **参数**: 
  - `text1`: 第一个文本
  - `text2`: 第二个文本
- **返回**: `(文本1的差异列表, 文本2的差异列表)` 元组
- **实现原理**: 使用 `difflib.SequenceMatcher` 进行文本比对，识别四种差异类型：
  - `equal`: 相同的部分
  - `delete`: 文本1中有但文本2中没有的部分
  - `insert`: 文本2中有但文本1中没有的部分
  - `replace`: 两个文本都有但内容不同的部分

##### `simple_compare_original_texts(text1: str, text2: str) -> Tuple[List[Dict], List[Dict]]`
- **功能**: 直接比较原始文本（不进行规范化处理）
- **参数**: 
  - `text1`: 第一个文本
  - `text2`: 第二个文本
- **返回**: `(文本1的差异字典列表, 文本2的差异字典列表)` 元组
- **用途**: 用于在界面上直接比较和显示原始文本的差异

### 3. 主程序模块 (`main.py`)

#### Eel 暴露的函数（API 接口）

##### `load_file(file_path: str, file_index: int) -> dict`
- **功能**: 加载文件（TXT 或 Word）
- **参数**: 
  - `file_path`: 文件路径
  - `file_index`: 文件索引（1 或 2）
- **返回**: 包含文件内容和状态信息的字典
  ```python
  {
      'success': bool,
      'original_text': str,      # 原始文本内容
      'normalized_text': str,    # 规范化文本内容
      'file_name': str,          # 文件名
      'message': str             # 状态消息
  }
  ```
- **错误处理**: 如果加载失败，返回 `success: False` 和错误信息

##### `compare_files() -> dict`
- **功能**: 比较两个文件的内容
- **返回**: 包含比对结果的字典
  ```python
  {
      'success': bool,
      'diffs1': List[Dict],      # 文件1的差异列表
      'diffs2': List[Dict],      # 文件2的差异列表
      'message': str
  }
  ```
- **差异字典格式**:
  ```python
  {
      'text': str,               # 文本内容
      'status': str,             # 'equal', 'delete', 'insert', 'replace'
      'start_pos': int,          # 起始位置
      'end_pos': int             # 结束位置
  }
  ```

##### `update_file_content(file_index: int, new_content: str) -> dict`
- **功能**: 更新文件内容（实时编辑，不保存到源文件）
- **参数**: 
  - `file_index`: 文件索引（1 或 2）
  - `new_content`: 新的文件内容
- **返回**: 包含更新状态的字典
- **用途**: 当用户在界面上编辑文本时，实时更新后端存储的内容

##### `get_file_content(file_index: int) -> dict`
- **功能**: 获取当前文件内容
- **参数**: 
  - `file_index`: 文件索引（1 或 2）
- **返回**: 包含文件内容的字典

##### `compare_with_normalization() -> dict`
- **功能**: 使用规范化文本进行比较（忽略标点、空格、换行）
- **返回**: 包含比对结果的字典（包含规范化文本信息）
- **当前实现**: 简化版本，直接比较原始文本

#### 主函数

##### `main()`
- **功能**: 启动 Eel 应用
- **配置**:
  - 使用 Chrome 浏览器模式
  - 窗口大小: 1400x900 像素
  - 端口: 自动选择可用端口

### 4. 前端模块 (`web/`)

#### HTML 结构 (`web/index.html`)

- **头部区域**: 标题和副标题
- **文件控制区域**: 文件选择按钮和比对按钮
- **比对选项**: 忽略标点符号的选项（复选框）
- **状态栏**: 显示操作状态和消息
- **内容显示区域**: 双栏布局，左右各显示一个文件的内容
- **编辑器**: 使用 `contenteditable` 属性实现可编辑的文本区域

#### CSS 样式 (`web/css/style.css`)

- **设计风格**: 现代化渐变背景、圆角卡片、阴影效果
- **布局**: 
  - 使用 CSS Grid 实现双栏布局
  - 响应式设计，小屏幕下自动切换为单栏
- **颜色方案**:
  - 主题色: 紫色渐变 (`#667eea` 到 `#764ba2`)
  - 差异高亮:
    - 相同: 透明背景
    - 不同: 红色背景 (`#ffe6e6`)
    - 缺失: 黄色背景，删除线 (`#fff3cd`)
    - 新增: 绿色背景 (`#d4edda`)
  - 拖拽状态:
    - 悬停背景: 浅蓝色 (`#e8e8ff`)
    - 悬停边框: 紫色虚线 (`#667eea`)
- **交互效果**: 
  - 按钮悬停动画、淡入动画、自定义滚动条
  - 拖拽上传时的视觉反馈（边框和背景色变化）
  - 使用 CSS 过渡动画提供流畅体验

#### JavaScript 逻辑 (`web/js/main.js`)

##### 主要函数

###### `selectFile(fileIndex)`
- **功能**: 触发文件选择对话框
- **实现**: 通过隐藏的 `<input type="file">` 元素实现

###### `handleFileSelect(event)`
- **功能**: 处理文件选择事件
- **流程**:
  1. 获取选中的文件
  2. 调用后端 `load_file` 函数
  3. 更新界面显示文件内容
  4. 如果两个文件都已加载，自动触发比对

###### `performCompare()`
- **功能**: 执行文本比对
- **流程**:
  1. 获取编辑器当前内容
  2. 更新后端内容
  3. 调用后端 `compare_files` 函数
  4. 应用高亮显示

###### `applyHighlights(editorId, diffs)`
- **功能**: 在编辑器中应用文本高亮
- **实现原理**:
  1. 将文本差异信息转换为 HTML
  2. 为不同状态的文本添加对应的 CSS 类
  3. 使用 `innerHTML` 更新编辑器内容
- **高亮类**:
  - `highlight-equal`: 相同内容
  - `highlight-different`: 不同内容
  - `highlight-missing`: 缺失内容
  - `highlight-added`: 新增内容

###### `onEditorInput(fileIndex)`
- **功能**: 处理编辑器内容输入事件
- **特性**: 
  - 实时更新后端内容
  - 延迟自动重新比对（1秒延迟，避免频繁比对）

###### `syncScroll(editorIndex)`
- **功能**: 同步两个编辑器的滚动位置
- **实现原理**: 
  - 使用比例同步算法，计算当前滚动位置占总滚动高度的比例
  - 将相同比例应用到另一个编辑器，确保内容高度不同时也能正确同步
  - 使用 `requestAnimationFrame` 优化性能，避免频繁的 DOM 操作
  - 通过 `isScrolling` 标志防止滚动循环触发
- **特性**: 
  - 同时同步垂直滚动和水平滚动
  - 支持内容高度不同的情况

###### `handleDragOver(event)`
- **功能**: 处理文件拖拽悬停事件
- **实现**: 
  - 阻止默认行为，允许文件拖放
  - 检查拖拽内容是否为文件
  - 添加视觉反馈样式（`drag-over` 类）

###### `handleDragLeave(event)`
- **功能**: 处理文件拖拽离开事件
- **实现**: 移除视觉反馈样式

###### `handleDrop(event, fileIndex)`
- **功能**: 处理文件拖拽放置事件
- **实现流程**:
  1. 阻止默认行为
  2. 获取拖拽的文件
  3. 验证文件类型（TXT 或 DOCX）
  4. 使用 FileReader 读取文件内容
  5. 调用后端 API 加载文件
  6. 更新界面显示
- **特性**: 
  - 支持 TXT 和 DOCX 文件
  - 自动识别文件类型并选择相应的读取方式
  - 提供错误处理和用户反馈

## 使用方法

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行程序

```bash
python main.py
```

程序会自动打开 Chrome 浏览器窗口（或使用系统默认浏览器），显示应用程序界面。

### 操作步骤

1. **加载文件 1**: 
   - 方式一：点击"文件 1"的"选择文件"按钮，选择 TXT 或 Word 文件
   - 方式二：直接将文件拖拽到左侧编辑器容器中
2. **加载文件 2**: 
   - 方式一：点击"文件 2"的"选择文件"按钮，选择要比对的文件
   - 方式二：直接将文件拖拽到右侧编辑器容器中
3. **开始比对**: 点击"开始比对"按钮，或等待自动比对（两个文件都加载后自动触发）
4. **查看差异**: 差异内容会以不同颜色高亮显示：
   - 红色背景: 内容不同
   - 黄色背景+删除线: 文件1中有但文件2中没有
   - 绿色背景: 文件2中有但文件1中没有
5. **实时编辑**: 可以直接在编辑器中修改文本内容，修改后会自动重新比对
6. **同步滚动**: 滚动任意一个编辑器时，另一个编辑器会自动同步滚动位置，方便对比查看
7. **清空内容**: 点击"清空"按钮可以清空所有内容

### 注意事项

1. **Word 文件格式**: 仅支持 .docx 格式，不支持旧的 .doc 格式
2. **文件编码**: TXT 文件支持 UTF-8、GBK 编码，程序会自动尝试不同的编码
3. **编辑功能**: 在编辑器中的修改不会保存到源文件，只在当前会话中有效
4. **比对方式**: 当前版本直接比较原始文本，规范化功能在代码中已实现但未完全集成到比对流程

## API 接口文档

### Python 后端 API（通过 Eel 暴露）

所有 API 函数都通过 `@eel.expose` 装饰器暴露给前端，前端可以通过 `eel.function_name()` 调用。

#### `load_file(file_path: str, file_index: int) -> dict`

加载文件到指定位置。

**参数**:
- `file_path` (str): 文件的完整路径
- `file_index` (int): 文件索引，1 或 2

**返回**:
```python
{
    'success': bool,              # 是否成功
    'original_text': str,         # 原始文本内容（成功时）
    'normalized_text': str,       # 规范化文本内容（成功时）
    'file_name': str,             # 文件名（成功时）
    'message': str,               # 状态消息
    'error': str                  # 错误信息（失败时）
}
```

**示例**:
```python
result = await eel.load_file("/path/to/file.txt", 1)()
if result['success']:
    print(f"文件内容: {result['original_text']}")
```

#### `compare_files() -> dict`

比较当前加载的两个文件。

**返回**:
```python
{
    'success': bool,
    'diffs1': List[Dict],         # 文件1的差异列表
    'diffs2': List[Dict],         # 文件2的差异列表
    'message': str
}
```

**差异字典格式**:
```python
{
    'text': str,                  # 文本片段
    'status': str,                # 'equal', 'delete', 'insert', 'replace'
    'start_pos': int,             # 起始位置
    'end_pos': int                # 结束位置
}
```

**示例**:
```python
result = await eel.compare_files()()
if result['success']:
    for diff in result['diffs1']:
        print(f"{diff['status']}: {diff['text']}")
```

#### `update_file_content(file_index: int, new_content: str) -> dict`

更新文件内容（不保存到源文件）。

**参数**:
- `file_index` (int): 文件索引，1 或 2
- `new_content` (str): 新的文件内容

**返回**:
```python
{
    'success': bool,
    'message': str
}
```

**示例**:
```python
result = await eel.update_file_content(1, "新的文本内容")()
```

#### `get_file_content(file_index: int) -> dict`

获取当前文件内容。

**参数**:
- `file_index` (int): 文件索引，1 或 2

**返回**:
```python
{
    'success': bool,
    'content': str,               # 文件内容
    'error': str                  # 错误信息（失败时）
}
```

## 技术实现细节

### 文本规范化算法

文本规范化使用正则表达式 `r'[^\w\u4e00-\u9fff]'` 来移除所有非字母数字字符。这个正则表达式的含义：
- `\w`: 匹配字母、数字和下划线（ASCII 字符）
- `\u4e00-\u9fff`: Unicode 范围，匹配中文字符
- `[^...]`: 否定字符类，匹配不在括号内的字符
- 结果: 保留所有字母、数字、下划线和中文字符，移除其他所有字符（包括标点、空格、换行等）

### 文本比对算法

使用 Python 标准库 `difflib.SequenceMatcher` 进行文本比对。该算法基于最长公共子序列（LCS）算法，能够高效地找出两个序列的差异。

比对过程：
1. 创建 `SequenceMatcher` 对象
2. 调用 `get_opcodes()` 方法获取差异操作码
3. 操作码类型：
   - `equal`: 相同部分
   - `delete`: 删除部分
   - `insert`: 插入部分
   - `replace`: 替换部分
4. 将操作码转换为 `TextDiff` 对象列表

### 高亮显示实现

前端使用 `contenteditable` div 元素作为编辑器，通过以下方式实现高亮：

1. **获取差异信息**: 从后端获取文本差异列表
2. **构建 HTML**: 将每个差异片段包装在 `<span>` 标签中，添加对应的 CSS 类
3. **更新内容**: 使用 `innerHTML` 属性更新编辑器内容
4. **样式应用**: CSS 类定义不同的背景色和文本样式

**注意事项**: 使用 `innerHTML` 会清除 `contenteditable` 的编辑状态，但用户仍可以继续编辑（浏览器会重新设置编辑能力）。

### 实时编辑和自动比对

实现机制：
1. 监听编辑器的 `input` 事件
2. 事件触发时，调用后端 `update_file_content` 更新内容
3. 使用 `setTimeout` 延迟触发比对（1秒延迟，避免频繁比对）
4. 比对完成后重新应用高亮

### 滚动同步

实现机制：
1. 监听编辑器容器的 `scroll` 事件
2. 使用 `isScrolling` 标志防止循环触发
3. 计算滚动比例（当前滚动位置 / 总滚动高度）
4. 将相同比例应用到另一个编辑器容器
5. 使用 `requestAnimationFrame` 优化性能
6. 同时同步垂直滚动和水平滚动

**优势**:
- 支持内容高度不同的情况
- 性能优化，避免频繁 DOM 操作
- 防止滚动循环触发

### 拖拽上传

实现机制：
1. 在编辑器容器上监听拖拽事件：
   - `ondragover`: 处理拖拽悬停，显示视觉反馈
   - `ondragleave`: 处理拖拽离开，移除视觉反馈
   - `ondrop`: 处理文件放置，加载文件
2. 验证文件类型（仅支持 TXT 和 DOCX）
3. 使用 FileReader API 读取文件内容
4. 根据文件类型选择读取方式：
   - TXT 文件：使用 `readAsText` 读取文本
   - DOCX 文件：使用 `readAsArrayBuffer` 读取二进制
5. 将文件内容转换为 base64 编码
6. 调用后端 API 加载文件
7. 更新界面显示

**视觉反馈**:
- 拖拽悬停时：编辑器容器显示蓝色边框和浅蓝色背景
- 使用 CSS 过渡动画，提供流畅的用户体验

## 扩展和优化建议

### 当前实现的局限性

1. **规范化比对**: 虽然规范化功能已实现，但当前比对直接使用原始文本。可以改进为基于规范化文本比对，但在原始文本上显示差异。
2. **大文件处理**: 对于非常大的文件，可能需要分块加载和比对。
3. **性能优化**: 频繁的文本比对可能影响性能，可以添加防抖和节流机制。
4. **保存功能**: 当前不支持将编辑后的内容保存到文件。

### 可能的改进方向

1. **保存功能**: 添加保存编辑内容到文件的功能
2. **导出功能**: 导出比对报告（HTML、PDF 等格式）
3. **批量比对**: 支持同时比对多个文件
4. **配置文件**: 支持自定义比对规则和显示样式
5. **历史记录**: 保存比对历史记录
6. **搜索功能**: 在文本中搜索特定内容
7. **统计信息**: 显示差异统计信息（差异数量、相似度等）

## 故障排除

### 常见问题

1. **无法加载 Word 文件**
   - 确保安装了 `python-docx`: `pip install python-docx`
   - 确保文件格式是 .docx（不是 .doc）

2. **中文显示乱码**
   - 确保 TXT 文件使用 UTF-8 或 GBK 编码
   - 程序会自动尝试不同的编码，但某些特殊编码可能不支持

3. **Eel 无法启动**
   - 确保安装了 Eel: `pip install eel`
   - 确保 Chrome 浏览器已安装（Eel 需要浏览器运行）

4. **比对结果不准确**
   - 当前实现直接比较原始文本，如果文件格式差异较大，可能需要使用规范化比对
   - 可以修改代码使用 `compare_with_normalization` 函数

## 许可证

本项目仅供学习和参考使用。

## 作者

字幕核对工具开发团队

## 更新日志

### v1.1.0 (最新版本)
- **新增拖拽上传功能**: 支持将文件直接拖拽到编辑器容器中加载
  - 拖拽时显示视觉反馈（蓝色边框和背景高亮）
  - 支持 TXT 和 DOCX 文件格式
  - 自动识别文件类型并加载
- **改进同步滚动功能**: 优化两个编辑器容器的滚动同步
  - 使用比例同步算法，确保内容高度不同时也能正确同步
  - 使用 `requestAnimationFrame` 优化性能
  - 防止滚动循环触发，提升稳定性

### v1.0.0 (初始版本)
- 实现基本的文件加载功能（TXT 和 Word）
- 实现文本比对和差异高亮显示
- 实现实时编辑功能
- 实现双栏布局和滚动同步
- 添加现代化 UI 设计
