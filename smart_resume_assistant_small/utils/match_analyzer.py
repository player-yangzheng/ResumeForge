from typing import Dict, List, Any, Tuple
import re
from collections import Counter

class MatchAnalyzer:
    """简化版匹配分析器"""
    
    def __init__(self):
        # 分析权重配置
        self.weights = {
            'skills': 0.4,      # 技能匹配权重40%
            'experience': 0.3,  # 经验匹配权重30%
            'education': 0.2,   # 学历匹配权重20%
            'keywords': 0.1     # 关键词匹配权重10%
        }
        
        # 技能重要性权重
        self.skill_importance = {
            'programming': 1.0,    # 编程语言最重要
            'frameworks': 0.8,     # 框架次重要
            'databases': 0.7,      # 数据库
            'tools': 0.6,          # 工具
            'soft_skills': 0.5     # 软技能
        }
    
    def analyze_match(self, resume_data: Dict[str, Any], jd_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析简历与职位的匹配度"""
        try:
            print(f"Match analyzer input - resume_data type: {type(resume_data)}, jd_data type: {type(jd_data)}")
            print(f"Resume data keys: {list(resume_data.keys()) if isinstance(resume_data, dict) else 'Not a dict'}")
            print(f"JD data keys: {list(jd_data.keys()) if isinstance(jd_data, dict) else 'Not a dict'}")
            
            # 处理不同的数据结构
            if resume_data.get('success') is not None:
                # LLM解析器返回的格式
                if not resume_data.get('success') or not jd_data.get('success'):
                    raise ValueError("简历或职位描述解析失败")
                resume = resume_data['data']
                jd = jd_data['data']
            else:
                # 传统解析器返回的格式
                resume = resume_data
                jd = jd_data
            
            # 处理数据结构差异 - 统一数据格式
            print(f"Resume data keys: {list(resume.keys())}")
            print(f"JD data keys: {list(jd.keys())}")
            
            # 处理简历技能数据
            resume_skills = resume.get('skills', {})
            if not isinstance(resume_skills, dict):
                resume_skills = {'general': resume_skills if isinstance(resume_skills, list) else []}
            
            # 处理JD技能数据
            jd_skills = {}
            if jd.get('requirements'):
                if isinstance(jd['requirements'], dict):
                    jd_skills = jd['requirements'].get('skills', {})
                elif isinstance(jd['requirements'], list):
                    jd_skills = {'general': jd['requirements']}
            elif jd.get('skills'):
                jd_skills = jd['skills']
            
            # 如果JD技能仍为空，尝试从其他字段提取
            if not jd_skills:
                tech_skills = []
                for key in ['technical_skills', 'required_skills', 'keywords']:
                    if jd.get(key):
                        if isinstance(jd[key], list):
                            tech_skills.extend(jd[key])
                        elif isinstance(jd[key], str):
                            tech_skills.append(jd[key])
                if tech_skills:
                    jd_skills = {'general': tech_skills}
            
            print(f"Processed resume skills: {resume_skills}")
            print(f"Processed JD skills: {jd_skills}")
            
            resume_experience = resume.get('work_experience', [])
            jd_experience = jd.get('job_info', {}) if jd.get('job_info') else jd.get('experience', {})
            
            resume_education = resume.get('education', [])
            jd_education = jd_experience.get('education_required', '') if isinstance(jd_experience, dict) else ''
            
            jd_keywords = jd.get('keywords', [])
            
            # 各维度匹配分析
            skill_analysis = self._analyze_skills_match(resume_skills, jd_skills)
            experience_analysis = self._analyze_experience_match(resume_experience, {'min_years': jd_experience.get('experience_required', 0)})
            education_analysis = self._analyze_education_match(resume_education, {'required': jd_education})
            # 获取简历原文用于关键词匹配
            resume_text = ''
            if resume_data.get('raw_text'):
                resume_text = resume_data['raw_text']
            elif resume_data.get('success') and resume_data.get('raw_text'):
                resume_text = resume_data['raw_text']
            else:
                # 从解析后的数据重构文本
                text_parts = []
                if resume.get('personal_info', {}).get('name'):
                    text_parts.append(resume['personal_info']['name'])
                if resume.get('summary'):
                    text_parts.append(resume['summary'])
                for exp in resume.get('work_experience', []):
                    if exp.get('description'):
                        text_parts.append(exp['description'])
                for skill_list in resume.get('skills', {}).values():
                    if isinstance(skill_list, list):
                        text_parts.extend(skill_list)
                resume_text = ' '.join(text_parts)
            
            keyword_analysis = self._analyze_keyword_match(resume_text, jd_keywords)
            
            # 计算总体匹配度
            overall_score = self._calculate_overall_score(
                skill_analysis['score'],
                experience_analysis['score'],
                education_analysis['score'],
                keyword_analysis['score']
            )
            
            # 生成匹配报告
            match_report = {
                'overall_score': overall_score,
                'skill_score': skill_analysis['score'],
                'experience_score': experience_analysis['score'],
                'education_score': education_analysis['score'],
                'keyword_score': keyword_analysis['score'],
                'matched_skills': skill_analysis['matched'],
                'missing_skills': skill_analysis['missing'],
                'skill_gaps': skill_analysis['gaps'],
                'strengths': self._identify_strengths(skill_analysis, experience_analysis, education_analysis),
                'weaknesses': self._identify_weaknesses(skill_analysis, experience_analysis, education_analysis),
                'recommendations': self._generate_recommendations(skill_analysis, experience_analysis, education_analysis),
                'match_level': self._get_match_level(overall_score)
            }
            
            return {
                'success': True,
                'data': match_report
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': None
            }
    
    def _analyze_skills_match(self, resume_skills: Dict[str, List[str]], jd_skills: Dict[str, List[str]]) -> Dict[str, Any]:
        """分析技能匹配度"""
        matched_skills = []
        missing_skills = []
        skill_gaps = []
        
        total_jd_skills = 0
        total_matched = 0
        weighted_score = 0
        total_weight = 0
        
        for category, jd_skill_list in jd_skills.items():
            if not jd_skill_list:
                continue
                
            resume_skill_list = resume_skills.get(category, [])
            category_weight = self.skill_importance.get(category, 0.5)
            
            # 计算该类别的匹配情况
            category_matched = []
            category_missing = []
            
            for skill in jd_skill_list:
                if any(skill.lower() in resume_skill.lower() or resume_skill.lower() in skill.lower() 
                      for resume_skill in resume_skill_list):
                    category_matched.append(skill)
                    matched_skills.append(skill)
                else:
                    category_missing.append(skill)
                    missing_skills.append(skill)
            
            # 计算该类别得分
            if jd_skill_list:
                category_score = len(category_matched) / len(jd_skill_list) * 100
                weighted_score += category_score * category_weight
                total_weight += category_weight
                
                if len(category_missing) > 0:
                    skill_gaps.append({
                        'category': category,
                        'missing_count': len(category_missing),
                        'missing_skills': category_missing
                    })
            
            total_jd_skills += len(jd_skill_list)
            total_matched += len(category_matched)
        
        # 计算最终得分
        if total_weight > 0:
            final_score = weighted_score / total_weight
        else:
            final_score = 0 if total_jd_skills > 0 else 100
        
        return {
            'score': round(final_score, 1),
            'matched': matched_skills,
            'missing': missing_skills,
            'gaps': skill_gaps,
            'match_rate': round(total_matched / max(total_jd_skills, 1) * 100, 1)
        }
    
    def _analyze_experience_match(self, resume_experience: List[Dict], jd_experience: Dict[str, Any]) -> Dict[str, Any]:
        """分析经验匹配度"""
        score = 0
        analysis = {
            'has_experience': len(resume_experience) > 0,
            'experience_count': len(resume_experience),
            'meets_requirement': False,
            'gap_years': 0
        }
        
        # 如果JD没有明确经验要求，给予基础分数
        if not jd_experience.get('min_years'):
            score = 80 if analysis['has_experience'] else 60
            analysis['meets_requirement'] = True
        else:
            required_years = jd_experience['min_years']
            
            # 简单估算简历经验年限（基于经验条目数量）
            estimated_years = len(resume_experience) * 1.5  # 假设每个经验条目代表1.5年
            
            if estimated_years >= required_years:
                score = 100
                analysis['meets_requirement'] = True
            elif estimated_years >= required_years * 0.8:  # 80%符合
                score = 80
                analysis['gap_years'] = required_years - estimated_years
            elif estimated_years >= required_years * 0.6:  # 60%符合
                score = 60
                analysis['gap_years'] = required_years - estimated_years
            else:
                score = 40
                analysis['gap_years'] = required_years - estimated_years
        
        return {
            'score': round(score, 1),
            'analysis': analysis
        }
    
    def _analyze_education_match(self, resume_education: List[Dict], jd_education: Dict[str, Any]) -> Dict[str, Any]:
        """分析学历匹配度"""
        score = 0
        analysis = {
            'has_education': len(resume_education) > 0,
            'education_count': len(resume_education),
            'meets_requirement': False
        }
        
        # 如果JD没有明确学历要求，给予基础分数
        if not jd_education.get('level'):
            score = 80 if analysis['has_education'] else 60
            analysis['meets_requirement'] = True
        else:
            required_level = jd_education['level']
            
            # 学历等级映射
            education_levels = {
                '博士': 4,
                '硕士': 3,
                '本科': 2,
                '专科': 1
            }
            
            required_level_score = education_levels.get(required_level, 2)
            
            # 检查简历中的学历
            max_education_score = 0
            for edu in resume_education:
                edu_text = edu.get('description', '').lower()
                for level, level_score in education_levels.items():
                    if level in edu_text:
                        max_education_score = max(max_education_score, level_score)
            
            if max_education_score >= required_level_score:
                score = 100
                analysis['meets_requirement'] = True
            elif max_education_score >= required_level_score - 1:  # 差一个等级
                score = 70
            elif max_education_score > 0:
                score = 50
            else:
                score = 30  # 没有明确学历信息
        
        return {
            'score': round(score, 1),
            'analysis': analysis
        }
    
    def _analyze_keyword_match(self, resume_text: str, jd_keywords: List[str]) -> Dict[str, Any]:
        """分析关键词匹配度"""
        if not jd_keywords:
            return {'score': 80, 'matched_keywords': [], 'missing_keywords': []}
        
        resume_text_lower = resume_text.lower()
        matched_keywords = []
        missing_keywords = []
        
        for keyword in jd_keywords:
            if keyword.lower() in resume_text_lower:
                matched_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)
        
        # 计算匹配率
        match_rate = len(matched_keywords) / len(jd_keywords) if jd_keywords else 0
        score = match_rate * 100
        
        return {
            'score': round(score, 1),
            'matched_keywords': matched_keywords,
            'missing_keywords': missing_keywords,
            'match_rate': round(match_rate * 100, 1)
        }
    
    def _calculate_overall_score(self, skill_score: float, experience_score: float, 
                               education_score: float, keyword_score: float) -> int:
        """计算总体匹配度分数"""
        overall = (
            skill_score * self.weights['skills'] +
            experience_score * self.weights['experience'] +
            education_score * self.weights['education'] +
            keyword_score * self.weights['keywords']
        )
        return round(overall)
    
    def _identify_strengths(self, skill_analysis: Dict, experience_analysis: Dict, 
                          education_analysis: Dict) -> List[str]:
        """识别优势"""
        strengths = []
        
        if skill_analysis['score'] >= 80:
            strengths.append(f"技能匹配度高达{skill_analysis['score']}%，专业技能符合要求")
        
        if experience_analysis['score'] >= 80:
            strengths.append("工作经验丰富，满足岗位要求")
        
        if education_analysis['score'] >= 80:
            strengths.append("教育背景符合岗位要求")
        
        if len(skill_analysis['matched']) > 5:
            strengths.append(f"掌握{len(skill_analysis['matched'])}项相关技能，技术栈较为全面")
        
        if not strengths:
            strengths.append("具备基础的岗位相关能力")
        
        return strengths
    
    def _identify_weaknesses(self, skill_analysis: Dict, experience_analysis: Dict, 
                           education_analysis: Dict) -> List[str]:
        """识别不足"""
        weaknesses = []
        
        if skill_analysis['score'] < 60:
            weaknesses.append(f"技能匹配度较低({skill_analysis['score']}%)，需要提升相关技能")
        
        if experience_analysis['score'] < 60:
            weaknesses.append("工作经验可能不足，需要积累更多相关经验")
        
        if education_analysis['score'] < 60:
            weaknesses.append("教育背景可能不完全符合要求")
        
        if len(skill_analysis['missing']) > 3:
            weaknesses.append(f"缺少{len(skill_analysis['missing'])}项关键技能")
        
        return weaknesses
    
    def _generate_recommendations(self, skill_analysis: Dict, experience_analysis: Dict, 
                                education_analysis: Dict) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 技能相关建议
        if skill_analysis['missing']:
            top_missing = skill_analysis['missing'][:3]
            recommendations.append(f"建议学习以下关键技能：{', '.join(top_missing)}")
        
        if skill_analysis['score'] < 70:
            recommendations.append("在简历中更详细地描述已掌握的技能和项目经验")
        
        # 经验相关建议
        if experience_analysis['score'] < 70:
            if experience_analysis['analysis']['gap_years'] > 0:
                recommendations.append(f"建议积累更多相关工作经验（还需约{experience_analysis['analysis']['gap_years']:.1f}年）")
            else:
                recommendations.append("在简历中更详细地描述工作经历和项目成果")
        
        # 教育相关建议
        if education_analysis['score'] < 70:
            recommendations.append("考虑通过在线课程或认证提升专业背景")
        
        # 通用建议
        recommendations.append("针对目标职位定制简历内容，突出相关经验和技能")
        recommendations.append("准备具体的项目案例来展示技术能力和解决问题的能力")
        
        return recommendations[:5]  # 最多返回5个建议
    
    def _get_match_level(self, score: int) -> str:
        """获取匹配等级"""
        if score >= 85:
            return "优秀匹配"
        elif score >= 70:
            return "良好匹配"
        elif score >= 55:
            return "一般匹配"
        elif score >= 40:
            return "较低匹配"
        else:
            return "匹配度低"
    
    def get_detailed_analysis(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """获取详细分析报告"""
        if not match_data.get('success'):
            return {'error': '匹配分析失败'}
        
        data = match_data['data']
        
        return {
            'summary': {
                'overall_score': data['overall_score'],
                'match_level': data['match_level'],
                'total_matched_skills': len(data['matched_skills']),
                'total_missing_skills': len(data['missing_skills'])
            },
            'score_breakdown': {
                'skills': data['skill_score'],
                'experience': data['experience_score'],
                'education': data['education_score'],
                'keywords': data['keyword_score']
            },
            'strengths_count': len(data['strengths']),
            'weaknesses_count': len(data['weaknesses']),
            'recommendations_count': len(data['recommendations']),
            'improvement_priority': self._get_improvement_priority(data)
        }
    
    def _get_improvement_priority(self, data: Dict[str, Any]) -> List[str]:
        """获取改进优先级"""
        priorities = []
        
        scores = [
            ('技能', data['skill_score']),
            ('经验', data['experience_score']),
            ('学历', data['education_score']),
            ('关键词', data['keyword_score'])
        ]
        
        # 按分数排序，分数低的优先改进
        scores.sort(key=lambda x: x[1])
        
        for area, score in scores:
            if score < 70:
                priorities.append(f"{area}({score}%)")
        
        return priorities[:3]  # 返回前3个优先级