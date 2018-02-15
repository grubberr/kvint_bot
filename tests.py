#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from fsm import OrderPizzaFsm

class TestOrderPizzaFsm(unittest.TestCase):

    def test_start(self):
        fsm = OrderPizzaFsm()
        responses = fsm.push_message('/start')
        self.assertEqual(responses[0]['msg'], 'Заказ пиццы')
        self.assertEqual(responses[1]['msg'], 'Какую вы хотите пиццу?')
        self.assertEqual(responses[1]['buttons'], ['большую', 'маленькую'])

    def test_pizza_big(self):

        fsm = OrderPizzaFsm()
        fsm.to_pizza()
        responses = fsm.push_message('большую')
        self.assertEqual(fsm.pizza_size, 'большую')
        self.assertEqual(fsm.state, 'payment')
        self.assertEqual(responses[0]['msg'], 'Как вы будете платить?')

    def test_pizza_fail(self):

        fsm = OrderPizzaFsm()
        fsm.to_pizza()
        responses = fsm.push_message('незнаю')

        self.assertEqual(fsm.pizza_size, None)
        self.assertEqual(fsm.state, 'pizza')
        self.assertEqual(responses[0]['msg'], 'Какую вы хотите пиццу?')

    def test_payment(self):

        fsm = OrderPizzaFsm()
        fsm.to_payment()
        fsm.pizza_size = 'большую'

        responses = fsm.push_message('наличными')
        self.assertEqual(fsm.payment_type, 'наличными')
        self.assertEqual(fsm.state, 'approve')
        self.assertEqual(responses[0]['msg'], 'Вы хотите большую пиццу, оплата - наличными ?')


if __name__ == '__main__':
    unittest.main()
