# 智能简历助手配置文件示例
# 复制此文件为 config.py 并填入你的API密钥
import os
# 大模型配置
LLM_CONFIG = {
    # 是否启用大模型解析（需要配置API密钥）
    'enabled': True,
    
    # 大模型提供商：'baidu'（百度文心一言）或 'qwen'（阿里通义千问）
    'provider': 'qwen',  # 推荐使用通义千问
    
    # 百度文心一言配置
    # 获取地址：https://console.bce.baidu.com/qianfan/ais/console/applicationConsole/application
    'baidu': {
        'api_key': 'your_baidu_api_key_here',
        'secret_key': 'your_baidu_secret_key_here'
    },
    
    # 阿里通义千问配置
    # 获取地址：https://dashscope.console.aliyun.com/
    'qwen': {
        'api_key': os.getenv('OPENAI_API_KEY'),
        'model': 'qwen-plus'  # 可选：qwen-plus, qwen-turbo, qwen-max, qwen-max-latest
    }
}

# 使用说明：

# 方式一：使用阿里通义千问（推荐）
# 1. 注册阿里云账号：https://www.aliyun.com/
# 2. 开通百炼平台：https://dashscope.console.aliyun.com/
# 3. 创建API Key：https://dashscope.console.aliyun.com/apiKey
# 4. 将API Key填入上述 qwen 配置中
# 5. 将 provider 设置为 'qwen'
# 6. 将 enabled 设置为 True
# 7. 重启应用即可使用

# 方式二：使用百度文心一言
# 1. 注册百度智能云账号：https://cloud.baidu.com/
# 2. 开通千帆大模型平台：https://console.bce.baidu.com/qianfan/
# 3. 创建应用获取API Key和Secret Key
# 4. 将密钥填入上述 baidu 配置中
# 5. 将 provider 设置为 'baidu'
# 6. 将 enabled 设置为 True
# 7. 重启应用即可使用

# 免费额度说明：
# 通义千问：
# - 新用户有免费额度，具体额度请查看官网
# - 支持多种模型：qwen-plus（推荐）、qwen-turbo、qwen-max等
# 
# 百度文心一言：
# - ERNIE-Speed-8K: RPM=300, TPM=300000
# - ERNIE-Lite-8K: RPM=300, TPM=300000