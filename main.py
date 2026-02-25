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

# 配置 DeepSeek 客户端（关键！使用 OpenAI 兼容接口）
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"  # 必须指向 DeepSeek 的地址
)

async def start(update: Update, context):
    """处理 /start 命令"""
    user = update.effective_user
    await update.message.reply_text(
        f"👋 你好 {user.first_name}！\n\n"
        f"我是 AI 机器人（DeepSeek版），直接发送消息给我，"
        f"我就会用 AI 回复你！\n"
        f"有什么想问的吗？"
    )

async def help_command(update: Update, context):
    """处理 /help 命令"""
    await update.message.reply_text(
        "🤖 使用方法：\n"
        "• 直接发送文字消息，我会回复你\n"
        "• 发送 /start 重新开始\n"
        "• 发送 /help 查看帮助"
    )

async def handle_message(update: Update, context):
    """处理用户消息"""
    try:
        # 获取用户消息
        user_message = update.message.text
        logger.info(f"收到消息: {user_message[:50]}...")
        
        # 发送"正在输入"状态
        await update.message.chat.send_action(action="typing")
        
        # 调用 DeepSeek API
        response = client.chat.completions.create(
            model="deepseek-chat",  # DeepSeek 模型
            messages=[
                {"role": "system", "content": "你是一个友好的 AI 助手，用中文回答。回答要简洁有用。"},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        # 获取回复
        ai_reply = response.choices[0].message.content
        logger.info(f"AI回复: {ai_reply[:50]}...")
        
        # 发送回复（如果太长就分段）
        if len(ai_reply) > 4096:
            for i in range(0, len(ai_reply), 4096):
                await update.message.reply_text(ai_reply[i:i+4096])
        else:
            await update.message.reply_text(ai_reply)
            
    except Exception as e:
        logger.error(f"错误: {e}")
        await update.message.reply_text(f"❌ 出错了：{str(e)}\n请稍后再试。")

def main():
    """主函数"""
    logger.info("🚀 机器人启动中...")
    
    # 创建应用
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # 注册处理器
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # 启动机器人
    logger.info("✅ 机器人启动成功！等待消息...")
    app.run_polling()

if __name__ == '__main__':
    main()
