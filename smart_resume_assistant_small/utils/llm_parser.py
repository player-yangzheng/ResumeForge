import re
import json
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import time

@dataclass
class LLMConfig:
    """大模型配置"""
    provider: str  # 'baidu', 'qwen', 'xunfei', 'tencent'
    api_key: str
    secret_key: str = None
    app_id: str = None
    base_url: str = None
    model: str = None  # 模型名称

class LLMParser:
    """基于大模型的智能解析器"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.access_token = None
        self.token_expires_at = 0
        
    def _get_baidu_access_token(self) -> str:
        """获取百度文心一言访问令牌"""
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token
            
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.config.api_key,
            "client_secret": self.config.secret_key
        }
        
        try:
            response = requests.post(url, params=params, timeout=10)
            result = response.json()
            if "access_token" in result:
                self.access_token = result["access_token"]
                self.token_expires_at = time.time() + result.get("expires_in", 3600) - 300  # 提前5分钟刷新
                return self.access_token
            else:
                raise Exception(f"获取访问令牌失败: {result}")
        except Exception as e:
            raise Exception(f"获取百度访问令牌失败: {str(e)}")
    
    def _call_baidu_api(self, prompt: str, model: str = "ernie-speed") -> str:
        """调用百度文心一言API"""
        access_token = self._get_baidu_access_token()
        url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/{model}?access_token={access_token}"
        
        payload = {
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "top_p": 0.8,
            "penalty_score": 1.0
        }
        
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            result = response.json()
            if "result" in result:
                return result["result"]
            else:
                raise Exception(f"API调用失败: {result}")
        except Exception as e:
            raise Exception(f"调用百度API失败: {str(e)}")
    
    def _call_qwen_api(self, prompt: str, model: str = "qwen-plus") -> str:
        """调用通义千问API"""
        url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        
        payload = {
            "model": self.config.model or model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "top_p": 0.8
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.config.api_key}'
        }
        
        # 添加重试机制
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=60)
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
                else:
                    raise Exception(f"API调用失败: {result}")
            except requests.exceptions.Timeout as e:
                if attempt < max_retries:
                    print(f"通义千问API超时，正在重试 ({attempt + 1}/{max_retries})...")
                    continue
                else:
                    raise Exception(f"调用通义千问API超时: {str(e)}")
            except Exception as e:
                raise Exception(f"调用通义千问API失败: {str(e)}")
    
    def _call_llm_api(self, prompt: str) -> str:
        """调用大模型API"""
        if self.config.provider == "baidu":
            return self._call_baidu_api(prompt)
        elif self.config.provider == "qwen":
            return self._call_qwen_api(prompt)
        else:
            raise NotImplementedError(f"暂不支持 {self.config.provider} 提供商")
    
    def parse_resume(self, text: str) -> Dict[str, Any]:
        """使用大模型解析简历"""
        prompt = f"""
请仔细分析以下简历内容，提取所有关键信息并以JSON格式返回。要求：
1. 严格按照指定的JSON格式输出
2. 如果某个字段无法提取，设置为null或空数组
3. 技能列表请尽可能详细分类，包括所有提到的技术栈
4. 工作经历按时间倒序排列，详细提取工作描述和成就
5. 项目经历要包含使用的技术和具体成果
6. 仔细识别编程语言、框架、数据库、工具等不同类别的技能

简历内容：
{text}

请返回以下JSON格式：
{{
  "personal_info": {{
    "name": "姓名",
    "email": "邮箱",
    "phone": "电话",
    "location": "所在地",
    "age": "年龄",
    "gender": "性别"
  }},
  "education": [
    {{
      "school": "学校名称",
      "major": "专业",
      "degree": "学历",
      "start_date": "开始时间",
      "end_date": "结束时间",
      "gpa": "成绩"
    }}
  ],
  "work_experience": [
    {{
      "company": "公司名称",
      "position": "职位",
      "start_date": "开始时间",
      "end_date": "结束时间",
      "description": "工作描述",
      "achievements": ["成就1", "成就2"]
    }}
  ],
  "skills": {{
    "programming_languages": ["编程语言列表"],
    "frameworks": ["框架列表"],
    "databases": ["数据库列表"],
    "tools": ["工具列表"],
    "soft_skills": ["软技能列表"]
  }},
  "projects": [
    {{
      "name": "项目名称",
      "description": "项目描述",
      "technologies": ["使用技术"],
      "role": "担任角色",
      "achievements": ["项目成果"]
    }}
  ],
  "certifications": ["证书列表"],
  "summary": "个人总结/优势"
}}

