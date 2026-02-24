import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import openai

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 从环境变量读取密钥
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# 初始化 OpenAI
openai.api_key = OPENAI_API_KEY

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /start 命令"""
    await update.message.reply_text(
        '🤖 你好！我是 AI 机器人。\n'
        '直接发送消息给我，我就会用 AI 回复你！'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理用户消息"""
    try:
        # 获取用户消息
        user_message = update.message.text
        logger.info(f"收到消息: {user_message[:50]}...")
        
        # 发送"正在输入"状态
        await update.message.chat.send_action(action="typing")
        
        # 调用 OpenAI API
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一个友好的 AI 助手，用中文回答。"},
                {"role": "user", "content": user_message}
            ],
            max_tokens=1000
        )
        
        # 获取并发送回复
        ai_reply = response.choices[0].message.content
        await update.message.reply_text(ai_reply)
        
    except Exception as e:
        logger.error(f"错误: {e}")
        await update.message.reply_text(f'❌ 出错了：{str(e)}')

def main():
    """主函数"""
    # 检查环境变量
    if not TELEGRAM_TOKEN:
        logger.error("请设置 TELEGRAM_TOKEN")
        return
    if not OPENAI_API_KEY:
        logger.error("请设置 OPENAI_API_KEY")
        return
    
    # 创建应用
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # 注册处理器
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # 启动机器人
    logger.info("✅ 机器人启动成功！")
    app.run_polling()

if __name__ == '__main__':
    main()