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
    logger.error("⚠️ TELEGRAM_TOKEN 没有设置")
if not DEEPSEEK_API_KEY:
    logger.error("⚠️ DEEPSEEK_API_KEY 没有设置")

# 打印API Key前几位（确认读取成功）
if DEEPSEEK_API_KEY:
    logger.info(f"✅ DeepSeek Key 已读取: {DEEPSEEK_API_KEY[:8]}...")

# 配置 DeepSeek 客户端（关键！）
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com/v1"  # 注意必须有 /v1
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /start 命令"""
    await update.message.reply_text('你好！我是AI机器人（DeepSeek版）')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理用户消息"""
    try:
        # 获取用户消息
        user_message = update.message.text
        logger.info(f"📨 收到消息: {user_message}")
        
        # 发送"正在输入"状态
        await update.message.chat.send_action(action="typing")
        
        # 调用 DeepSeek API
        logger.info("🔄 调用 DeepSeek API...")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个友好的AI助手，用中文回答。"},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        # 获取回复
        ai_reply = response.choices[0].message.content
        logger.info(f"💬 AI回复: {ai_reply[:50]}...")
        
        # 发送回复
        await update.message.reply_text(ai_reply)
        
    except Exception as e:
        logger.error(f"❌ 错误: {e}")
        await update.message.reply_text(f'出错了：{str(e)}')

def main():
    """主函数"""
    logger.info("🚀 机器人启动中...")
    
    # 创建应用
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # 注册处理器
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # 启动机器人
    logger.info("✅ 机器人启动成功！等待消息...")
    app.run_polling()

if __name__ == '__main__':
    main()