只返回JSON，不要其他内容：
"""
        
        try:
            response = self._call_llm_api(prompt)
            # 尝试提取JSON
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                parsed_data = json.loads(json_str)
                return {
                    'success': True,
                    'data': parsed_data,
                    'raw_text': text
                }
            else:
                raise ValueError("无法从响应中提取JSON")
        except Exception as e:
            return {
                'success': False,
                'error': f"简历解析失败: {str(e)}",
                'raw_text': text
            }
    
    def parse_jd(self, text: str) -> Dict[str, Any]:
        """使用大模型解析职位描述"""
        prompt = f"""
请仔细分析以下职位描述(JD)内容，提取所有关键信息并以JSON格式返回。要求：
1. 严格按照指定的JSON格式输出
2. 如果某个字段无法提取，设置为null或空数组
3. 技能要求请尽可能详细分类，区分必备技能和优先技能
4. 薪资范围请提取具体数字
5. 仔细识别编程语言、框架、数据库、工具等不同类别的技能要求
6. 工作职责要详细列出，包含具体的技术要求
7. 经验要求要提取具体年数

职位描述内容：
{text}

请返回以下JSON格式：
{{
  "job_info": {{
    "title": "职位名称",
    "company": "公司名称",
    "location": "工作地点",
    "salary_min": "最低薪资(数字)",
    "salary_max": "最高薪资(数字)",
    "work_type": "工作类型(全职/兼职/实习)",
    "experience_required": "所需工作经验(年数)",
    "education_required": "学历要求"
  }},
  "requirements": {{
    "must_have_skills": ["必备技能列表"],
    "preferred_skills": ["优先技能列表"],
    "programming_languages": ["编程语言要求"],
    "frameworks": ["框架要求"],
    "databases": ["数据库要求"],
    "tools": ["工具要求"],
    "soft_skills": ["软技能要求"]
  }},
  "responsibilities": ["工作职责列表"],
  "benefits": ["福利待遇列表"],
  "company_info": {{
    "industry": "行业",
    "size": "公司规模",
    "description": "公司描述"
  }},
  "keywords": ["关键词列表"]
}}

只返回JSON，不要其他内容：
"""
        
        try:
            response = self._call_llm_api(prompt)
            # 尝试提取JSON
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                parsed_data = json.loads(json_str)
                return {
                    'success': True,
                    'data': parsed_data,
                    'raw_text': text
                }
            else:
                raise ValueError("无法从响应中提取JSON")
        except Exception as e:
            return {
                'success': False,
                'error': f"JD解析失败: {str(e)}",
                'raw_text': text
            }
    
    def analyze_match(self, resume_data: Dict, jd_data: Dict) -> Dict[str, Any]:
        """使用大模型分析简历与JD的匹配度"""
        prompt = f"""
请分析以下简历和职位描述的匹配度，并提供详细的分析报告。

简历信息：
{json.dumps(resume_data, ensure_ascii=False, indent=2)}

职位描述：
{json.dumps(jd_data, ensure_ascii=False, indent=2)}

请从以下维度进行分析并以JSON格式返回：

