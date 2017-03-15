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
    update.message.reply_text('Hello ' + update.message.from_user.first_name + emojize(':grinning_face:', use_aliases=True))

def save(bot, update):
    text = update.message.text[6:]
    grinning_face = emojize(':grinning_face:', use_aliases=True)

    if len(text) < 5:
        response = 'The post-it is too short {}'.format(emojize(':disappointed:', use_aliases=True).encode('utf-8'))
    elif len(text) > 200:
        response = 'The post-it is too big {}'.format(emojize(':astonished:', use_aliases=True).encode('utf-8'))
    else:
        chat_id = update.message.chat.id
        if (quantityOfPostItsFor(chat_id) < 10):
            savePostIt(chat_id, text)
            response = 'Post-it saved! {}'.format(emojize(':grinning:', use_aliases=True).encode('utf-8'))
        else:
            response = 'You have 10 post-its. Sorry, I can not add more post-its {}'.format(emojize(':cry:', use_aliases=True).encode('utf-8'))

    update.message.reply_text(response)

def savePostIt(chat_id, text):
    connection = openConnection()
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO `posty`.`post_its` (`chat_id`, `text`) VALUES (%s, %s);"
            cursor.execute(sql, (chat_id, text))

        connection.commit()
    finally:
        connection.close()

def quantityOfPostItsFor(chat_id):
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
    post_its = getAllFromDb(update.message.chat.id)

    for post_it in post_its:
        keyboard.append([InlineKeyboardButton(
            '[{}] {}'.format(post_it['id'], post_it['text'][:40].encode('utf-8')),
            callback_data='/show {}'.format(post_it['id'])
        )])

    update.message.reply_text('List of your Post-it',
            reply_markup=InlineKeyboardMarkup(keyboard), one_time_keyboard=True)

def getAllFromDb(chat_id):
    connection = openConnection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT `id`, `text` FROM `posty`.`post_its` WHERE `chat_id` = %s;"
            cursor.execute(sql, (chat_id))
            return cursor.fetchall()
    finally:
        connection.close()

def show(bot, update):
    order = update.callback_query.data
    if '/show' in order:
        post_it = findFromDb(update.callback_query.message.chat.id, order[5:])

        update.callback_query.message.reply_text(post_it['text'])
    else:
        update.callback_query.message.reply_text('Wrong post it!')

def findFromDb(chat_id, post_it_id):
    connection = openConnection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT `text` FROM `posty`.`post_its` WHERE `chat_id` = %s AND `id` = %s;"
            cursor.execute(sql, (chat_id, post_it_id))
            return cursor.fetchone()
    finally:
        connection.close()

updater = Updater(TOKEN)

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('hello', hello))
updater.dispatcher.add_handler(CommandHandler('save', save))
updater.dispatcher.add_handler(CommandHandler('all', all))
updater.dispatcher.add_handler(CallbackQueryHandler(show))
updater.bot.setWebhook(SITE_URL)
updater.start_webhook()
updater.idle()
