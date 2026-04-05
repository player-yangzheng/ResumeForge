# 智能简历助手 - 大模型版本

## 功能升级

本版本集成了大语言模型(LLM)，提供更智能、更准确的简历和职位描述解析功能。

### 新增功能

1. **智能简历解析**：使用大模型理解简历内容，提取更准确的个人信息、工作经历、技能等
2. **智能JD解析**：深度理解职位描述，准确提取职位要求、技能需求等关键信息
3. **智能匹配分析**：基于大模型的语义理解，提供更精准的匹配度分析和建议
4. **自动降级**：如果大模型不可用，自动回退到传统解析方法，确保系统稳定性

## 配置说明

### 方法一：配置文件（推荐）

1. 复制 `config_example.py` 为 `config.py`
2. 编辑 `config.py`，填入你的API密钥：

**使用通义千问（推荐）：**
```python
LLM_CONFIG = {
    'enabled': True,  # 启用大模型
    'provider': 'qwen',
    'qwen': {
        'api_key': 'your_qwen_api_key_here',
        'model': 'qwen-plus'  # 可选：qwen-plus, qwen-turbo, qwen-max
    }
}
```

**使用百度文心一言：**
```python
LLM_CONFIG = {
    'enabled': True,  # 启用大模型
    'provider': 'baidu',
    'baidu': {
        'api_key': 'your_baidu_api_key_here',
        'secret_key': 'your_baidu_secret_key_here'
    }
}
```

### 方法二：环境变量

**通义千问：**
```bash
export DASHSCOPE_API_KEY="your_qwen_api_key_here"
export QWEN_MODEL="qwen-plus"  # 可选
```

**百度文心一言：**
```bash
export BAIDU_API_KEY="your_baidu_api_key_here"
export BAIDU_SECRET_KEY="your_baidu_secret_key_here"
```

## 获取API密钥

### 阿里通义千问（推荐）

1. 注册阿里云账号：https://www.aliyun.com/
2. 开通百炼平台：https://dashscope.console.aliyun.com/
3. 创建API Key：https://dashscope.console.aliyun.com/apiKey
4. 复制API Key到配置文件

**优势：**
- 新用户有免费额度
- 支持多种模型：qwen-plus（推荐）、qwen-turbo、qwen-max等
- API调用简单，兼容OpenAI格式
- 响应速度快，稳定性好

### 百度文心一言（备选方案）

1. 注册百度智能云账号：https://cloud.baidu.com/
2. 开通千帆大模型平台：https://console.bce.baidu.com/qianfan/
3. 创建应用：https://console.bce.baidu.com/qianfan/ais/console/applicationConsole/application
4. 获取API Key和Secret Key

**免费额度：**
- ERNIE-Speed-8K: 每分钟300次请求，每分钟30万tokens
- ERNIE-Lite-8K: 每分钟300次请求，每分钟30万tokens

## 使用说明

1. 配置完成后重启应用
2. 上传简历和输入JD，系统会自动使用大模型进行解析
3. 如果大模型解析失败，会自动使用传统方法作为备选
4. 查看控制台日志了解解析过程

## 优势对比

| 功能 | 传统解析器 | 大模型解析器 |
|------|------------|-------------|
| 姓名提取 | 基于规则，容易出错 | 语义理解，准确率高 |
| 技能识别 | 关键词匹配 | 语义理解，识别同义词 |
| 工作经历 | 格式依赖强 | 适应各种格式 |
| 匹配分析 | 简单统计 | 深度语义分析 |
| 建议质量 | 模板化 | 个性化、专业化 |

## 故障排除

### 常见问题

1. **大模型解析失败**
   - 检查API密钥是否正确
   - 检查网络连接
   - 查看控制台错误信息

2. **配置不生效**
   - 确保config.py文件在正确位置
   - 重启应用
   - 检查配置文件语法

3. **API调用超限**
   - 检查免费额度使用情况
   - 考虑升级付费版本
   - 降低请求频率

### 日志说明

- `从配置文件加载大模型配置成功`：配置加载成功
- `大模型解析器初始化成功`：大模型可用
- `使用大模型解析简历...`：正在使用大模型
- `使用传统方法解析简历...`：回退到传统方法

## 性能建议

1. **首次使用**：大模型API调用需要时间，请耐心等待
2. **批量处理**：避免短时间内大量请求，注意API限制
3. **网络环境**：确保网络稳定，避免超时
4. **内容长度**：过长的简历或JD可能影响解析效果

## 技术架构

```
用户上传 → 文本提取 → 大模型解析 → 结果验证 → 传统解析(备选) → 返回结果
                ↓
            智能匹配分析
                ↓
            个性化建议
```

## 更新日志

- v2.0.0: 集成大模型解析功能
- 支持百度文心一言API
- 自动降级机制
- 配置文件管理