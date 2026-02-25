import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# 设置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 从环境变量读取密钥
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')

# 检查环境变量
if not TELEGRAM_TOKEN:
    logger.error("❌ TELEGRAM_TOKEN 没有设置")
if not DEEPSEEK_API_KEY:
    logger.error("❌ DEEPSEEK_API_KEY 没有设置")

# 配置 DeepSeek 客户端
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /start 命令"""
    await update.message.reply_text('你好！我是AI机器人（DeepSeek版）')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理用户消息"""
    try:
        user_message = update.message.text
        logger.info(f"收到消息: {user_message}")
        
        await update.message.chat.send_action(action="typing")
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": user_message}]
        )
        
        ai_reply = response.choices[0].message.content
        await update.message.reply_text(ai_reply)
        
    except Exception as e:
        logger.error(f"错误: {e}")
        await update.message.reply_text(f'❌ 出错了：{str(e)}')

def main():
    """主函数"""
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("✅ 机器人启动成功！")
    app.run_polling()

if __name__ == '__main__':
    main()
