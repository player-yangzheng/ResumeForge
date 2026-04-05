import re
from typing import Dict, List, Optional, Any

class JDParser:
    """简化版职位描述解析器"""
    
    def __init__(self):
        # 技能关键词库（与简历解析器保持一致）
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
                '学习能力', '适应能力', '责任心', '执行力', '抗压能力', '时间管理'
            ]
        }
        
        # 经验要求关键词
        self.experience_patterns = [
            r'(\d+)年以上.*?经验',
            r'(\d+)\+年.*?经验',
            r'(\d+)-?(\d+)?年.*?经验',
            r'(\d+)年.*?工作经验',
            r'经验.*?(\d+)年',
            r'(\d+)\s*years?.*?experience',
            r'experience.*?(\d+)\s*years?'
        ]
        
        # 学历要求关键词
        self.education_keywords = {
            '本科': ['本科', '学士', 'bachelor', '大学本科'],
            '硕士': ['硕士', 'master', '研究生'],
            '博士': ['博士', 'phd', 'doctor'],
            '专科': ['专科', '大专', 'college', 'associate']
        }
        
        # 职位级别关键词
        self.level_keywords = {
            '初级': ['初级', '入门', '新手', 'junior', 'entry', 'trainee'],
            '中级': ['中级', '有经验', 'mid', 'intermediate', 'experienced'],
            '高级': ['高级', '资深', 'senior', 'lead', 'principal'],
            '专家': ['专家', '架构师', 'expert', 'architect', 'specialist'],
            '管理': ['经理', '主管', '总监', 'manager', 'director', 'supervisor']
        }
        
        # 工作类型关键词
        self.work_type_keywords = {
            '全职': ['全职', 'full-time', '正式'],
            '兼职': ['兼职', 'part-time'],
            '实习': ['实习', 'intern', 'internship'],
            '合同': ['合同', 'contract', '外包'],
            '远程': ['远程', 'remote', '在家办公']
        }
    
    def parse_jd(self, jd_text: str) -> Dict[str, Any]:
        """解析职位描述"""
        try:
            if not jd_text or len(jd_text.strip()) < 50:
                raise ValueError("职位描述内容过短，至少需要50个字符")
            
            # 清理文本
            cleaned_text = self._clean_text(jd_text)
            
            # 解析各部分信息
            parsed_data = {
                'job_info': self._extract_job_info(cleaned_text),
                'requirements': self._extract_requirements(cleaned_text),
                'skills': self._extract_skills(cleaned_text),
                'experience': self._extract_experience_requirements(cleaned_text),
                'education': self._extract_education_requirements(cleaned_text),
                'benefits': self._extract_benefits(cleaned_text),
                'keywords': self._extract_keywords(cleaned_text),
                'text_length': len(cleaned_text)
            }
            
            return {
                'success': True,
                'data': parsed_data,
                'raw_text': jd_text[:1000]  # 保留前1000字符
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': None
            }
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)
        # 保留中文、英文、数字和常用标点
        text = re.sub(r'[^\w\s\u4e00-\u9fff.,;:()\-+@/]', '', text)
        return text.strip()
    
    def _extract_job_info(self, text: str) -> Dict[str, Optional[str]]:
        """提取职位基本信息"""
        info = {
            'title': None,
            'company': None,
            'location': None,
            'salary': None,
            'work_type': None,
            'level': None
        }
        
        # 提取公司信息（通常包含"公司"、"科技"、"有限"等关键词）
        company_patterns = [
            r'([\u4e00-\u9fff]+(?:公司|科技|集团|企业|有限|股份|责任|网络|信息|软件|技术))',
            r'([A-Za-z]+\s*(?:Company|Corp|Inc|Ltd|LLC|Technology|Tech))',
            r'公司名称.*?([\u4e00-\u9fff]+)',
            r'招聘公司.*?([\u4e00-\u9fff]+)'
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                company_name = match.group(1).strip()
                if len(company_name) > 2 and len(company_name) < 30:
                    info['company'] = company_name
                    break
        
        # 提取职位名称（通常在开头）
        lines = text.split('\n')[:3]
        for line in lines:
            line = line.strip()
            if len(line) > 2 and len(line) < 50:
                if any(keyword in line for keyword in ['工程师', '开发', '经理', '专员', 'engineer', 'developer', 'manager']):
                    info['title'] = line
                    break
        
        # 提取薪资信息
        salary_patterns = [
            r'(\d+)k?-?(\d+)?k?/月',
            r'月薪.*?(\d+)k?-?(\d+)?k?',
            r'薪资.*?(\d+)k?-?(\d+)?k?',
            r'(\d+)k?-(\d+)k?',
            r'\$(\d+)k?-?(\d+)?k?'
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info['salary'] = match.group()
                break
        
        # 提取工作类型
        text_lower = text.lower()
        for work_type, keywords in self.work_type_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                info['work_type'] = work_type
                break
        
        # 提取职位级别
        for level, keywords in self.level_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                info['level'] = level
                break
        
        # 提取地点信息
        location_patterns = [
            r'工作地点.*?([\u4e00-\u9fff]+市?)',
            r'地点.*?([\u4e00-\u9fff]+市?)',
            r'([\u4e00-\u9fff]+市).*?工作'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text)
            if match:
                info['location'] = match.group(1)
                break
        
        return info
    
    def _extract_requirements(self, text: str) -> List[str]:
        """提取职位要求"""
        requirements = []
        
        # 查找要求相关段落
        requirement_keywords = ['任职要求', '职位要求', '岗位要求', 'requirements', '要求']
        lines = text.split('\n')
        
        in_requirements = False
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检查是否进入要求部分
            if any(keyword in line for keyword in requirement_keywords):
                in_requirements = True
                continue
            
            # 如果在要求部分
            if in_requirements:
                # 检查是否离开要求部分
                if any(keyword in line for keyword in ['工作职责', '岗位职责', '福利', 'responsibilities', 'benefits']):
                    break
                
                # 添加要求项
                if len(line) > 5 and ('.' in line or '、' in line or line.startswith(('-', '*', '•'))):
                    requirements.append(line)
        
        return requirements[:10]  # 最多返回10个要求
    
    def _extract_skills(self, text: str) -> Dict[str, List[str]]:
        """提取技能要求"""
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
    
    def _extract_experience_requirements(self, text: str) -> Dict[str, Any]:
        """提取经验要求"""
        experience_info = {
            'min_years': None,
            'max_years': None,
            'description': None
        }
        
        # 查找经验年限
        for pattern in self.experience_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) >= 1 and groups[0]:
                    experience_info['min_years'] = int(groups[0])
                if len(groups) >= 2 and groups[1]:
                    experience_info['max_years'] = int(groups[1])
                experience_info['description'] = match.group()
                break
        
        return experience_info
    
    def _extract_education_requirements(self, text: str) -> Dict[str, Any]:
        """提取学历要求"""
        education_info = {
            'level': None,
            'major': None,
            'description': None
        }
        
        text_lower = text.lower()
        
        # 查找学历要求
        for level, keywords in self.education_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                education_info['level'] = level
                break
        
        # 查找专业要求
        major_patterns = [
            r'计算机.*?专业',
            r'软件.*?专业',
            r'电子.*?专业',
            r'信息.*?专业',
            r'数学.*?专业',
            r'相关专业',
            r'computer.*?science',
            r'software.*?engineering'
        ]
        
        for pattern in major_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                education_info['major'] = match.group()
                break
        
        return education_info
    
    def _extract_benefits(self, text: str) -> List[str]:
        """提取福利待遇"""
        benefits = []
        
        # 福利关键词
        benefit_keywords = [
            '五险一金', '六险一金', '年终奖', '带薪年假', '弹性工作',
            '股票期权', '培训机会', '健身房', '免费午餐', '交通补贴',
            '住房补贴', '通讯补贴', '节日福利', '团建活动'
        ]
        
        text_lower = text.lower()
        for keyword in benefit_keywords:
            if keyword in text:
                benefits.append(keyword)
        
        # 查找福利相关段落
        benefit_section_keywords = ['福利待遇', '公司福利', 'benefits', '福利']
        lines = text.split('\n')
        
        in_benefits = False
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检查是否进入福利部分
            if any(keyword in line for keyword in benefit_section_keywords):
                in_benefits = True
                continue
            
            # 如果在福利部分
            if in_benefits:
                # 检查是否离开福利部分
                if any(keyword in line for keyword in ['联系方式', '应聘方式', 'contact']):
                    break
                
                # 添加福利项
                if len(line) > 3:
                    benefits.append(line)
        
        return list(set(benefits))[:10]  # 去重，最多返回10个福利
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 移除常用停用词
        stop_words = {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个',
            '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好',
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of',
            'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had'
        }
        
        # 分词（简单按空格和标点分割）
        words = re.findall(r'[\w\u4e00-\u9fff]+', text.lower())
        
        # 过滤关键词
        keywords = []
        for word in words:
            if len(word) > 1 and word not in stop_words:
                keywords.append(word)
        
        # 统计词频并返回前20个
        from collections import Counter
        word_counts = Counter(keywords)
        return [word for word, count in word_counts.most_common(20)]
    
    def get_jd_summary(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成JD摘要"""
        if not parsed_data or not parsed_data.get('success'):
            return {'error': '无法生成摘要'}
        
        data = parsed_data['data']
        
        # 统计技能数量
        total_skills = sum(len(skills) for skills in data['skills'].values())
        
        # 统计要求数量
        requirements_count = len(data['requirements'])
        
        # 统计福利数量
        benefits_count = len(data['benefits'])
        
        return {
            'total_skills': total_skills,
            'requirements_count': requirements_count,
            'benefits_count': benefits_count,
            'has_experience_req': bool(data['experience']['min_years']),
            'has_education_req': bool(data['education']['level']),
            'text_length': data['text_length'],
            'job_level': data['job_info']['level'],
            'work_type': data['job_info']['work_type'],
            'completeness_score': self._calculate_jd_completeness_score(data)
        }
    
    def _calculate_jd_completeness_score(self, data: Dict[str, Any]) -> int:
        """计算JD完整度分数"""
        score = 0
        
        # 基本信息 (30分)
        job_info = data['job_info']
        if job_info['title']: score += 10
        if job_info['salary']: score += 10
        if job_info['location']: score += 10
        
        # 技能要求 (25分)
        total_skills = sum(len(skills) for skills in data['skills'].values())
        if total_skills > 0: score += min(25, total_skills * 2)
        
        # 职位要求 (20分)
        if data['requirements']: score += min(20, len(data['requirements']) * 3)
        
        # 经验和学历要求 (15分)
        if data['experience']['min_years']: score += 8
        if data['education']['level']: score += 7
        
        # 福利待遇 (10分)
        if data['benefits']: score += min(10, len(data['benefits']) * 2)
        
        return min(100, score)
    
    def extract_job_categories(self, text: str) -> List[str]:
        """提取职位类别"""
        categories = []
        
        category_keywords = {
            '软件开发': ['开发', '工程师', 'developer', 'engineer', '程序员'],
            '产品管理': ['产品经理', 'product', '产品', 'pm'],
            '数据分析': ['数据分析', '数据科学', 'data', 'analyst', '分析师'],
            '测试': ['测试', 'test', 'qa', '质量'],
            '运维': ['运维', 'devops', '系统管理', 'sre'],
            '设计': ['设计师', 'designer', 'ui', 'ux', '设计'],
            '市场营销': ['市场', '营销', 'marketing', '推广'],
            '销售': ['销售', 'sales', '商务'],
            '人力资源': ['人力资源', 'hr', '招聘'],
            '财务': ['财务', 'finance', '会计']
        }
        
        text_lower = text.lower()
        for category, keywords in category_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                categories.append(category)
        
        return categories