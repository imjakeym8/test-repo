import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update, context):
        await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text="I'm a bot, la la la."
        )

if __name__ == '__main__':
    application = ApplicationBuilder().token('6267001374:AAGToyLmUcWePIGHvZq9ZQbUTHGVbWYnhv0').build()
    
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    
    application.run_polling()