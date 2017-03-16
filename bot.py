#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardMarkup,InlineKeyboardButton

from emoji import emojize
import pymysql.cursors
import logging

def openConnection():
    return pymysql.connect(host='localhost',
                           user='root',
                           password='root',
                           db='posty',
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger()

TOKEN='#'
SITE_URL='#'

def start(bot, update):
    update.message.reply_text('Hello World!')

def hello(bot, update):
    update.message.reply_text('Hello {} {}'.format(
        update.message.from_user.first_name,
        emojize(':grinning_face:', use_aliases=True).encode('utf-8')))

def save(bot, update):
    text = update.message.text[6:]

    if len(text) < 5:
        response = 'The post-it is too short {}'.format(
            emojize(':disappointed:', use_aliases=True).encode('utf-8'))
    elif len(text) > 200:
        response = 'The post-it is too big {}'.format(
            emojize(':astonished:', use_aliases=True).encode('utf-8'))
    else:
        chat_id = update.message.chat.id
        if quantity_of_post_its_for(chat_id) < 10:
            save_post_it(chat_id, text)
            response = 'Post-it saved! {}'.format(
                emojize(':grinning:', use_aliases=True).encode('utf-8'))
        else:
            response = 'You have already 10 post-its. Sorry, I can not add \
                        more post-its {}'.format(
                emojize(':cry:', use_aliases=True).encode('utf-8'))

    update.message.reply_text(response)

def save_post_it(chat_id, text):
    connection = openConnection()
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO `posty`.`post_its` (`chat_id`, `text`) VALUES (%s, %s);"
            cursor.execute(sql, (chat_id, text))

        connection.commit()
    finally:
        connection.close()

def quantity_of_post_its_for(chat_id):
    quantity = 0
    connection = openConnection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT count(*) as quantity FROM `posty`.`post_its` WHERE chat_id = %s;"
            cursor.execute(sql, (chat_id))
            quantity = cursor.fetchone()['quantity']
    finally:
        connection.close()

    return quantity

def all(bot, update):
    keyboard = []
    chat_id  = update.message.chat.id
    post_its = get_first_five(chat_id)

    for post_it in post_its:
        keyboard.append([InlineKeyboardButton(
            '[{}] {}'.format(post_it['id'],
                             post_it['text'][:40].encode('utf-8')),
            callback_data='/show {}'.format(post_it['id'])
        )])

    if (quantity_of_post_its_for(chat_id) > 5):
        keyboard.append([InlineKeyboardButton('Next 5 post-its',
                                              callback_data='last5')])

    update.message.reply_text('List of your Post-it',
            reply_markup=InlineKeyboardMarkup(keyboard))

def get_first_five(chat_id):
    connection = openConnection()
    post_its = []
    try:
        with connection.cursor() as cursor:
            sql = "SELECT `id`, `text` FROM `posty`.`post_its` WHERE `chat_id` = %s LIMIT 5;"
            cursor.execute(sql, (chat_id))
            post_its = cursor.fetchall()
    finally:
        connection.close()
    return post_its

def get_last_five(chat_id):
    connection = openConnection()
    post_its = []
    try:
        with connection.cursor() as cursor:
            sql = "SELECT `id`, `text` FROM `posty`.`post_its` WHERE `chat_id` = %s LIMIT 5 OFFSET 5;"
            cursor.execute(sql, (chat_id))
            post_its = cursor.fetchall()
    finally:
        connection.close()
    return post_its

def callback_handler(bot, update):
    query   = update.callback_query
    order   = query.data
    chat_id = query.message.chat.id

    if '/show' in order:
        post_it = find(chat_id, order[5:])

        query.message.reply_text(post_it['text'])
    elif 'last5' == order:
        keyboard = []
        post_its = get_last_five(chat_id)

        for post_it in post_its:
            keyboard.append([InlineKeyboardButton(
                '[{}] {}'.format(post_it['id'],
                                 post_it['text'][:40].encode('utf-8')),
                callback_data='/show {}'.format(post_it['id'])
            )])

        keyboard.append([InlineKeyboardButton('First 5 post-its',
                                              callback_data='first5')])

        bot.editMessageText(text=query.message.text,
                            chat_id=chat_id,
                            message_id=query.message.message_id,
                            reply_markup=InlineKeyboardMarkup(keyboard))
    elif 'first5' == order:
        keyboard = []
        post_its = get_first_five(chat_id)

        for post_it in post_its:
            keyboard.append([InlineKeyboardButton(
                '[{}] {}'.format(post_it['id'], post_it['text'][:40].encode('utf-8')),
                callback_data='/show {}'.format(post_it['id'])
            )])

        if (quantity_of_post_its_for(chat_id) > 5):
            keyboard.append([InlineKeyboardButton(
                'Next 5 post-its', callback_data='last5'
            )])

        bot.editMessageText(text=query.message.text,
                            chat_id=chat_id,
                            message_id=query.message.message_id,
                            reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        query.message.reply_text('Wrong post it!')

def find(chat_id, post_it_id):
    connection = openConnection()
    post_it = None
    try:
        with connection.cursor() as cursor:
            sql = "SELECT `text` FROM `posty`.`post_its` WHERE `chat_id` = %s AND `id` = %s;"
            cursor.execute(sql, (chat_id, post_it_id))
            post_it = cursor.fetchone()
    finally:
        connection.close()
    return post_it

updater = Updater(TOKEN)

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('hello', hello))
updater.dispatcher.add_handler(CommandHandler('save', save))
updater.dispatcher.add_handler(CommandHandler('all', all))
updater.dispatcher.add_handler(CallbackQueryHandler(callback_handler))
updater.bot.setWebhook(SITE_URL)
updater.start_webhook()
updater.idle()
