import os
from dotenv import load_dotenv
from passlib.context import CryptContext

# 加载环境变量
load_dotenv()  # 从 .env 文件或环境变量加载


class Config:
    """基础配置 - 所有环境共享的配置"""
    # Flask 配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key-for-development')
    DEBUG = os.getenv('FLASK_DEBUG', '0') == '1'
    TESTING = False

    # 数据库配置 (MongoDB)
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    DB_NAME = os.getenv('DB_NAME', 'chat_analysis')

    # MONGO连接池设置
    MONGO_CONNECT_TIMEOUT_MS = int(os.getenv('MONGO_CONNECT_TIMEOUT_MS', '5000'))
    MONGO_SOCKET_TIMEOUT_MS = int(os.getenv('MONGO_SOCKET_TIMEOUT_MS', '30000'))

    # Token管理
    TTL_MINUTES = 60

    # 文件储存管理
    ALLOWED_EXTENSIONS = {'txt'}
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')

    # 哈希加密参数
    pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

    # DeepSeek API 配置
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
    DEEPSEEK_BASE_URL = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1')
    DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')

    # API 限制与超时
    DEEPSEEK_TIMEOUT = int(os.getenv('DEEPSEEK_TIMEOUT', '30'))
    DEEPSEEK_MAX_TOKENS = int(os.getenv('DEEPSEEK_MAX_TOKENS', '2000'))

    # 线程池设置
    THREAD_POOL_SIZE = int(os.getenv('THREAD_POOL_SIZE', '4'))

    # 缓存配置
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'SimpleCache')
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', '300'))  # 5分钟

    # 聊天记录解析参数
    MAX_MESSAGES_PER_ANALYSIS = int(os.getenv('MAX_MESSAGES_PER_ANALYSIS', '5000'))

    # 分析结果保留策略
    ANALYSIS_RETENTION_DAYS = int(os.getenv('ANALYSIS_RETENTION_DAYS', '30'))

    # DEEPSEEK默认分析提示
    DEFAULT_ANALYSIS_PROMPT = os.getenv(
        'DEFAULT_ANALYSIS_PROMPT',
        "你是一个专业的聊天记录分析师。请分析以下聊天内容，包括但不限于：\n"
        "1. 主要讨论话题\n2. 情感倾向\n3. 关键人物\n4. 潜在问题或冲突\n"
        "5. 任何有趣的观察结果\n\n分析要求：使用专业、客观的语言，提供结构化分析报告。"
    )


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    pass


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    pass


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    pass


# 配置映射
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
