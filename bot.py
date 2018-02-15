#!/Users/ant/kvint_bot/env/bin/python3
# -*- coding: utf-8 -*-

import os
import time
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
from transitions import Machine
from fsm import OrderPizzaFsm

fsm = OrderPizzaFsm()

def handle(msg):

    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type == 'text':

        responses = fsm.push_message(msg['text'])

        for resp in responses:

            reply_markup = None
            if 'buttons' in resp:

                keyboard = [[KeyboardButton(text=text) for text in resp['buttons']]]
                reply_markup = ReplyKeyboardMarkup(
                    keyboard=keyboard,
                    resize_keyboard=True,
                    one_time_keyboard=True)

            bot.sendMessage(chat_id, resp['msg'], reply_markup=reply_markup)


TOKEN = os.environ['TOKEN']
bot = telepot.Bot(TOKEN)
MessageLoop(bot, handle).run_as_thread()

while 1:
    time.sleep(10)
