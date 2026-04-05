#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能求职助手平台 - 简化版
主要功能：简历上传、JD输入、匹配分析、简历优化建议、模拟面试问题生成
"""

import os
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from utils.interview_generator import InterviewQuestionGenerator

# 导入工具模块
from utils.resume_parser import ResumeParser
from utils.jd_parser import JDParser
from utils.match_analyzer import MatchAnalyzer
from utils.optimizer import ResumeOptimizer
from utils.interview_generator import InterviewQuestionGenerator
from utils.llm_parser import LLMParser, LLMParserFactory

# 创建Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'smart-resume-assistant-2024'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# 配置文件上传
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 大模型配置 - 优先级：config.py > 环境变量 > 默认配置
LLM_CONFIG = {
    'enabled': False,  # 默认关闭，需要配置API密钥后开启
    'provider': 'qwen',  # 默认使用通义千问
    'api_key': '',  # 需要用户配置
    'secret_key': '',  # 百度需要
    'model': 'qwen-plus'  # 通义千问模型
}

# 尝试从配置文件读取
try:
    from config import LLM_CONFIG as CONFIG_LLM
    if CONFIG_LLM.get('enabled'):
        provider = CONFIG_LLM.get('provider', 'qwen')
        
        if provider == 'qwen':
            qwen_config = CONFIG_LLM.get('qwen', {})
            if qwen_config.get('api_key'):
                LLM_CONFIG.update({
                    'enabled': True,
                    'provider': 'qwen',
                    'api_key': qwen_config['api_key'],
                    'model': qwen_config.get('model', 'qwen-plus')
                })
                print("从配置文件加载通义千问配置成功")
        elif provider == 'baidu':
            baidu_config = CONFIG_LLM.get('baidu', {})
            if baidu_config.get('api_key') and baidu_config.get('secret_key'):
                LLM_CONFIG.update({
                    'enabled': True,
                    'provider': 'baidu',
                    'api_key': baidu_config['api_key'],
                    'secret_key': baidu_config['secret_key']
                })
                print("从配置文件加载百度文心一言配置成功")
except ImportError:
    print("未找到config.py配置文件，使用默认配置")

# 尝试从环境变量读取配置（如果配置文件未设置）
if not LLM_CONFIG['enabled']:
    import os
    # 优先尝试通义千问
    if os.getenv('DASHSCOPE_API_KEY'):
        LLM_CONFIG.update({
            'enabled': True,
            'provider': 'qwen',
            'api_key': os.getenv('DASHSCOPE_API_KEY'),
            'model': os.getenv('QWEN_MODEL', 'qwen-plus')
        })
        print("从环境变量加载通义千问配置成功")
    # 其次尝试百度
    elif os.getenv('BAIDU_API_KEY') and os.getenv('BAIDU_SECRET_KEY'):
        LLM_CONFIG.update({
            'enabled': True,
            'provider': 'baidu',
            'api_key': os.getenv('BAIDU_API_KEY'),
            'secret_key': os.getenv('BAIDU_SECRET_KEY')
        })
        print("从环境变量加载百度文心一言配置成功")

# 初始化大模型解析器
llm_parser = None
print(f"LLM配置状态: enabled={LLM_CONFIG['enabled']}, provider={LLM_CONFIG.get('provider')}, api_key={'已配置' if LLM_CONFIG.get('api_key') else '未配置'}")
if LLM_CONFIG['enabled']:
    try:
        if LLM_CONFIG['provider'] == 'qwen':
            llm_parser = LLMParserFactory.create_qwen_parser(
                LLM_CONFIG['api_key'],
                LLM_CONFIG.get('model', 'qwen-plus')
            )
            print(f"通义千问解析器初始化成功，使用模型: {LLM_CONFIG.get('model', 'qwen-plus')}")
        elif LLM_CONFIG['provider'] == 'baidu':
            llm_parser = LLMParserFactory.create_baidu_parser(
                LLM_CONFIG['api_key'], 
                LLM_CONFIG['secret_key']
            )
            print("百度文心一言解析器初始化成功")
    except Exception as e:
        print(f"大模型解析器初始化失败: {e}")
        llm_parser = None
else:
    print("大模型解析器未启用")

print(f"最终LLM解析器状态: {'已初始化' if llm_parser else '未初始化'}")

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """主页 - 显示上传界面"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """处理文件上传和分析"""
    try:
        # 检查是否有文件上传
        if 'resume' not in request.files:
            return jsonify({
                'success': False,
                'error': '请选择简历文件'
            })
        
        file = request.files['resume']
        jd_text = request.form.get('jd_text', '').strip()
        
        # 检查文件和JD文本
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': '请选择简历文件'
            })
        
        if not jd_text:
            return jsonify({
                'success': False,
                'error': '请输入职位描述'
            })
        
        if len(jd_text) < 50:
            return jsonify({
                'success': False,
                'error': '职位描述至少需要50个字符'
            })
        
        # 检查文件类型
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': '只支持PDF和DOCX格式的文件'
            })
        
        # 保存文件 - 先从原始文件名提取扩展名
        original_filename = file.filename
        file_ext = ''
        if '.' in original_filename:
            file_ext = '.' + original_filename.rsplit('.', 1)[1].lower()
        
        # 处理文件名安全性
        filename = secure_filename(original_filename)
        
        # 生成新文件名，确保包含扩展名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = filename.rsplit('.', 1)[0] if '.' in filename else filename
        new_filename = f"{timestamp}_{base_name}{file_ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
        file.save(filepath)
        
        print(f"原始文件名: {original_filename}")
        print(f"提取扩展名: {file_ext}")
        print(f"保存文件: {new_filename}, 完整路径: {filepath}")
        try:
            # 首先提取简历文本内容
            print("提取简历文本内容...")
            resume_parser = ResumeParser()
            resume_text = resume_parser._extract_text(filepath)
            print(f"简历文本提取完成，长度: {len(resume_text) if resume_text else 0}")
            
            if not resume_text or len(resume_text.strip()) < 50:
                return jsonify({
                    'success': False,
                    'error': '无法提取简历内容或内容过短，请检查文件格式'
                })
            
            # 解析简历 - 优先使用大模型
            print("开始解析简历...")
            resume_data = None
            resume_success = False
            resume_used_llm = False
            
            if llm_parser:
                print("使用大模型解析简历...")
                try:
                    print(f"简历文本长度: {len(resume_text)}")
                    resume_result = llm_parser.parse_resume(resume_text)
                    print(f"大模型简历解析结果: success={resume_result.get('success')}, error={resume_result.get('error')}")
                    if resume_result.get('success'):
                        resume_data = resume_result.get('data', {})
                        resume_success = True
                        resume_used_llm = True
                        print("大模型简历解析成功")
                        print(f"解析得到的数据字段: {list(resume_data.keys()) if resume_data else 'None'}")
                    else:
                        print(f"大模型简历解析失败: {resume_result.get('error')}")
                except Exception as e:
                    print(f"大模型简历解析异常: {str(e)}")
                    import traceback
                    print(f"异常详情: {traceback.format_exc()}")
            else:
                print("LLM解析器未初始化，跳过大模型解析")
            
            # 如果大模型解析失败，使用传统解析器
            if not resume_success:
                print("使用传统方法解析简历...")
                try:
                    resume_data = resume_parser.parse_resume(filepath)
                    resume_success = bool(resume_data)
                    print(f"传统简历解析完成: {resume_data.keys() if resume_data else 'None'}")
                except Exception as e:
                    print(f"传统简历解析失败: {str(e)}")
                    resume_data = {}
                    resume_success = False
            
            # 解析JD - 优先使用大模型
            print("开始解析职位描述...")
            jd_data = None
            jd_success = False
            jd_used_llm = False
            
            if llm_parser:
                print("使用大模型解析JD...")
                try:
                    print(f"JD文本长度: {len(jd_text)}")
                    jd_result = llm_parser.parse_jd(jd_text)
                    print(f"大模型JD解析结果: success={jd_result.get('success')}, error={jd_result.get('error')}")
                    if jd_result.get('success'):
                        jd_data = jd_result.get('data', {})
                        jd_success = True
                        jd_used_llm = True
                        print("大模型JD解析成功")
                        print(f"解析得到的数据字段: {list(jd_data.keys()) if jd_data else 'None'}")
                    else:
                        print(f"大模型JD解析失败: {jd_result.get('error')}")
                except Exception as e:
                    print(f"大模型JD解析异常: {str(e)}")
                    import traceback
                    print(f"异常详情: {traceback.format_exc()}")
            else:
                print("LLM解析器未初始化，跳过大模型JD解析")
            
            # 如果大模型解析失败，使用传统解析器
            if not jd_success:
                print("使用传统方法解析JD...")
                try:
                    jd_parser = JDParser()
                    jd_result = jd_parser.parse_jd(jd_text)
                    if jd_result.get('success'):
                        jd_data = jd_result.get('data', {})
                        jd_success = True
                    print(f"传统JD解析完成: {jd_data.keys() if jd_data else 'None'}")
                except Exception as e:
                    print(f"传统JD解析失败: {str(e)}")
                    jd_success = False
            
            # 检查解析是否成功
            if not resume_success:
                return jsonify({
                    'success': False,
                    'error': '简历解析失败，请检查文件格式和内容'
                })
            
            if not jd_success:
                return jsonify({
                    'success': False,
                    'error': '职位描述解析失败，请检查JD内容'
                })
            
            # 匹配分析 - 优先使用大模型
            print("开始匹配分析...")
            match_result = None
            
            if llm_parser:
                print("使用大模型进行匹配分析...")
                try:
                    match_result = llm_parser.analyze_match(resume_data, jd_data)
                    if match_result.get('success'):
                        print("大模型匹配分析成功")
                    else:
                        print(f"大模型匹配分析失败: {match_result.get('error')}")
                        match_result = None
                except Exception as e:
                    print(f"大模型匹配分析异常: {str(e)}")
                    match_result = None
            
            # 如果大模型分析失败，使用传统分析器
            if not match_result or not match_result.get('success'):
                print("使用传统方法进行匹配分析...")
                try:
                    analyzer = MatchAnalyzer()
                    # 构造正确的数据格式
                    resume_for_analyzer = {'success': resume_success, 'data': resume_data}
                    jd_for_analyzer = {'success': jd_success, 'data': jd_data}
                    match_result = analyzer.analyze_match(resume_for_analyzer, jd_for_analyzer)
                    print(f"传统匹配分析完成: {type(match_result)}")
                except Exception as e:
                    print(f"传统匹配分析失败: {str(e)}")
                    match_result = {'success': False, 'error': str(e)}
            
            # AI优化建议
            print("开始生成优化建议...")
            interviewgen=InterviewQuestionGenerator()
            optimizer = ResumeOptimizer()
            try:
                # 构造优化建议生成器需要的数据格式
                resume_for_optimizer = {'success': resume_success, 'data': resume_data}
                jd_for_optimizer = {'success': jd_success, 'data': jd_data}
                optimization_result = optimizer.generate_optimization_suggestions(match_result, resume_for_optimizer, jd_for_optimizer)
                print(f"优化建议生成完成: {type(optimization_result)}")
            except Exception as e:
                print(f"优化建议生成失败: {str(e)}")
                optimization_result = {'success': False, 'error': str(e)}
            
            print("开始生成面试问题...")
            try:
                # 优先使用LLM生成带标准答案的面试问题
                if llm_parser and resume_success and jd_success:
                    print("使用大模型生成面试问题...")
                    interview_questions = llm_parser.generate_interview_questions(resume_data, jd_data)
                    print(f"大模型面试问题生成完成: {type(interview_questions)}")
                else:
                    print("使用传统方法生成面试问题...")
                    # 构造面试问题生成器需要的数据格式
                    resume_for_interview = {'success': resume_success, 'data': resume_data}
                    jd_for_interview = {'success': jd_success, 'data': jd_data}
                    interview_questions = interviewgen.generate_interview_questions(resume_for_interview, jd_for_interview)
                    print(f"传统面试问题生成完成: {type(interview_questions)}")
            except Exception as e:
                print(f"面试问题生成失败: {str(e)}")
                interview_questions = {'success': False, 'error': str(e)}
            
            # 构建返回结果
            print("构建返回结果...")
            
            # 安全地提取JD信息
            jd_job_info = {}
            if jd_data.get('success') and jd_data.get('data'):
                jd_job_info = jd_data['data'].get('job_info', {})
            
            # 确定使用的解析方法
            print(f"解析方法判断: resume_used_llm={resume_used_llm}, jd_used_llm={jd_used_llm}")
            parsing_method = "🤖 大模型解析" if (resume_used_llm and jd_used_llm) else "📋 传统规则解析"
            print(f"最终解析方法: {parsing_method}")
            
            result = {
                'resume_info': {
                    'name': resume_data.get('personal_info', {}).get('name', '未知'),
                    'email': resume_data.get('personal_info', {}).get('email', ''),
                    'phone': resume_data.get('personal_info', {}).get('phone', ''),
                    'summary': resume_data.get('summary', '')
                },
                'jd_info': {
                    'title': jd_job_info.get('title', ''),
                    'company': jd_job_info.get('company', ''),
                    'requirements': jd_data.get('data', {}).get('requirements', []) if jd_data.get('success') else []
                },
                'parsing_method': parsing_method,
                'match_analysis': match_result,
                'optimization': optimization_result,
                'interview_questions': interview_questions,
                'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            print(f"返回结果构建完成，准备发送JSON响应...")
            response_data = {
                'success': True,
                'parsing_method': 'llm' if (resume_used_llm and jd_used_llm) else 'traditional',
                'match_analysis': match_result,
                'optimization': optimization_result,
                'interview_questions': interview_questions,
                'data': result
            }
            print(f"响应数据: success={response_data['success']}, data_keys={list(response_data['data'].keys())}")
            
            return jsonify(response_data)
            
        except Exception as e:
            app.logger.error(f"分析过程出错: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'分析失败: {str(e)}'
            })
        
        finally:
            # 清理上传的文件
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
            except:
                pass
    
    except RequestEntityTooLarge:
        return jsonify({
            'success': False,
            'error': '文件大小超过16MB限制'
        })
    
    except Exception as e:
        app.logger.error(f"上传处理出错: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'处理失败: {str(e)}'
        })

@app.route('/result')
def result():
    """结果展示页面"""
    return render_template('result.html')

@app.route('/health')
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.errorhandler(404)
def not_found_error(error):
    """404错误处理"""
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    app.logger.error(f"内部服务器错误: {str(error)}")
    return jsonify({
        'success': False,
        'error': '服务器内部错误，请稍后重试'
    }), 500

@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(error):
    """文件过大错误处理"""
    return jsonify({
        'success': False,
        'error': '文件大小超过16MB限制'
    }), 413

if __name__ == '__main__':
    # 开发环境配置
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True,
        threaded=True
    )