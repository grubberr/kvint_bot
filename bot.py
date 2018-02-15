#!/Users/ant/kvint_bot/env/bin/python3
# -*- coding: utf-8 -*-

import os
import time
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
from transitions import Machine

def normalize_message(msg):
    return msg.strip().lower()

class OrderPizzaFsm:

    state_meta = {
        'start': {'output': 'Заказ пиццы'},
        'pizza': {'output': 'Какую вы хотите пиццу?', 'buttons': ['большую', 'маленькую']},
        'payment': {'output': 'Как вы будете платить?'},
        'approve': {'output': lambda self: self.output_approve, 'buttons': ['да', 'нет']},
        'order': {'output': 'Спасибо за заказ'},
        'skip_order': {'output': 'ну нет так нет :)'}
    }

    def __init__(self):

        self.machine = Machine(model=self,
                               states=list(self.state_meta.keys()),
                               initial='start')

        self.machine.add_transition(trigger='next', source='start', dest='pizza')
        self.machine.add_transition(trigger='next', source='pizza', dest='payment')
        self.machine.add_transition(trigger='next', source='payment', dest='approve')
        self.machine.add_transition(trigger='next', source='approve', dest='order')
        self.machine.add_transition(trigger='next', source='order', dest='pizza')
        self.machine.add_transition(trigger='next', source='skip_order', dest='pizza')


    def output_approve(self):
        return 'Вы хотите %s пиццу, оплата - %s ?' % (self.pizza_size, self.payment_type)

    def input_pizza(self, msg):

        msg = normalize_message(msg)
        if msg in self.state_meta[self.state]['buttons']:
            self.pizza_size = msg
            return 'next'

        return 'to_pizza'

    def input_payment(self, msg):

        msg = normalize_message(msg)
        self.payment_type = msg
        return 'next'

    def input_approve(self, msg):

        msg = normalize_message(msg)
        if msg == 'да':
            return 'next'
        if msg == 'нет':
            return 'to_skip_order'

        return 'to_approve'

    def input_order(self, msg):
        return 'next'

    def input_skip_order(self, msg):
        return 'next'

    def get_output(self):

        msg = self.state_meta[self.state]['output']
        if callable(msg):
            msg = msg(self)()

        msg = {'msg': msg}
        if 'buttons' in self.state_meta[self.state]:
            msg['buttons'] = self.state_meta[self.state]['buttons']

        return msg

    def push_message(self, msg):

        if msg == '/start' or not hasattr(self, 'input_' + self.state):
            self.trigger('to_start')
        else:
            next_state = getattr(self, 'input_' + self.state)(msg)
            self.trigger(next_state)

        outputs = []
        while True:
            outputs.append(self.get_output())

            if hasattr(self, 'input_' + self.state):
                break

            self.trigger('next')

        return outputs



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
