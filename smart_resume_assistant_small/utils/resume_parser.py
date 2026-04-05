import re
import os
from typing import Dict, List, Optional, Any
from pathlib import Path

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None
    print("警告：PyPDF2库未安装，PDF文件解析功能将不可用")

try:
    from docx import Document
except ImportError:
    Document = None
    print("警告：python-docx库未安装，DOCX文件解析功能将不可用")

class ResumeParser:
    """简化版简历解析器"""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.txt']
        self.max_file_size = 16 * 1024 * 1024  # 16MB
        
        # 技能关键词库（简化版）
        self.skill_keywords = {
            'programming': [
                'python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
                'html', 'css', 'sql', 'r', 'matlab', 'scala', 'kotlin', 'swift', 'typescript'
            ],
            'frameworks': [
                'django', 'flask', 'spring', 'react', 'vue', 'angular', 'node.js', 'express',
                'laravel', 'rails', 'asp.net', 'bootstrap', 'jquery', 'tensorflow', 'pytorch'
            ],
            'databases': [
                'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sqlite', 'elasticsearch',
                'cassandra', 'dynamodb', 'neo4j'
            ],
            'tools': [
                'git', 'docker', 'kubernetes', 'jenkins', 'aws', 'azure', 'gcp', 'linux',
                'nginx', 'apache', 'postman', 'jira', 'confluence', 'slack'
            ],
            'soft_skills': [
                '团队合作', '沟通能力', '领导力', '项目管理', '问题解决', '创新思维',
                '学习能力', '适应能力', 'responsibility', '执行力'
            ]
        }
        
        # 教育关键词
        self.education_keywords = [
            '学士', '硕士', '博士', '本科', '研究生', '大学', '学院', '专业',
            'bachelor', 'master', 'phd', 'university', 'college', 'degree'
        ]
        
        # 工作经验关键词
        self.experience_keywords = [
            '工作经验', '项目经验', '实习经验', '工作经历', '项目经历',
            'experience', 'work', 'project', 'internship', 'employment'
        ]
    
    def parse_resume(self, file_path: str) -> Dict[str, Any]:
        """解析简历文件"""
        try:
            # 验证文件
            if not self._validate_file(file_path):
                raise ValueError("文件验证失败")
            
            # 提取文本
            text = self._extract_text(file_path)
            if not text:
                raise ValueError("无法提取文件内容")
            
            # 解析内容
            parsed_data = self._parse_content(text)
            
            # 添加文件信息
            parsed_data['file_info'] = {
                'name': os.path.basename(file_path),
                'size': os.path.getsize(file_path),
                'type': Path(file_path).suffix
            }
            parsed_data['raw_text'] = text[:1000]  # 只保留前1000字符
            
            return parsed_data
            
        except Exception as e:
            # 抛出异常而不是返回错误字典，让上层处理
            raise Exception(f"简历解析失败: {str(e)}")
    
    def _validate_file(self, file_path: str) -> bool:
        """验证文件"""
        print(f"验证文件: {file_path}")
        
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            return False
        
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        print(f"文件大小: {file_size} bytes, 限制: {self.max_file_size} bytes")
        if file_size > self.max_file_size:
            print(f"文件大小超限: {file_size} > {self.max_file_size}")
            return False
        
        # 检查文件格式
        file_ext = Path(file_path).suffix.lower()
        print(f"文件扩展名: {file_ext}, 支持的格式: {self.supported_formats}")
        is_supported = file_ext in self.supported_formats
        print(f"格式支持: {is_supported}")
        
        return is_supported
    
    def _extract_text(self, file_path: str) -> str:
        """提取文件文本"""
        file_ext = Path(file_path).suffix.lower()
        
        try:
            if file_ext == '.pdf':
                return self._extract_pdf_text(file_path)
            elif file_ext == '.docx':
                return self._extract_docx_text(file_path)
            elif file_ext == '.txt':
                return self._extract_txt_text(file_path)
            else:
                raise ValueError(f"不支持的文件格式: {file_ext}")
        except Exception as e:
            raise ValueError(f"文本提取失败: {str(e)}")
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """提取PDF文本"""
        if PyPDF2 is None:
            raise ImportError("PyPDF2 未安装，无法处理PDF文件")
        
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            raise ValueError(f"PDF解析错误: {str(e)}")
        
        return text.strip()
    
    def _extract_docx_text(self, file_path: str) -> str:
        """提取DOCX文本"""
        if Document is None:
            raise ImportError("python-docx 未安装，无法处理DOCX文件")
        
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise ValueError(f"DOCX解析错误: {str(e)}")
    
    def _extract_txt_text(self, file_path: str) -> str:
        """提取TXT文本"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='gbk') as file:
                    return file.read().strip()
            except Exception as e:
                raise ValueError(f"TXT解析错误: {str(e)}")
    
    def _parse_content(self, text: str) -> Dict[str, Any]:
        """解析简历内容"""
        # 清理文本
        cleaned_text = self._clean_text(text)
        
        # 提取各部分信息
        personal_info = self._extract_personal_info(cleaned_text)
        skills = self._extract_skills(cleaned_text)
        education = self._extract_education(cleaned_text)
        experience = self._extract_experience(cleaned_text)
        
        return {
            'personal_info': personal_info,
            'skills': skills,
            'education': education,
            'experience': experience,
            'text_length': len(cleaned_text),
            'sections': self._identify_sections(cleaned_text)
        }
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)
        # 移除特殊字符
        text = re.sub(r'[^\w\s\u4e00-\u9fff.,;:()\-+@]', '', text)
        return text.strip()
    
    def _extract_personal_info(self, text: str) -> Dict[str, Optional[str]]:
        """提取个人信息"""
        info = {
            'name': None,
            'email': None,
            'phone': None,
            'location': None
        }
        
        # 提取邮箱
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            info['email'] = email_match.group()
        
        # 提取电话
        phone_patterns = [
            r'1[3-9]\d{9}',  # 中国手机号
            r'\d{3}-\d{4}-\d{4}',  # 美国格式
            r'\(\d{3}\)\s*\d{3}-\d{4}'  # 美国格式带括号
        ]
        for pattern in phone_patterns:
            phone_match = re.search(pattern, text)
            if phone_match:
                info['phone'] = phone_match.group()
                break
        
        # 改进的姓名提取逻辑
        # 1. 首先尝试从文档开头提取（排除包含数字、邮箱、电话的行）
        lines = text.split('\n')[:10]  # 扩展到前10行
        for line in lines:
            line = line.strip()
            # 过滤掉包含数字、邮箱、电话、特殊符号的行
            if (len(line) >= 2 and len(line) <= 10 and 
                not any(char.isdigit() for char in line) and
                '@' not in line and 
                '电话' not in line and 'phone' not in line.lower() and
                '|' not in line and '：' not in line and ':' not in line and
                '优势' not in line and '经历' not in line and '技能' not in line and
                '证书' not in line and '开发' not in line):
                # 检查是否为中文姓名（2-4个中文字符）
                if re.match(r'^[\u4e00-\u9fff]{2,4}$', line):
                    info['name'] = line
                    break
                # 检查是否为英文姓名
                elif re.match(r'^[A-Za-z\s]{2,20}$', line) and ' ' in line:
                    info['name'] = line
                    break
        
        # 2. 如果上述方法没找到，尝试从整个文本中查找姓名模式
        if not info['name']:
            # 查找"姓名"、"Name"等关键词后的内容
            name_patterns = [
                r'姓名[：:]?\s*([\u4e00-\u9fff]{2,4})',
                r'Name[：:]?\s*([A-Za-z\s]{2,20})',
                r'申请人[：:]?\s*([\u4e00-\u9fff]{2,4})'
            ]
            for pattern in name_patterns:
                match = re.search(pattern, text)
                if match:
                    info['name'] = match.group(1).strip()
                    break
        
        # 3. 最后尝试：在文档最开始查找独立的中文姓名
        if not info['name']:
            # 移除所有数字、符号，只保留中文和空格
            clean_start = re.sub(r'[^\u4e00-\u9fff\s]', ' ', text[:200])
            words = clean_start.split()
            for word in words:
                if len(word) >= 2 and len(word) <= 4 and re.match(r'^[\u4e00-\u9fff]+$', word):
                    # 排除常见的非姓名词汇
                    if word not in ['个人', '优势', '经历', '教育', '工作', '项目', '技能', '证书', '后端', '开发', '期望', '城市', '上海', '专业', '课程', '成绩', '基础', '团队', '合作', '能力', '发展', '活动', '领域', '技术', '经验', '语言', '大学', '本科', '计算机', '科学', '社团', '社长', '资格', '英语', '六级', '竞赛', '相关', '项目']:
                        info['name'] = word
                        break
        
        return info
    
    def _extract_skills(self, text: str) -> Dict[str, List[str]]:
        """提取技能"""
        text_lower = text.lower()
        found_skills = {
            'programming': [],
            'frameworks': [],
            'databases': [],
            'tools': [],
            'soft_skills': []
        }
        
        for category, keywords in self.skill_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    found_skills[category].append(keyword)
        
        # 去重并排序
        for category in found_skills:
            found_skills[category] = sorted(list(set(found_skills[category])))
        
        return found_skills
    
    def _extract_education(self, text: str) -> List[Dict[str, str]]:
        """提取教育背景"""
        education = []
        
        # 查找教育相关段落
        lines = text.split('\n')
        education_section = False
        current_edu = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检查是否是教育部分开始
            if any(keyword in line for keyword in ['教育背景', '教育经历', 'education', 'Education']):
                education_section = True
                continue
            
            # 如果在教育部分
            if education_section:
                # 检查是否是新的部分开始
                if any(keyword in line for keyword in ['工作经验', '项目经验', 'experience', 'Experience']):
                    break
                
                # 查找学位和学校信息
                if any(keyword in line for keyword in self.education_keywords):
                    if current_edu:
                        education.append(current_edu)
                    current_edu = {'description': line}
        
        if current_edu:
            education.append(current_edu)
        
        return education
    
    def _extract_experience(self, text: str) -> List[Dict[str, str]]:
        """提取工作经验"""
        experience = []
        
        # 查找经验相关段落
        lines = text.split('\n')
        experience_section = False
        current_exp = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检查是否是经验部分开始
            if any(keyword in line for keyword in self.experience_keywords):
                experience_section = True
                continue
            
            # 如果在经验部分
            if experience_section:
                # 检查是否是新的部分开始
                if any(keyword in line for keyword in ['教育背景', '技能', 'education', 'skills']):
                    break
                
                # 查找公司和职位信息
                if len(line) > 10:  # 假设有意义的经验描述至少10个字符
                    if current_exp:
                        experience.append(current_exp)
                    current_exp = {'description': line}
        
        if current_exp:
            experience.append(current_exp)
        
        return experience
    
    def _identify_sections(self, text: str) -> List[str]:
        """识别简历章节"""
        sections = []
        
        section_keywords = {
            '个人信息': ['个人信息', '基本信息', 'personal', 'contact'],
            '教育背景': ['教育背景', '教育经历', 'education'],
            '工作经验': ['工作经验', '工作经历', 'experience', 'employment'],
            '项目经验': ['项目经验', '项目经历', 'project'],
            '技能': ['技能', '专业技能', 'skills', 'technical'],
            '证书': ['证书', '资格证书', 'certificate', 'certification']
        }
        
        text_lower = text.lower()
        for section_name, keywords in section_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                sections.append(section_name)
        
        return sections
    
    def get_resume_summary(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成简历摘要"""
        if not parsed_data or not parsed_data.get('success'):
            return {'error': '无法生成摘要'}
        
        data = parsed_data['data']
        
        # 统计技能数量
        total_skills = sum(len(skills) for skills in data['skills'].values())
        
        # 统计经验数量
        experience_count = len(data['experience'])
        
        # 统计教育数量
        education_count = len(data['education'])
        
        return {
            'total_skills': total_skills,
            'experience_count': experience_count,
            'education_count': education_count,
            'sections_found': len(data['sections']),
            'text_length': data['text_length'],
            'has_contact_info': bool(data['personal_info']['email'] or data['personal_info']['phone']),
            'completeness_score': self._calculate_completeness_score(data)
        }
    
    def _calculate_completeness_score(self, data: Dict[str, Any]) -> int:
        """计算简历完整度分数"""
        score = 0
        
        # 个人信息 (30分)
        personal = data['personal_info']
        if personal['name']: score += 10
        if personal['email']: score += 10
        if personal['phone']: score += 10
        
        # 技能 (25分)
        total_skills = sum(len(skills) for skills in data['skills'].values())
        if total_skills > 0: score += min(25, total_skills * 2)
        
        # 经验 (25分)
        if data['experience']: score += min(25, len(data['experience']) * 8)
        
        # 教育 (20分)
        if data['education']: score += min(20, len(data['education']) * 10)
        
        return min(100, score)