# PDF知识库系统

一个基于windows本地部署的PDF文档知识库系统，支持文档上传、向量化存储和智能查询。

## 项目结构
pdf_knowledge_base/

├── app.py                 # Flask主应用

├── knowledge_base.py      # 知识库核心功能

├── requirements.txt       # 依赖包列表

├── run.bat               # Windows启动脚本

├── README.md             # 使用说明

└── templates/

    └── index.html         # Web界面模板

    


## 功能特性

- 📚 PDF文档批量导入
- 🔍 向量化语义搜索
- 🤖 可选智能问答（基于本地LLM）
- 🌐 Web界面交互
- 🔒 完全本地运行，保护隐私

## 系统要求

- Windows 10/11
- Python 3.8+
- 至少8GB内存（推荐16GB）
- 至少5GB可用存储空间

## 安装步骤

1. 下载项目文件到本地
2. 创建Python虚拟环境：
   bash
   python -m venv venv
3. 激活虚拟环境：
   bash
   venv\Scripts\activate
4. 安装依赖：
   bash
   pip install -r requirements.txt
5. 将PDF文件放入`pdfs`文件夹
6. 运行系统：
   bash
   python app.py

或双击`run.bat`

## 使用说明

1. 访问 http://localhost:5000
2. 上传PDF文件或使用批量导入功能
3. 在搜索框输入问题
4. 选择搜索模式（向量搜索或智能问答）
5. 查看查询结果

## 文件结构

- `app.py` - Flask Web应用
- `knowledge_base.py` - 知识库核心功能
- `templates/index.html` - Web界面
- `pdfs/` - PDF存储目录
- `chroma_db/` - 向量数据库

## 注意事项

- 首次运行会下载嵌入模型（约400MB）
- 智能问答功能需要额外下载语言模型（约1GB）
- 处理大量PDF时请耐心等待

- 确保系统有足够的内存和存储空间


