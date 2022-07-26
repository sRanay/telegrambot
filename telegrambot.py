import requests
import re
import random
import threading
import os.path
import datetime

from telegram.ext import Updater, InlineQueryHandler, CommandHandler
from telegram.ext.dispatcher import run_async
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# dp_add_handler Function
# Adds the commands to the bot
def dp_add_handler(dp, cmddict):
    for key, value in cmddict.items():
        dp.add_handler(CommandHandler(key,value))

# get_chat_id Function
# Gets the chat id 
def get_chat_id(update):
    chat_id = update.message.chat_id
    return chat_id

# get_url Function
# Get the url from the random dog picture
def get_url():
    contents = requests.get('https://random.dog/woof.json').json()    
    url = contents['url']
    return url

# get_image_url Function
# Get the url of the image
def get_image_url():
    allowed_extension = ['jpg','jpeg','png']
    file_extension = ''
    while file_extension not in allowed_extension:
        url = get_url()
        file_extension = re.search("([^.]*)$",url).group(1).lower()
    return url

# start Function
# Botting starting messages
def start(update, context):
    commandmsg = """Welcome to Ranay's Bot.I have created this bot for fun and to play around what it can do
\nBelow are the list of commands that can work:  
/commands - Prints out the command list
/rng - Returns a random temperature
/bop - Returns a picture of a random dog
/currenttime - Returns current time
/events - Shows upcoming events from Google Calendar"""
    chat_id = get_chat_id(update)
    context.bot.send_message(chat_id=chat_id, text=commandmsg)

# bop Function
# Sends a Picture of a random dog
def bop(update, context):
    url = get_image_url()
    chat_id = get_chat_id(update)
    context.bot.send_photo(chat_id=update.message.chat_id, photo=url)

# rng Function
# Send a Random Number between 1 to 10
def rng(update, context):
    tempnum = round(random.uniform(1,10),1)
    msg = "The number is " + str(tempnum)
    chat_id = get_chat_id(update)
    context.bot.send_message(chat_id=chat_id, text=msg)

# commands Function
# Send the command list
def commands(update, context):
    commandmsg = """ This is Ranay's Bot.
\nBelow are the list of commands that can work:
/commands - Prints out the command list
/rng - Returns a random temperature
/bop - Returns a picture of a random dog
/currenttime - Returns current time
/events - Shows upcoming events from Google Calendar"""
    chat_id = get_chat_id(update)
    context.bot.send_message(chat_id=chat_id, text=commandmsg)

# currenttime Function
# Display current time
def currenttime(update, context):
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    chat_id = get_chat_id(update)
    timemsg = "Current Time = " + current_time
    context.bot.send_message(chat_id=chat_id, text=timemsg)

# events Function
# Returns the upcoming event from the user's google calendar using Google Calendar API
def events(update, context):
    chat_id = get_chat_id(update)
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        print('Getting the upcoming 10 events')
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            context.bot.send_message(chat_id=chat_id, text="No upcoming events found.")
            return

        # Prints the start and name of the next 10 events
        message = "The next up coming 10 events:\n"
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start,"--",event['summary'])
            message += start + " -- " + event['summary'] + "\n"

        context.bot.send_message(chat_id=chat_id, text=message)
    except HttpError as error:
        print('An error occurred: %s' % error)

# shutdown Function
# Shuts down the bot
def shutdown():
    print("Bot is shutting down")
    updater.stop()
    updater.is_idle = False
    print("Bot has shut down")

# stop Function
# Start the shutdown sequence
def stop(update, context):
    threading.Thread(target=shutdown).start()

# List of the command to be use for add_handler
cmddict = {
    'start' : start,
    'bop': bop,
    'rng': rng,
    'commands': commands,
    'currenttime' : currenttime,
    'stop' : stop,
    'events' : events,
}

def main():
    print("Bot is starting up")
    dp = updater.dispatcher
    print("Bot has started")
    dp_add_handler(dp,cmddict)
    updater.start_polling()
    updater.idle()

updater = Updater('<Telegram Bot ID>', use_context=True)
if __name__ == '__main__':
    main()