你是一个python开发人员，现在需要你帮助设计一个智能求职助手平台，
这个平台需要能够帮助用户快速评估、优化简历，提升与岗位的匹配度，并生成面试建议，以及有可能的面试问题。项目具体信息如下。


项目名称：智能求职助手平台
🎯 核心目标：
帮助用户快速评估、优化简历，提升与岗位的匹配度，并生成面试建议。

🗂️ 一、功能模块划分
模块	功能说明	技术点
1. 简历上传	上传 .pdf / .docx 格式简历	pdfplumber / python-docx
2. JD 输入	用户粘贴职位描述或岗位链接	文本框收集
3. 匹配分析	分析简历是否满足岗位要求，标红缺失内容	NLU + 简单规则比对
4. 简历改写	针对具体岗位生成更优的简历表述	ChatGPT API / ChatGLM
5. 模拟面试	自动生成 5 个常见面试问题	LLM 提问模块
6. UI 界面	让用户上传文档、查看结果、下载优化简历	Flask + Jinja2 或 Streamlit

🧱 二、项目技术栈
方向	推荐技术
后端逻辑	Python 3.10+
文本分析	transformers, spaCy, jieba, fuzzywuzzy
文档处理	pdfplumber, python-docx, re
模型调用	OpenAI GPT-4 / ChatGLM / Claude（选其一）
前端展示	Flask + Jinja2 + Bootstrap（简单网页 UI）
可视化增强	matplotlib、wordcloud（关键词图）

以下是我建议的项目结构：请先帮我生成项目结构

smart_resume_assistant/
├── app.py                   # Flask 主程序
├── templates/
│   ├── index.html           # 上传界面
│   └── result.html          # 分析与优化结果展示
├── static/
│   └── style.css            # 页面样式（可选）
├── utils/
│   ├── parse_resume.py      # 简历解析工具
│   ├── parse_jd.py          # JD 解析与对比逻辑
│   ├── match_analyzer.py    # 匹配度分析模块
│   └── ai_optimizer.py      # GPT 接口：优化简历 & 问题生成
├── test_data/
│   ├── sample_resume.pdf
│   └── sample_jd.txt
├── requirements.txt         # 项目依赖包
└── README.md
