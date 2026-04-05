<div align="center">

# ResumeForge

**智能求职助手 — 简历解析 / 职位匹配 / 面试准备**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-Web%20Framework-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 功能特性

- **简历解析** — 支持 PDF、DOCX、TXT 格式上传与智能解析
- **职位匹配** — 多维度分析简历与目标岗位的匹配度（技能 / 经验 / 教育 / 关键词）
- **简历优化** — 生成个性化改进建议与技能提升方向
- **面试准备** — 针对性产出技术题、行为题与情境题

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3.8+ / Flask |
| 文档处理 | PyPDF2 / python-docx |
| 中文分词 | jieba |
| 前端 | HTML5 / CSS3 / JavaScript / Bootstrap 5 / Font Awesome |

## 项目结构

```
smart_resume_assistant_small/
├── app.py                    # Flask 主应用
├── requirements.txt          # 依赖清单
├── static/
│   └── style.css             # 样式
├── templates/
│   └── index.html            # 主页模板
└── utils/
    ├── resume_parser.py      # 简历解析器
    ├── jd_parser.py          # 职位描述解析器
    ├── match_analyzer.py     # 匹配度分析器
    ├── optimizer.py          # 简历优化器
    └── interview_generator.py # 面试问题生成器
```

## 快速开始

**1. 克隆项目**

```bash
git clone https://github.com/<your-username>/ResumeForge.git
cd ResumeForge
```

**2. 创建虚拟环境（推荐）**

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/macOS
```

**3. 安装依赖**

```bash
pip install -r requirements.txt
```

**4. 启动应用**

```bash
python app.py
```

浏览器访问 **http://localhost:5000** 即可使用。

## 使用方式

1. **上传简历** — 拖拽或点击上传 PDF / DOCX / TXT 文件（最大 10MB）
2. **粘贴职位描述** — 填写目标岗位的完整 JD
3. **开始分析** — 点击按钮，系统自动输出匹配度评分、技能差距、优化建议与面试题

## 许可证

[MIT](LICENSE)
