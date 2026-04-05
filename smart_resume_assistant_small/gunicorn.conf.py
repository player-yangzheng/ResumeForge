# Gunicorn 生产环境配置
# 使用方式: gunicorn app:app -c gunicorn.conf.py

import multiprocessing

# 工作进程数：CPU核数，最多4个
workers = min(multiprocessing.cpu_count(), 4)

# 每个工作进程的线程数
threads = 2

# 超时时间（秒），LLM调用可能较慢
timeout = 120

# 绑定地址（可通过环境变量覆盖）
bind = "0.0.0.0:5000"

# 日志级别
loglevel = "info"

# 访问日志
accesslog = "-"

# 错误日志
errorlog = "-"

# 预加载应用（节省内存，但注意多进程间共享状态）
preload_app = True
