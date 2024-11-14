import telebot
import telebot.formatting
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import API_KEYS
import google.generativeai as genai
import time

#Gemini
genai.configure(api_key=API_KEYS.genai_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")
genai_chat = model.start_chat()

#Telebot
bot = telebot.TeleBot(API_KEYS.tg_API_KEY)

#------------------------------------------------------
@bot.message_handler(commands=['start'])
def main(message):
    msg = f'Привет, {message.from_user.first_name}! Я ваш личный помощник. Я здесь, чтобы отвечать на ваши вопросы, помогать с информацией и делать ваше общение более интересным. \nПросто напишите, что вас интересует, и я постараюсь помочь!'
    bot.send_message(message.chat.id, msg, parse_mode='html')

help_info = 'Как я могу помочь вам? Вот несколько команд, которые вы можете использовать:\n  /start - начать общение со мной.\n  /info - получить информацию о доступных командах.\n  /вопрос [ваш вопрос] - задать вопрос, на который вы хотите получить ответ.\nЕсли у вас есть другие идеи или вопросы, просто напишите, и я постараюсь вам помочь!'
@bot.message_handler(commands=['info'])
def main(message):
        bot.send_message(message.chat.id, help_info)

# @bot.message_handler(commands=['restart'])
# def restart(message):

#------------------------------------------------------
@bot.message_handler(commands=['вопрос'])
def handle_question(message):

    global genai_chat

    question = message.text[len('/вопрос '):]
    if question:
        genai_response = model.generate_content(question)
        response = genai_response.text
    else:
        response = "Пожалуйста, задайте свой вопрос после команды /вопрос."
    
    bot.reply_to(message, response, parse_mode='Markdown')

#------------------------------------------------------
@bot.message_handler()
def handle_text(message):

    global genai_chat

    responses = ['info', 'information', 'инфо', "информация", "помощь", "help"]
    if message.text.lower() in responses:
        bot.send_message(message.chat.id, help_info)
    else: 
        try:
            response = genai_chat.send_message(message.text, stream=True)
            current_chat_id = message.chat.id
            sended_response = bot.send_message(current_chat_id, '*')
            chunks = []
            last_update_time = time.time()
            for chunk in response:
                chunks.append(chunk.text)
                
                if time.time() - last_update_time > 0.3:
                    bot.edit_message_text(
                        chat_id=current_chat_id, 
                        message_id=sended_response.message_id, 
                        text=''.join(chunks)
                    )
                    last_update_time = time.time()

            bot.edit_message_text(
                chat_id=current_chat_id, 
                message_id=sended_response.message_id, 
                text=''.join(chunks), 
                parse_mode='Markdown'
            )
        except Exception as e:
            print('--------\n', e, '\n--------')

print("Bot initialized")
bot.infinity_polling()
print("Bot ended")