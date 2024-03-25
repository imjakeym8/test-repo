import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
import os

#logging.basicConfig(
#    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#    level=logging.INFO
#)
my_secret = os.environ['PRIVATE_KEY']

# Chat group I'm basing on @anothertrashgroup
chat_id = -1001936065448

# Mutes users on TG
no_permission = ChatPermissions(can_send_messages=False)

# Unmutes users on TG
default_permissions = ChatPermissions(can_send_messages=True)

#Inside bot DM function only
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    markup = [
        [InlineKeyboardButton("1️⃣", callback_data="1")],
        [InlineKeyboardButton("2️⃣", callback_data="2")],
        [InlineKeyboardButton("3️⃣", callback_data="3")],
        [InlineKeyboardButton("4️⃣", callback_data="4")]
      ]
    reply_markup = InlineKeyboardMarkup(markup)

    user_id = update.message.from_user.id
    member_status = await context.bot.get_chat_member(chat_id, user_id)

    #print(member_status.status)
    # Checks if user is muted and already in the group. /start does not work if user left, or unmuted already.
    if member_status.status == 'restricted' and not member_status.can_send_messages:
      #print(True)
      with open("bananacat.jpg", "rb") as photo:
        await update.message.reply_photo(
            photo=photo,
            caption="What is your answer to this question?",
            reply_markup=reply_markup)
    #else:
    #    print(False)
    #print("/start - command working")

#Event-based function
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    markup = [
      [InlineKeyboardButton("Confirm your identification here", url="https://t.me/tgspamcleanserbot?start=start")]
    ]
    reply_markup = InlineKeyboardMarkup(markup)

    joined = update.message.new_chat_members
    new_members = [member.username for member in joined]
    #print(new_members)

    for member in joined:
      if member.id != context.bot.id:
        await context.bot.restrict_chat_member(chat_id, member.id, no_permission) # Mutes user after joining

    each_username = ', '.join([f"@{username}" for username in new_members])
    await update.message.reply_text(f"Welcome {each_username}. Go here ⏬", reply_markup=reply_markup)
    #print("/welcome - command triggered")

#Callback Query for Buttons function
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    query.answer()

    if query.data == "1":
      await query.message.reply_text("Wrong 1️⃣")
    elif query.data == "2":
      await query.message.reply_text("Wrong 2️⃣")
    elif query.data == "3":
      await query.message.reply_text("Wrong 3️⃣")
    elif query.data == "4":
      user_id = query.from_user.id
      await context.bot.restrict_chat_member(chat_id, user_id, default_permissions) # Unmutes user
      await query.message.reply_text("Correct 4️⃣. You can go back in the chats!")

def main():
    app = ApplicationBuilder().token(my_secret).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()


if __name__ == "__main__":
    main()
