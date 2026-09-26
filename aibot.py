import requests
import json
import time
import threading
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler


BOT_TOKEN = "8652778396:AAF-OglZohWG0eEr0jaGrQI2oAMdgpqguV4"

DEEP_AI_API_KEY = "tryit-30839203218-cad0e109cb0a51c82d256e8244669566"
DEEP_AI_SESSION_UUID = "09cd8161-d2e8-424a-b69c-eb6cc3fe11ca"
DEEP_AI_SENSITIVITY_ID = "86ca9708-ee83-4054-b85a-a70007e070f9"


DEEP_AI_COOKIES = {
    "deepai_device_id": "38wVNk0cTHlx17YMc9u8t-ewFYRpFSmxARjY5kWQTVo",
    "_twpid": "tw.1788259473499.427904894228813417",
    "_kad": "1788259473709.e30b0794-e80b-4c81-813e-7e75ac966381",
    "_fbp": "fb.1.1788259473951.636050830938247053",
    "deepai_privacy_prefs": '%7B%22analytics%22%3Atrue%2C%22ads%22%3Atrue%2C%22audiences%22%3Atrue%2C%22third_party%22%3Atrue%2C%22training%22%3Atrue%2C%22marketing%22%3Atrue%7D',
    "_gcl_au": "1.1.807424234.1788259474",
    "_ga": "GA1.1.915433285.1788259474",
    "_tt_enable_cookie": "1",
    "_ttp": "01M1E947FJ1FXTF6DZ89MD4697_.tt.1",
    "__obref": "3d61c0a4-e24f-4208-b55c-a5ad2290daae",
    "user_sees_ads": "true",
    "_ga_GY2GHX2J9Y": "GS2.1.s1788259474$o1$g1$t1788259920$j60$l0$h0",
    "_uetsid": "1f409f60a5f211f18dee016b75aff32c",
    "_uetvid": "1f411520a5f211f1bcc769fe91feab43",
    "_twsid": '%7B%22id%22%3A%221788259473499-683531432%22%2C%22ct%22%3A1%2C%22ts%22%3A1788259930987%7D',
    "ttcsid": "1788259474957::QUJWo1t8e-MCzgEuvknq.1.1788259975811.0::1.444622.446588::500838.7.304.1552::488231.15.1160",
    "ttcsid_DAAL8KRC77U44RJM9S10": "1788259474953::sduqpjBbSHQwqak2qONP.1.1788259975812.1"
}


user_sessions = {}

def get_user_session(user_id):
    if user_id not in user_sessions:
        session = requests.Session()
        for key, value in DEEP_AI_COOKIES.items():
            session.cookies.set(key, value, domain=".deepai.org")
        user_sessions[user_id] = {
            "session": session,
            "chat_history": [],
            "last_activity": time.time()
        }
    return user_sessions[user_id]

def send_message_to_deepai(user_id, message):
    user_data = get_user_session(user_id)
    session = user_data["session"]
    chat_history = user_data["chat_history"]
    
    chat_history.append({"role": "user", "content": message})
    
    headers = {
        "authority": "api.deepai.org",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "api-key": DEEP_AI_API_KEY,
        "origin": "https://deepai.org",
        "sec-ch-ua": '"Chromium";v="139", "Not;A=Brand";v="99"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36"
    }
    
    boundary = "----WebKitFormBoundary2dRXMsVb9TBsbTiQ"
    
    fields = {
        "chat_style": "chat",
        "chatHistory": json.dumps(chat_history, ensure_ascii=False),
        "model": "standard",
        "session_uuid": DEEP_AI_SESSION_UUID,
        "sensitivity_request_id": DEEP_AI_SENSITIVITY_ID,
        "tool_activity_support": "1",
        "thinking_image_tool_support": "1",
        "hacker_is_stinky": "very_stinky",
        "enabled_tools": '["image_generator","image_editor"]'
    }
    
    parts = []
    for key, value in fields.items():
        parts.append(f'--{boundary}')
        parts.append(f'Content-Disposition: form-data; name="{key}"')
        parts.append('')
        parts.append(value)
    
    parts.append(f'--{boundary}--')
    parts.append('')
    
    body = '\r\n'.join(parts)
    headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    
    response = session.post(
        "https://api.deepai.org/hacking_is_a_serious_crime",
        headers=headers,
        data=body.encode('utf-8')
    )
    
    ai_response = response.text.strip()
    chat_history.append({"role": "assistant", "content": ai_response})
    
    return ai_response

def clear_user_history(user_id):
    if user_id in user_sessions:
        user_sessions[user_id]["chat_history"] = []
        return True
    return False

async def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Start New Chat", callback_data="new_chat")],
        [InlineKeyboardButton("Clear History", callback_data="clear_history")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Welcome to the SOMANI AI Bot!\n\n"
        "Send any message and I will reply.\n"
        "Use the buttons below to manage the conversation.",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_message = update.message.text
    
    if not user_message:
        await update.message.reply_text("Please send text.")
        return
    
    typing_message = await update.message.reply_text("Thinking...")
    
    try:
        ai_response = send_message_to_deepai(user_id, user_message)
        
        if len(ai_response) > 4096:
            for i in range(0, len(ai_response), 4096):
                await update.message.reply_text(ai_response[i:i+4096])
        else:
            await update.message.reply_text(ai_response)
        
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {str(e)}\nThe cookies might have expired.")
    finally:
        await typing_message.delete()

async def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    data = query.data
    
    if data == "new_chat":
        clear_user_history(user_id)
        await query.edit_message_text("Started a new chat. Send your message!")
    
    elif data == "clear_history":
        clear_user_history(user_id)
        await query.edit_message_text("Chat history cleared. Send your message!")

async def help_command(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Available commands:\n"
        "/start - Start the bot\n"
        "/help - Display help\n"
        "/clear - Clear chat history\n"
        "/new - Start a new chat"
    )

async def clear_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if clear_user_history(user_id):
        await update.message.reply_text("Chat history cleared.")
    else:
        await update.message.reply_text("No chat history found.")

async def new_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    clear_user_history(user_id)
    await update.message.reply_text("Started a new chat.")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("clear", clear_command))
    application.add_handler(CommandHandler("new", new_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    print("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
