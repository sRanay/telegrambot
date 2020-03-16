from telegram.ext import Updater, InlineQueryHandler, CommandHandler
from telegram.ext.dispatcher import run_async
import requests
import re
import random

def get_url():
    contents = requests.get('https://random.dog/woof.json').json()    
    url = contents['url']
    return url

def get_image_url():
    allowed_extension = ['jpg','jpeg','png']
    file_extension = ''
    while file_extension not in allowed_extension:
        url = get_url()
        file_extension = re.search("([^.]*)$",url).group(1).lower()
    return url

#Sends a Picture of a random dog
def bop(update, context):
    url = get_image_url()
    chat_id = update.message.chat_id
    context.bot.send_photo(chat_id=update.message.chat_id, photo=url)

def temp(update, context):
    tempnum = round(random.uniform(35.8,37.0),1)
    msg = "Your current temperature is " + str(tempnum)
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id=chat_id, text=msg)

def main():
    updater = Updater('908776847:AAEpVQDnjYTweN5s7y6_RcxUbl2J1LrGyH0', use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('bop',bop))
    dp.add_handler(CommandHandler('temp',temp))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()