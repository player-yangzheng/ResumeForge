from typing import Dict, List, Any, Optional
import random

class ResumeOptimizer:
    """简化版简历优化器"""
    
    def __init__(self):
        # 优化建议模板
        self.suggestion_templates = {
            'skills': {
                'add_missing': "建议在简历中添加以下技能：{skills}",
                'highlight_existing': "突出展示已有技能：{skills}",
                'skill_section': "建议增加专门的技能部分，详细列出技术栈",
                'certifications': "考虑获得相关技术认证来证明技能水平"
            },
            'experience': {
                'quantify': "用具体数字量化工作成果，如'提升效率30%'、'管理团队10人'",
                'keywords': "在工作经历中融入更多职位相关关键词",
                'projects': "详细描述重要项目的技术栈、规模和个人贡献",
                'achievements': "突出工作中的具体成就和解决的问题",
                'timeline': "确保工作经历时间线清晰，避免空白期"
            },
            'format': {
                'structure': "优化简历结构，确保信息层次清晰",
                'length': "控制简历长度在1-2页，突出重点信息",
                'keywords': "在简历中自然融入职位描述中的关键词",
                'action_verbs': "使用强有力的动作词汇，如'开发'、'优化'、'领导'",
                'consistency': "保持格式一致性，包括字体、间距、标点等"
            },
            'content': {
                'summary': "添加专业摘要部分，简洁概括核心优势",
                'education': "根据职位要求调整教育背景的展示重点",
                'contact': "确保联系方式准确完整，包括邮箱和电话",
                'customization': "针对具体职位定制简历内容",
                'proofreading': "仔细校对，确保没有拼写和语法错误"
            }
        }
        
        # 技能提升建议
        self.skill_learning_resources = {
            'programming': {
                'python': ['Python官方文档', 'LeetCode练习', 'Django/Flask框架学习'],
                'java': ['Oracle Java教程', 'Spring框架学习', 'Java设计模式'],
                'javascript': ['MDN Web文档', 'React/Vue框架', 'Node.js后端开发']
            },
            'frameworks': {
                'react': ['React官方教程', '实战项目开发', 'Redux状态管理'],
                'django': ['Django官方文档', 'REST API开发', '数据库集成'],
                'spring': ['Spring Boot快速入门', '微服务架构', 'Spring Security']
            },
            'databases': {
                'mysql': ['MySQL官方文档', 'SQL查询优化', '数据库设计原理'],
                'mongodb': ['MongoDB大学课程', 'NoSQL设计模式', '聚合管道操作']
            }
        }
    
    def generate_optimization_suggestions(self, match_analysis: Dict[str, Any], 
                                        resume_data: Dict[str, Any], 
                                        jd_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成优化建议"""
        try:
            if not match_analysis.get('success'):
                raise ValueError("匹配分析数据无效")
            
            match_data = match_analysis['data']
            suggestions = []
            
            # 基于匹配分析生成建议
            skill_suggestions = self._generate_skill_suggestions(match_data, jd_data)
            experience_suggestions = self._generate_experience_suggestions(match_data, resume_data)
            format_suggestions = self._generate_format_suggestions(match_data)
            content_suggestions = self._generate_content_suggestions(match_data, resume_data, jd_data)
            
            # 合并所有建议
            all_suggestions = {
                'skills': skill_suggestions,
                'experience': experience_suggestions,
                'format': format_suggestions,
                'content': content_suggestions
            }
            
            # 生成优先级排序的建议列表
            prioritized_suggestions = self._prioritize_suggestions(all_suggestions, match_data)
            
            # 生成学习计划
            learning_plan = self._generate_learning_plan(match_data.get('missing_skills', []))
            
            return {
                'success': True,
                'data': {
                    'suggestions': prioritized_suggestions,
                    'categorized_suggestions': all_suggestions,
                    'learning_plan': learning_plan,
                    'priority_areas': self._identify_priority_areas(match_data),
                    'quick_wins': self._identify_quick_wins(match_data),
                    'long_term_goals': self._identify_long_term_goals(match_data)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': None
            }
    
    def _generate_skill_suggestions(self, match_data: Dict[str, Any], jd_data: Dict[str, Any]) -> List[str]:
        """生成技能相关建议"""
        suggestions = []
        
        missing_skills = match_data.get('missing_skills', [])
        matched_skills = match_data.get('matched_skills', [])
        
        # 添加缺失技能的建议
        if missing_skills:
            top_missing = missing_skills[:3]  # 取前3个最重要的
            suggestions.append(f"学习并在简历中添加以下关键技能：{', '.join(top_missing)}")
        
        # 突出已有技能的建议
        if matched_skills:
            suggestions.append(f"在简历中更突出地展示匹配技能：{', '.join(matched_skills[:3])}")
        
        # 技能部分优化建议
        if match_data.get('skill_score', 0) < 70:
            suggestions.append("创建专门的技能部分，按技术栈分类组织")
        
        return suggestions
    
    def _generate_experience_suggestions(self, match_data: Dict[str, Any], resume_data: Dict[str, Any]) -> List[str]:
        """生成经验相关建议"""
        suggestions = []
        
        experience_score = match_data.get('experience_score', 0)
        
        if experience_score < 70:
            suggestions.append("用具体数据量化工作成果，如'提升效率30%'、'管理团队10人'")
            suggestions.append("在工作描述中自然融入职位相关关键词")
        
        # 项目经验建议
        if resume_data.get('success'):
            work_exp = resume_data['data'].get('work_experience', [])
            projects = resume_data['data'].get('projects', [])
            if len(work_exp) + len(projects) < 3:
                suggestions.append("增加项目经验描述，包括技术选型和个人贡献")
        
        return suggestions
    
    def _generate_format_suggestions(self, match_data: Dict[str, Any]) -> List[str]:
        """生成格式相关建议"""
        suggestions = []
        
        # 基础格式建议
        suggestions.append("确保简历结构清晰：个人信息-专业摘要-工作经验-技能-教育背景")
        suggestions.append("在简历各部分自然融入职位描述中的关键词")
        suggestions.append("保持简历格式一致，使用统一的字体和排版")
        
        suggestions.append("使用有力的动作词汇开始每个工作描述，如'开发'、'优化'、'领导'")
        
        return suggestions
    
    def _generate_content_suggestions(self, match_data: Dict[str, Any], 
                                    resume_data: Dict[str, Any], 
                                    jd_data: Dict[str, Any]) -> List[str]:
        """生成内容相关建议"""
        suggestions = []
        
        # 基于具体简历内容生成个性化建议
        if resume_data.get('success') and jd_data.get('success'):
            resume_content = resume_data['data']
            jd_content = jd_data['data']
            
            # 检查专业摘要
            if not resume_content.get('summary'):
                suggestions.append("添加专业摘要部分，简洁概括核心优势")
            
            # 检查联系方式
            personal_info = resume_content.get('personal_info', {})
            if not personal_info.get('email') or not personal_info.get('phone'):
                suggestions.append("完善联系方式，确保邮箱和电话信息准确")
            
            # 检查工作经历描述
            work_exp = resume_content.get('work_experience', [])
            if work_exp:
                for exp in work_exp:
                    if not exp.get('achievements') or len(exp.get('achievements', [])) == 0:
                        suggestions.append("在工作经历中添加具体成就和量化数据")
                        break
            
            # 检查技能部分
            skills = resume_content.get('skills', {})
            if not any(skills.values()):
                suggestions.append("建议增加专门的技能部分，详细列出技术栈")
            
            # 根据JD要求提供定制化建议
            jd_keywords = jd_content.get('keywords', [])
            if jd_keywords:
                suggestions.append("在简历中自然融入职位描述中的关键词")
                
        # 通用建议
        suggestions.extend([
            "用具体数字量化工作成果，如'提升效率30%'、'管理团队10人'",
            "针对具体职位定制简历内容",
            "优化简历结构，确保信息层次清晰",
            "使用强有力的动作词汇，如'开发'、'优化'、'领导'"
        ])
        
        return suggestions
    
    def _prioritize_suggestions(self, all_suggestions: Dict[str, List], match_data: Dict[str, Any]) -> List[str]:
        """对建议进行优先级排序"""
        prioritized = []
        
        # 收集所有建议
        for category, suggestions in all_suggestions.items():
            prioritized.extend(suggestions)
        
        # 去重并限制数量
        unique_suggestions = list(dict.fromkeys(prioritized))  # 保持顺序的去重
        
        return unique_suggestions[:8]  # 返回前8个建议
    
    def _generate_learning_plan(self, missing_skills: List[str]) -> Dict[str, Any]:
        """生成学习计划"""
        if not missing_skills:
            return {
                'immediate': [],
                'short_term': [],
                'long_term': [],
                'resources': {}
            }
        
        # 按技能类型分类
        skill_categories = {
            'programming': [],
            'frameworks': [],
            'databases': [],
            'tools': [],
            'other': []
        }
        
        for skill in missing_skills:
            categorized = False
            for category, keywords in {
                'programming': ['python', 'java', 'javascript', 'c++', 'c#'],
                'frameworks': ['react', 'vue', 'django', 'spring', 'flask'],
                'databases': ['mysql', 'postgresql', 'mongodb', 'redis'],
                'tools': ['git', 'docker', 'kubernetes', 'aws']
            }.items():
                if any(keyword in skill.lower() for keyword in keywords):
                    skill_categories[category].append(skill)
                    categorized = True
                    break
            if not categorized:
                skill_categories['other'].append(skill)
        
        # 生成学习计划
        plan = {
            'immediate': [],  # 1-2周
            'short_term': [],  # 1-3个月
            'long_term': [],   # 3-6个月
            'resources': {}
        }
        
        # 编程语言优先级最高
        if skill_categories['programming']:
            plan['immediate'].extend(skill_categories['programming'][:2])
            plan['short_term'].extend(skill_categories['programming'][2:])
        
        # 框架次之
        if skill_categories['frameworks']:
            plan['short_term'].extend(skill_categories['frameworks'][:2])
            plan['long_term'].extend(skill_categories['frameworks'][2:])
        
        # 其他技能
        remaining_skills = (skill_categories['databases'] + 
                          skill_categories['tools'] + 
                          skill_categories['other'])
        plan['long_term'].extend(remaining_skills)
        
        # 添加学习资源
        for skill in missing_skills[:5]:  # 只为前5个技能提供资源
            resources = self._get_learning_resources(skill)
            if resources:
                plan['resources'][skill] = resources
        
        return plan
    
    def _get_learning_resources(self, skill: str) -> List[str]:
        """获取技能学习资源"""
        skill_lower = skill.lower()
        
        # 查找具体技能的资源
        for category, skills in self.skill_learning_resources.items():
            for skill_name, resources in skills.items():
                if skill_name in skill_lower or skill_lower in skill_name:
                    return resources
        
        # 通用资源
        generic_resources = {
            'programming': ['在线编程平台练习', '官方文档学习', '开源项目贡献'],
            'framework': ['官方教程', '实战项目', '社区文档'],
            'database': ['官方文档', 'SQL练习平台', '数据库设计课程'],
            'tool': ['官方文档', '实践操作', '认证考试']
        }
        
        # 根据技能类型返回通用资源
        if any(keyword in skill_lower for keyword in ['python', 'java', 'javascript']):
            return generic_resources['programming']
        elif any(keyword in skill_lower for keyword in ['react', 'vue', 'django', 'spring']):
            return generic_resources['framework']
        elif any(keyword in skill_lower for keyword in ['mysql', 'mongodb', 'redis']):
            return generic_resources['database']
        else:
            return generic_resources['tool']
    
    def _identify_priority_areas(self, match_data: Dict[str, Any]) -> List[str]:
        """识别优先改进领域"""
        areas = []
        
        scores = {
            '技能匹配': match_data.get('skill_score', 0),
            '经验匹配': match_data.get('experience_score', 0),
            '学历匹配': match_data.get('education_score', 0),
            '关键词匹配': match_data.get('keyword_score', 0)
        }
        
        # 按分数排序，分数低的优先
        sorted_areas = sorted(scores.items(), key=lambda x: x[1])
        
        for area, score in sorted_areas:
            if score < 70:
                areas.append(f"{area}({score}%)")
        
        return areas[:3]
    
    def _identify_quick_wins(self, match_data: Dict[str, Any]) -> List[str]:
        """识别快速改进点"""
        quick_wins = []
        
        # 关键词优化（最容易实现）
        if match_data.get('keyword_score', 0) < 80:
            quick_wins.append("在简历中添加职位描述中的关键词")
        
        # 格式优化
        quick_wins.append("优化简历格式和结构")
        
        # 已有技能突出
        if match_data.get('matched_skills'):
            quick_wins.append("突出展示已掌握的相关技能")
        
        # 工作描述量化
        quick_wins.append("用数字量化工作成果")
        
        return quick_wins[:4]
    
    def _identify_long_term_goals(self, match_data: Dict[str, Any]) -> List[str]:
        """识别长期目标"""
        long_term = []
        
        missing_skills = match_data.get('missing_skills', [])
        
        if missing_skills:
            # 按技能重要性分类
            critical_skills = [skill for skill in missing_skills 
                             if any(keyword in skill.lower() 
                                   for keyword in ['python', 'java', 'react', 'mysql'])]
            
            if critical_skills:
                long_term.append(f"学习核心技能：{', '.join(critical_skills[:3])}")
        
        # 经验积累
        if match_data.get('experience_score', 0) < 70:
            long_term.append("积累更多相关项目经验")
        
        # 认证获取
        long_term.append("获得相关技术认证")
        
        # 持续学习
        long_term.append("建立持续学习计划，跟上技术发展")
        
        return long_term[:4]
    
    def generate_rewrite_suggestions(self, resume_data: Dict[str, Any], 
                                   jd_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成简历重写建议"""
        try:
            suggestions = {
                'professional_summary': self._generate_summary_rewrite(resume_data, jd_data),
                'experience_descriptions': self._generate_experience_rewrite(resume_data, jd_data),
                'skills_section': self._generate_skills_rewrite(resume_data, jd_data),
                'overall_structure': self._generate_structure_suggestions()
            }
            
            return {
                'success': True,
                'data': suggestions
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': None
            }
    
    def _generate_summary_rewrite(self, resume_data: Dict, jd_data: Dict) -> str:
        """生成专业摘要重写建议"""
        if not jd_data.get('success'):
            return "添加2-3句专业摘要，突出核心技能和经验优势"
        
        jd_skills = jd_data['data'].get('skills', {})
        top_skills = []
        
        for category, skills in jd_skills.items():
            top_skills.extend(skills[:2])  # 每类取前2个
        
        if top_skills:
            return f"建议专业摘要突出以下技能：{', '.join(top_skills[:5])}，并量化工作年限和主要成就"
        else:
            return "添加专业摘要，简洁描述核心技能、经验年限和主要成就"
    
    def _generate_experience_rewrite(self, resume_data: Dict, jd_data: Dict) -> List[str]:
        """生成工作经验重写建议"""
        suggestions = [
            "使用STAR法则（情况-任务-行动-结果）描述工作经历",
            "每个职位用3-5个要点描述主要职责和成就",
            "用具体数字量化工作成果（如：提升效率30%、管理团队10人）",
            "突出与目标职位相关的项目经验和技术栈",
            "使用强有力的动作词汇开始每个描述点"
        ]
        
        return suggestions
    
    def _generate_skills_rewrite(self, resume_data: Dict, jd_data: Dict) -> str:
        """生成技能部分重写建议"""
        return "按类别组织技能：编程语言、框架/库、数据库、工具/平台、软技能，优先展示与职位最相关的技能"
    
    def _generate_structure_suggestions(self) -> List[str]:
        """生成结构建议"""
        return [
            "建议结构：联系方式 → 专业摘要 → 核心技能 → 工作经验 → 项目经验 → 教育背景",
            "确保每个部分标题清晰，内容层次分明",
            "控制简历长度在1-2页，突出最相关的信息",
            "使用一致的格式和字体，保持专业外观"
        ]