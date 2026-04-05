"""智能求职助手工具包"""

from .resume_parser import ResumeParser
from .jd_parser import JDParser
from .match_analyzer import MatchAnalyzer
from .optimizer import ResumeOptimizer
from .interview_generator import InterviewQuestionGenerator

# 版本信息
__version__ = '1.0.0'
__author__ = 'Smart Resume Assistant Team'
__email__ = 'support@smartresume.com'

# 导出的类
__all__ = [
    'ResumeParser',
    'JDParser', 
    'MatchAnalyzer',
    'ResumeOptimizer',
    'InterviewQuestionGenerator'
]

# 默认配置
DEFAULT_CONFIG = {
    'max_file_size': 10 * 1024 * 1024,  # 10MB
    'supported_formats': ['.pdf', '.docx', '.txt'],
    'default_language': 'zh',
    'timeout': 30,
    'enable_cache': True,
    'debug_mode': False
}

# 自定义异常类
class ResumeAnalysisError(Exception):
    """简历分析错误"""
    pass

class FileFormatError(ResumeAnalysisError):
    """文件格式错误"""
    pass

class FileSizeError(ResumeAnalysisError):
    """文件大小错误"""
    pass

class ParseError(ResumeAnalysisError):
    """解析错误"""
    pass

class AnalysisError(ResumeAnalysisError):
    """分析错误"""
    pass

# 工具函数
def validate_file(file_path: str, max_size: int = None) -> bool:
    """验证文件"""
    import os
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    # 检查文件大小
    if max_size is None:
        max_size = DEFAULT_CONFIG['max_file_size']
    
    file_size = os.path.getsize(file_path)
    if file_size > max_size:
        raise FileSizeError(f"文件大小超过限制: {file_size} > {max_size}")
    
    # 检查文件格式
    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext not in DEFAULT_CONFIG['supported_formats']:
        raise FileFormatError(f"不支持的文件格式: {file_ext}")
    
    return True

def get_file_info(file_path: str) -> dict:
    """获取文件信息"""
    import os
    from datetime import datetime
    
    if not os.path.exists(file_path):
        return None
    
    stat = os.stat(file_path)
    return {
        'path': file_path,
        'name': os.path.basename(file_path),
        'size': stat.st_size,
        'extension': os.path.splitext(file_path)[1].lower(),
        'created_time': datetime.fromtimestamp(stat.st_ctime),
        'modified_time': datetime.fromtimestamp(stat.st_mtime)
    }

def clean_text(text: str) -> str:
    """清理文本"""
    import re
    
    if not text:
        return ""
    
    # 移除多余的空白字符
    text = re.sub(r'\s+', ' ', text)
    
    # 移除特殊字符
    text = re.sub(r'[^\w\s\u4e00-\u9fff.,;:!?()\[\]{}"\'-]', '', text)
    
    return text.strip()

def extract_keywords(text: str, top_k: int = 10) -> list:
    """提取关键词"""
    import re
    from collections import Counter
    
    if not text:
        return []
    
    # 简单的关键词提取（基于词频）
    words = re.findall(r'\b\w+\b', text.lower())
    
    # 过滤停用词
    stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}
    words = [word for word in words if word not in stop_words and len(word) > 1]
    
    # 统计词频
    word_counts = Counter(words)
    
    return [word for word, count in word_counts.most_common(top_k)]

def calculate_text_similarity(text1: str, text2: str) -> float:
    """计算文本相似度"""
    if not text1 or not text2:
        return 0.0
    
    # 简单的基于词汇重叠的相似度计算
    words1 = set(extract_keywords(text1, 50))
    words2 = set(extract_keywords(text2, 50))
    
    if not words1 or not words2:
        return 0.0
    
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    
    return intersection / union if union > 0 else 0.0

def format_score(score: float) -> str:
    """格式化分数"""
    return f"{score:.1f}%"

def get_score_level(score: float) -> str:
    """获取分数等级"""
    if score >= 90:
        return "优秀"
    elif score >= 80:
        return "良好"
    elif score >= 70:
        return "中等"
    elif score >= 60:
        return "及格"
    else:
        return "需要改进"

def create_analysis_summary(analysis_data: dict) -> str:
    """创建分析摘要"""
    if not analysis_data or not analysis_data.get('success'):
        return "分析失败，请检查输入数据"
    
    data = analysis_data['data']
    overall_score = data.get('overall_score', 0)
    match_level = data.get('match_level', '未知')
    
    summary = f"整体匹配度：{format_score(overall_score)}（{match_level}）\n"
    
    # 添加各项得分
    scores = {
        '技能匹配': data.get('skill_score', 0),
        '经验匹配': data.get('experience_score', 0),
        '学历匹配': data.get('education_score', 0),
        '关键词匹配': data.get('keyword_score', 0)
    }
    
    for item, score in scores.items():
        summary += f"{item}：{format_score(score)}\n"
    
    return summary

def setup_logging(level: str = 'INFO', log_file: str = None):
    """设置日志"""
    import logging
    
    # 配置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 设置日志级别
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # 配置根日志器
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # 清除现有处理器
    logger.handlers.clear()
    
    # 添加控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 添加文件处理器（如果指定了日志文件）
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def simple_cache(func):
    """简单的缓存装饰器"""
    cache = {}
    
    def wrapper(*args, **kwargs):
        # 创建缓存键
        key = str(args) + str(sorted(kwargs.items()))
        
        if key in cache:
            return cache[key]
        
        result = func(*args, **kwargs)
        cache[key] = result
        return result
    
    return wrapper

def measure_performance(func):
    """性能测量装饰器"""
    import time
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        print(f"{func.__name__} 执行时间: {execution_time:.2f}秒")
        
        return result
    
    return wrapper

def get_version_info() -> dict:
    """获取版本信息"""
    return {
        'version': __version__,
        'author': __author__,
        'email': __email__
    }

def health_check() -> dict:
    """健康检查"""
    import sys
    import platform
    
    return {
        'status': 'healthy',
        'python_version': sys.version,
        'platform': platform.platform(),
        'package_version': __version__
    }

def initialize(config: dict = None):
    """初始化工具包"""
    global DEFAULT_CONFIG
    
    # 更新配置
    if config:
        DEFAULT_CONFIG.update(config)
    
    # 设置日志
    log_level = 'DEBUG' if DEFAULT_CONFIG.get('debug_mode') else 'INFO'
    setup_logging(level=log_level)
    
    print(f"智能求职助手工具包 v{__version__} 初始化完成")
    print(f"支持的文件格式: {', '.join(DEFAULT_CONFIG['supported_formats'])}")
    print(f"最大文件大小: {DEFAULT_CONFIG['max_file_size'] / (1024*1024):.1f}MB")
    
    return True

# 自动初始化
if __name__ != '__main__':
    try:
        initialize()
    except Exception as e:
        print(f"警告：工具包初始化时出现问题: {e}")
        print("应用将继续运行，但某些功能可能受到影响")