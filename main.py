import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 从环境变量读取密钥
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')  # 这一行必须完全匹配

# 配置 DeepSeek 客户端
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,  # 这一行用上面的变量
    base_url="https://api.deepseek.com"
)