{{
  "overall_match_score": "总体匹配度(0-100)",
  "detailed_analysis": {{
    "skills_match": {{
      "score": "技能匹配度(0-100)",
      "matched_skills": ["匹配的技能"],
      "missing_skills": ["缺失的技能"],
      "analysis": "技能匹配分析"
    }},
    "experience_match": {{
      "score": "经验匹配度(0-100)",
      "analysis": "经验匹配分析"
    }},
    "education_match": {{
      "score": "学历匹配度(0-100)",
      "analysis": "学历匹配分析"
    }}
  }},
  "strengths": ["候选人优势"],
  "weaknesses": ["候选人劣势"],
  "recommendations": ["改进建议"],
  "interview_questions": ["推荐面试问题"],
  "summary": "总体评价"
}}

只返回JSON，不要其他内容：
"""
        
        try:
            response = self._call_llm_api(prompt)
            # 尝试提取JSON
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                parsed_data = json.loads(json_str)
                return {
                    'success': True,
                    'data': parsed_data
                }
            else:
                raise ValueError("无法从响应中提取JSON")
        except Exception as e:
            return {
                'success': False,
                'error': f"匹配分析失败: {str(e)}"
            }
    
    def generate_interview_questions(self, resume_data: Dict[str, Any], jd_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成带标准答案的面试问题"""
        try:
            # 构建提示词
            prompt = f"""
请根据以下简历信息和职位描述，生成5个具有针对性的面试问题，每个问题都要包含标准答案。
问题应该涵盖技术技能、项目经验、行为面试等方面，并且要结合具体的职位要求。

简历信息：
{json.dumps(resume_data, ensure_ascii=False, indent=2)}

职位描述：
{json.dumps(jd_data, ensure_ascii=False, indent=2)}

请按照以下JSON格式返回：
{{
    "interview_questions": [
        {{
            "question": "具体的面试问题",
            "type": "技术/行为/项目经验",
            "difficulty": "初级/中级/高级",
            "standard_answer": "详细的标准答案，包含关键要点",
            "evaluation_points": ["评分要点1", "评分要点2", "评分要点3"]
        }}
    ]
}}

要求：
1. 问题要具体且有针对性
2. 标准答案要详细且实用
3. 评分要点要明确
4. 涵盖不同难度级别
5. 结合职位的实际业务场景
"""
            
            # 调用LLM API
            response_text = self._call_llm_api(prompt)
            
            # 提取JSON
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if not json_match:
                raise ValueError("无法从响应中提取JSON数据")
            
            json_str = json_match.group()
            parsed_data = json.loads(json_str)
            
            return {
                'success': True,
                'data': parsed_data,
                'raw_text': response_text
            }
            
        except Exception as e:
            print(f"面试问题生成失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'raw_text': response_text if 'response_text' in locals() else ''
            }

# 使用示例和配置
class LLMParserFactory:
    """大模型解析器工厂"""
    
    @staticmethod
    def create_baidu_parser(api_key: str, secret_key: str) -> LLMParser:
        """创建百度文心一言解析器"""
        config = LLMConfig(
            provider="baidu",
            api_key=api_key,
            secret_key=secret_key
        )
        return LLMParser(config)
    
    @staticmethod
    def create_qwen_parser(api_key: str, model: str = "qwen-plus") -> LLMParser:
        """创建通义千问解析器"""
        config = LLMConfig(
            provider="qwen",
            api_key=api_key,
            model=model
        )
        return LLMParser(config)
    
    @staticmethod
    def get_default_config() -> Dict[str, str]:
        """获取默认配置说明"""
        return {
            "baidu": {
                "description": "百度文心一言 - 免费额度：ERNIE-Speed-8K RPM=300, TPM=300000",
                "signup_url": "https://console.bce.baidu.com/qianfan/ais/console/applicationConsole/application",
                "api_key": "在百度智能云千帆平台获取API Key",
                "secret_key": "在百度智能云千帆平台获取Secret Key"
            },
            "qwen": {
                "description": "阿里通义千问 - 支持多种模型：qwen-plus, qwen-turbo, qwen-max等",
                "signup_url": "https://dashscope.console.aliyun.com/",
                "api_key": "在阿里云百炼平台获取API Key",
                "models": ["qwen-plus", "qwen-turbo", "qwen-max", "qwen-max-latest"]
            }
        }