"""
京东自动登录配置文件
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """配置类"""

    # 京东登录信息
    JD_USERNAME = os.getenv('JD_USERNAME', '')
    JD_PASSWORD = os.getenv('JD_PASSWORD', '')

    # AI模型配置
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    AI_MODEL = os.getenv('AI_MODEL', 'claude')  # claude 或 openai

    # 浏览器配置
    HEADLESS = os.getenv('HEADLESS', 'false').lower() == 'true'
    WAIT_TIME = int(os.getenv('WAIT_TIME', '10'))

    # 京东URL
    JD_LOGIN_URL = 'https://passport.jd.com/new/login.aspx'

    @classmethod
    def validate(cls):
        """验证配置是否完整"""
        if not cls.JD_USERNAME or not cls.JD_PASSWORD:
            raise ValueError("请在.env文件中配置JD_USERNAME和JD_PASSWORD")

        if cls.AI_MODEL == 'claude' and not cls.ANTHROPIC_API_KEY:
            raise ValueError("使用Claude模型需要配置ANTHROPIC_API_KEY")

        if cls.AI_MODEL == 'openai' and not cls.OPENAI_API_KEY:
            raise ValueError("使用OpenAI模型需要配置OPENAI_API_KEY")

        return True
