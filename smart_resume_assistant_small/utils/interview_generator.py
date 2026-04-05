from typing import Dict, List, Any, Optional
import random

class InterviewQuestionGenerator:
    """简化版面试问题生成器"""
    
    def __init__(self):
        # 问题模板库
        self.question_templates = {
            'technical': {
                'programming': [
                    "请解释一下{skill}的核心特性和优势？",
                    "在{skill}开发中，你遇到过哪些挑战？如何解决的？",
                    "能否描述一个你用{skill}完成的项目？",
                    "你认为{skill}与其他类似技术相比有什么优势？",
                    "在{skill}项目中，你是如何进行代码优化的？"
                ],
                'frameworks': [
                    "你在{skill}框架中最常用的功能有哪些？",
                    "使用{skill}开发时，你是如何处理性能优化的？",
                    "能否分享一个使用{skill}解决复杂问题的经验？",
                    "你认为{skill}的最佳实践是什么？",
                    "在{skill}项目中，你是如何进行测试的？"
                ],
                'databases': [
                    "你在{skill}中是如何进行查询优化的？",
                    "能否描述一下{skill}的数据建模经验？",
                    "在使用{skill}时，你是如何处理数据一致性的？",
                    "你对{skill}的索引策略有什么理解？",
                    "在{skill}项目中，你遇到过哪些性能问题？"
                ],
                'tools': [
                    "你在项目中是如何使用{skill}的？",
                    "能否分享一个{skill}帮助你提高效率的例子？",
                    "你认为{skill}在团队协作中的作用是什么？",
                    "使用{skill}时，你遵循哪些最佳实践？",
                    "你是如何学习和掌握{skill}的？"
                ]
            },
            'behavioral': [
                "请描述一个你在工作中遇到的挑战，以及你是如何解决的？",
                "谈谈你在团队合作中的经验，你通常扮演什么角色？",
                "描述一次你需要在紧急期限内完成任务的经历。",
                "你是如何保持技术技能的更新和学习的？",
                "谈谈你对这个职位的理解和期望。",
                "描述一个你主导的项目，你是如何规划和执行的？",
                "你在工作中遇到过分歧吗？是如何处理的？",
                "谈谈你的职业规划和发展目标。",
                "描述一次你从失败中学到重要经验的经历。",
                "你认为自己最大的优势和需要改进的地方是什么？"
            ],
            'situational': [
                "如果你发现代码中有一个严重的bug，但修复它可能会影响项目进度，你会怎么处理？",
                "假设你需要学习一个全新的技术来完成项目，你会如何安排学习计划？",
                "如果团队成员对技术方案有不同意见，你会如何协调？",
                "当你发现现有的解决方案不是最优的，但重构需要大量时间，你会怎么决策？",
                "如果客户要求在很短时间内增加新功能，你会如何应对？",
                "假设你在代码审查中发现同事的代码有问题，你会如何处理？",
                "如果你负责的模块出现了生产环境问题，你会采取什么步骤？",
                "当你需要向非技术人员解释复杂的技术问题时，你会怎么做？",
                "如果你发现团队的开发流程有改进空间，你会如何推动改变？",
                "假设你需要在多个紧急任务之间分配时间，你会如何优先排序？"
            ],
            'company_specific': [
                "你为什么想加入我们公司？",
                "你对我们公司的产品/服务有什么了解？",
                "你认为这个职位最大的挑战是什么？",
                "你期望在这个职位上取得什么成就？",
                "你对我们公司的技术栈有什么看法？",
                "你认为自己能为团队带来什么价值？",
                "你对远程工作/团队协作有什么看法？",
                "你希望在这个职位上学到什么？",
                "你对公司的发展方向有什么想法？",
                "你还有什么问题想了解的吗？"
            ]
        }
        
        # 技能分类映射
        self.skill_categories = {
            'programming': ['python', 'java', 'javascript', 'c++', 'c#', 'go', 'rust', 'php'],
            'frameworks': ['react', 'vue', 'angular', 'django', 'flask', 'spring', 'express', 'laravel'],
            'databases': ['mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sqlite'],
            'tools': ['git', 'docker', 'kubernetes', 'aws', 'jenkins', 'nginx', 'linux']
        }
        
        # 难度级别定义
        self.difficulty_levels = {
            'junior': {
                'technical_ratio': 0.4,
                'behavioral_ratio': 0.4,
                'situational_ratio': 0.2,
                'focus': ['基础概念', '学习能力', '团队合作']
            },
            'mid': {
                'technical_ratio': 0.5,
                'behavioral_ratio': 0.3,
                'situational_ratio': 0.2,
                'focus': ['技术深度', '问题解决', '项目经验']
            },
            'senior': {
                'technical_ratio': 0.4,
                'behavioral_ratio': 0.3,
                'situational_ratio': 0.3,
                'focus': ['架构设计', '技术领导', '决策能力']
            }
        }
    
    def generate_interview_questions(self, resume_data: Dict[str, Any], 
                                   jd_data: Dict[str, Any], 
                                   difficulty: str = 'mid',
                                   question_count: int = 15) -> Dict[str, Any]:
        """生成面试问题"""
        try:
            if not resume_data.get('success') or not jd_data.get('success'):
                raise ValueError("简历或职位描述数据无效")
            
            # 提取技能信息
            resume_skills = self._extract_skills_from_resume(resume_data)
            jd_skills = self._extract_skills_from_jd(jd_data)
            
            # 找到匹配的技能
            matched_skills = self._find_matched_skills(resume_skills, jd_skills)
            
            # 根据难度级别分配问题类型
            question_distribution = self._calculate_question_distribution(difficulty, question_count)
            
            # 生成各类型问题
            questions = {
                'technical': self._generate_technical_questions(
                    matched_skills, question_distribution['technical']
                ),
                'behavioral': self._generate_behavioral_questions(
                    question_distribution['behavioral']
                ),
                'situational': self._generate_situational_questions(
                    question_distribution['situational']
                ),
                'company_specific': self._generate_company_questions(
                    question_distribution.get('company_specific', 2)
                )
            }
            
            # 生成面试准备建议
            preparation_tips = self._generate_preparation_tips(matched_skills, difficulty)
            
            # 生成评估标准
            evaluation_criteria = self._generate_evaluation_criteria(difficulty)
            
            # 将questions对象转换为扁平数组格式，以便前端处理
            questions_array = []
            for category, question_list in questions.items():
                for question in question_list:
                    if isinstance(question, dict):
                        questions_array.append(question)
                    else:
                        # 如果是字符串，转换为标准格式
                        questions_array.append({
                            'question': question,
                            'type': category,
                            'id': f"{category}_{len(questions_array) + 1}",
                            'focus': 'general'
                        })
            
            return {
                'success': True,
                'data': {
                    'questions': questions_array,  # 返回扁平数组而不是分类对象
                    'questions_by_category': questions,  # 保留原始分类结构供其他用途
                    'total_questions': sum(len(q) for q in questions.values()),
                    'difficulty_level': difficulty,
                    'matched_skills': matched_skills,
                    'preparation_tips': preparation_tips,
                    'evaluation_criteria': evaluation_criteria,
                    'interview_structure': self._generate_interview_structure(questions)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': None
            }
    
    def _extract_skills_from_resume(self, resume_data: Dict[str, Any]) -> List[str]:
        """从简历中提取技能"""
        skills = []
        
        if resume_data.get('success'):
            resume_skills = resume_data['data'].get('skills', {})
            
            # 合并所有技能类别
            for category, skill_list in resume_skills.items():
                if isinstance(skill_list, list):
                    skills.extend(skill_list)
                elif isinstance(skill_list, str):
                    skills.append(skill_list)
        
        return [skill.lower().strip() for skill in skills if skill.strip()]
    
    def _extract_skills_from_jd(self, jd_data: Dict[str, Any]) -> List[str]:
        """从职位描述中提取技能"""
        skills = []
        
        if jd_data.get('success'):
            jd_skills = jd_data['data'].get('skills', {})
            
            # 合并所有技能类别
            for category, skill_list in jd_skills.items():
                if isinstance(skill_list, list):
                    skills.extend(skill_list)
                elif isinstance(skill_list, str):
                    skills.append(skill_list)
        
        return [skill.lower().strip() for skill in skills if skill.strip()]
    
    def _find_matched_skills(self, resume_skills: List[str], jd_skills: List[str]) -> Dict[str, List[str]]:
        """找到匹配的技能并分类"""
        matched = {'programming': [], 'frameworks': [], 'databases': [], 'tools': [], 'other': []}
        
        # 找到简历和JD中都有的技能
        common_skills = set(resume_skills) & set(jd_skills)
        
        # 按类别分类匹配的技能
        for skill in common_skills:
            categorized = False
            for category, keywords in self.skill_categories.items():
                if any(keyword in skill for keyword in keywords):
                    matched[category].append(skill)
                    categorized = True
                    break
            if not categorized:
                matched['other'].append(skill)
        
        # 移除空的类别
        return {k: v for k, v in matched.items() if v}
    
    def _calculate_question_distribution(self, difficulty: str, total_count: int) -> Dict[str, int]:
        """计算各类型问题的数量分配"""
        level_config = self.difficulty_levels.get(difficulty, self.difficulty_levels['mid'])
        
        distribution = {
            'technical': int(total_count * level_config['technical_ratio']),
            'behavioral': int(total_count * level_config['behavioral_ratio']),
            'situational': int(total_count * level_config['situational_ratio'])
        }
        
        # 确保总数正确
        remaining = total_count - sum(distribution.values())
        distribution['company_specific'] = max(2, remaining)
        
        return distribution
    
    def _generate_technical_questions(self, matched_skills: Dict[str, List[str]], count: int) -> List[Dict[str, str]]:
        """生成技术问题"""
        questions = []
        
        if not matched_skills:
            # 如果没有匹配技能，生成通用技术问题
            general_questions = [
                "请介绍一下你最熟悉的编程语言及其特点。",
                "描述一个你认为技术上有挑战性的项目。",
                "你是如何保持技术技能更新的？",
                "谈谈你对代码质量的理解。",
                "你在项目中是如何进行调试的？"
            ]
            for i, question in enumerate(general_questions[:count]):
                questions.append({
                    'id': f'tech_{i+1}',
                    'question': question,
                    'type': 'general',
                    'difficulty': 'medium'
                })
            return questions
        
        question_id = 1
        
        # 为每个技能类别生成问题
        for category, skills in matched_skills.items():
            if question_id > count:
                break
                
            category_templates = self.question_templates['technical'].get(category, 
                                self.question_templates['technical']['tools'])
            
            for skill in skills:
                if question_id > count:
                    break
                    
                # 随机选择一个模板
                template = random.choice(category_templates)
                question_text = template.format(skill=skill)
                
                questions.append({
                    'id': f'tech_{question_id}',
                    'question': question_text,
                    'skill': skill,
                    'category': category,
                    'type': 'technical',
                    'difficulty': 'medium'
                })
                
                question_id += 1
        
        # 如果问题不够，添加通用技术问题
        while len(questions) < count:
            general_questions = [
                "请解释一下你对软件架构设计的理解。",
                "你是如何进行代码审查的？",
                "描述一下你的测试策略。",
                "你对敏捷开发有什么看法？",
                "谈谈你对性能优化的经验。"
            ]
            
            if len(questions) < len(general_questions):
                questions.append({
                    'id': f'tech_{len(questions)+1}',
                    'question': general_questions[len(questions)],
                    'type': 'general',
                    'difficulty': 'medium'
                })
            else:
                break
        
        return questions[:count]
    
    def _generate_behavioral_questions(self, count: int) -> List[Dict[str, str]]:
        """生成行为问题"""
        questions = []
        selected_questions = random.sample(self.question_templates['behavioral'], 
                                         min(count, len(self.question_templates['behavioral'])))
        
        for i, question in enumerate(selected_questions):
            questions.append({
                'id': f'behavioral_{i+1}',
                'question': question,
                'type': 'behavioral',
                'focus': 'soft_skills'
            })
        
        return questions
    
    def _generate_situational_questions(self, count: int) -> List[Dict[str, str]]:
        """生成情境问题"""
        questions = []
        selected_questions = random.sample(self.question_templates['situational'], 
                                         min(count, len(self.question_templates['situational'])))
        
        for i, question in enumerate(selected_questions):
            questions.append({
                'id': f'situational_{i+1}',
                'question': question,
                'type': 'situational',
                'focus': 'problem_solving'
            })
        
        return questions
    
    def _generate_company_questions(self, count: int) -> List[Dict[str, str]]:
        """生成公司相关问题"""
        questions = []
        selected_questions = random.sample(self.question_templates['company_specific'], 
                                         min(count, len(self.question_templates['company_specific'])))
        
        for i, question in enumerate(selected_questions):
            questions.append({
                'id': f'company_{i+1}',
                'question': question,
                'type': 'company_specific',
                'focus': 'cultural_fit'
            })
        
        return questions
    
    def _generate_preparation_tips(self, matched_skills: Dict[str, List[str]], difficulty: str) -> Dict[str, List[str]]:
        """生成面试准备建议"""
        tips = {
            'technical_preparation': [],
            'behavioral_preparation': [],
            'general_tips': []
        }
        
        # 技术准备建议
        if matched_skills:
            tips['technical_preparation'] = [
                f"复习{', '.join(sum(matched_skills.values(), [])[:5])}等核心技能",
                "准备具体的项目案例，能够详细描述技术实现",
                "练习编程题目，特别是与职位相关的算法",
                "了解最新的技术趋势和最佳实践",
                "准备技术问题的STAR格式回答"
            ]
        else:
            tips['technical_preparation'] = [
                "复习基础编程概念和数据结构",
                "准备项目经验的技术细节描述",
                "练习常见的编程面试题",
                "了解目标公司的技术栈"
            ]
        
        # 行为面试准备
        tips['behavioral_preparation'] = [
            "准备STAR格式的故事案例（情况-任务-行动-结果）",
            "思考职业发展目标和动机",
            "准备团队合作和冲突解决的例子",
            "反思个人优势和改进领域",
            "了解公司文化和价值观"
        ]
        
        # 通用建议
        tips['general_tips'] = [
            "提前了解公司背景和产品",
            "准备有质量的问题询问面试官",
            "练习清晰简洁的表达",
            "准备简历中每个项目的详细说明",
            "保持积极自信的态度"
        ]
        
        return tips
    
    def _generate_evaluation_criteria(self, difficulty: str) -> Dict[str, List[str]]:
        """生成评估标准"""
        criteria = {
            'technical_skills': [
                "技术知识的深度和广度",
                "问题分析和解决能力",
                "代码质量意识",
                "学习能力和适应性"
            ],
            'soft_skills': [
                "沟通表达能力",
                "团队协作精神",
                "主动性和责任心",
                "抗压能力"
            ],
            'cultural_fit': [
                "价值观匹配度",
                "工作态度",
                "发展潜力",
                "对公司的了解和兴趣"
            ]
        }
        
        if difficulty == 'senior':
            criteria['leadership'] = [
                "技术领导能力",
                "决策能力",
                "团队管理经验",
                "战略思维"
            ]
        
        return criteria
    
    def _generate_interview_structure(self, questions: Dict[str, List]) -> Dict[str, Any]:
        """生成面试结构建议"""
        total_questions = sum(len(q) for q in questions.values())
        
        structure = {
            'duration': f"{max(45, total_questions * 3)}分钟",
            'phases': [
                {
                    'phase': '开场介绍',
                    'duration': '5分钟',
                    'content': '自我介绍、简历概述'
                },
                {
                    'phase': '技术问题',
                    'duration': f"{len(questions.get('technical', [])) * 3}分钟",
                    'content': '技能相关问题、项目经验'
                },
                {
                    'phase': '行为问题',
                    'duration': f"{len(questions.get('behavioral', [])) * 2}分钟",
                    'content': '团队合作、问题解决经验'
                },
                {
                    'phase': '情境问题',
                    'duration': f"{len(questions.get('situational', [])) * 2}分钟",
                    'content': '假设场景、决策能力'
                },
                {
                    'phase': '公司相关',
                    'duration': f"{len(questions.get('company_specific', [])) * 2}分钟",
                    'content': '公司了解、职位期望'
                },
                {
                    'phase': '候选人提问',
                    'duration': '5-10分钟',
                    'content': '候选人向面试官提问'
                }
            ],
            'tips': [
                "保持轻松友好的氛围",
                "给候选人充分的思考时间",
                "记录关键回答要点",
                "观察候选人的沟通方式",
                "确保所有重要领域都有覆盖"
            ]
        }
        
        return structure
    
    def generate_mock_interview_script(self, questions: Dict[str, List]) -> Dict[str, Any]:
        """生成模拟面试脚本"""
        try:
            script = {
                'introduction': {
                    'interviewer': "您好，欢迎参加今天的面试。请先简单介绍一下自己和您的背景。",
                    'time_limit': "3-5分钟",
                    'notes': "观察候选人的表达能力和自信程度"
                },
                'main_questions': [],
                'closing': {
                    'interviewer': "感谢您今天的时间。您对我们公司或这个职位还有什么问题吗？",
                    'notes': "评估候选人的主动性和对职位的兴趣"
                }
            }
            
            # 整理所有问题
            all_questions = []
            for category, question_list in questions.items():
                for q in question_list:
                    q['category'] = category
                    all_questions.append(q)
            
            # 按推荐顺序排列问题
            ordered_questions = self._order_questions_for_interview(all_questions)
            
            for i, question in enumerate(ordered_questions):
                script['main_questions'].append({
                    'order': i + 1,
                    'question': question['question'],
                    'category': question.get('category', 'general'),
                    'expected_duration': '2-5分钟',
                    'evaluation_points': self._get_evaluation_points(question),
                    'follow_up_suggestions': self._get_follow_up_suggestions(question)
                })
            
            return {
                'success': True,
                'data': script
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': None
            }
    
    def _order_questions_for_interview(self, questions: List[Dict]) -> List[Dict]:
        """为面试排序问题"""
        # 推荐的问题顺序：技术 -> 行为 -> 情境 -> 公司相关
        order_priority = {
            'technical': 1,
            'behavioral': 2,
            'situational': 3,
            'company_specific': 4
        }
        
        return sorted(questions, key=lambda x: order_priority.get(x.get('category', 'technical'), 5))
    
    def _get_evaluation_points(self, question: Dict) -> List[str]:
        """获取问题的评估要点"""
        category = question.get('category', 'general')
        
        evaluation_points = {
            'technical': [
                "技术知识的准确性",
                "解释的清晰度",
                "实际应用经验",
                "问题解决思路"
            ],
            'behavioral': [
                "具体例子的完整性",
                "个人角色和贡献",
                "学习和成长",
                "团队合作能力"
            ],
            'situational': [
                "分析问题的逻辑",
                "解决方案的合理性",
                "考虑因素的全面性",
                "决策过程"
            ],
            'company_specific': [
                "对公司的了解程度",
                "职位匹配度",
                "动机和热情",
                "长期发展规划"
            ]
        }
        
        return evaluation_points.get(category, ["回答的完整性", "逻辑清晰度", "相关性"])
    
    def _get_follow_up_suggestions(self, question: Dict) -> List[str]:
        """获取追问建议"""
        category = question.get('category', 'general')
        
        follow_ups = {
            'technical': [
                "能否详细说明实现细节？",
                "遇到过什么技术难点？",
                "如何进行性能优化？",
                "有什么改进的想法？"
            ],
            'behavioral': [
                "您在其中的具体作用是什么？",
                "结果如何？有什么收获？",
                "如果重新来过，会有什么不同？",
                "团队其他成员的反馈如何？"
            ],
            'situational': [
                "还有其他解决方案吗？",
                "如何评估风险？",
                "需要哪些资源支持？",
                "如何确保执行效果？"
            ],
            'company_specific': [
                "您最感兴趣的是哪个方面？",
                "您认为最大的挑战是什么？",
                "您希望在团队中发挥什么作用？",
                "您的期望薪资范围是多少？"
            ]
        }
        
        return follow_ups.get(category, ["能否举个具体例子？", "您是如何学习的？"])