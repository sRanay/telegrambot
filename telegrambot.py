from telegram.ext import Updater, InlineQueryHandler, CommandHandler
from telegram.ext.dispatcher import run_async
from datetime import datetime
import requests
import re
import random
import threading

# Adds the commands to the bot
def dp_add_handler(dp, cmddict):
    for key, value in cmddict.items():
        dp.add_handler(CommandHandler(key,value))

# Gets the chat id 
def get_chat_id(update):
    chat_id = update.message.chat_id
    return chat_id

# Get the url from the random dog picture
def get_url():
    contents = requests.get('https://random.dog/woof.json').json()    
    url = contents['url']
    return url

# Get the url of the image
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
    chat_id = get_chat_id(update)
    context.bot.send_photo(chat_id=update.message.chat_id, photo=url)

#Sends a random temperature to the user
def temp(update, context):
    tempnum = round(random.uniform(35.8,37.0),1)
    msg = "Your current temperature is " + str(tempnum)
    chat_id = get_chat_id(update)
    context.bot.send_message(chat_id=chat_id, text=msg)

#Send the command list
def commands(update, context):
    commandmsg = """ This is Ranay's Bot.
    \n/commands - Prints out the command list
    \n/temp - Returns a random temperature
    \n/bop - Returns a picture of a random dog
    \n/currenttime - Returns current time"""
    chat_id = get_chat_id(update)
    context.bot.send_message(chat_id=chat_id, text=commandmsg)

# Display current time
def currenttime(update, context):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    chat_id = get_chat_id(update)
    timemsg = "Current Time = " + current_time
    context.bot.send_message(chat_id=chat_id, text=timemsg)

# Shuts down the bot
def shutdown():
    print("Bot is shutting down")
    updater.stop()
    updater.is_idle = False
    print("Bot has shut down")

def stop(update, context):
    threading.Thread(target=shutdown).start()

# List of the command to be use for add_handler
cmddict = {
    'bop': bop,
    'temp': temp,
    'commands': commands,
    'currenttime' : currenttime,
    'stop' : stop,
}

def main():
    print("Bot is starting up")
    dp = updater.dispatcher
    print("Bot has started")
    dp_add_handler(dp,cmddict)
    updater.start_polling()
    updater.idle()

updater = Updater('908776847:AAEpVQDnjYTweN5s7y6_RcxUbl2J1LrGyH0', use_context=True)
if __name__ == '__main__':
    main()