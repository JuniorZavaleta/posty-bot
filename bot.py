#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler
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
    savePostIt(update.message.chat.id, text)

    update.message.reply_text('Post-it saved! ' + grinning_face)

def savePostIt(chat_id, text):
    connection = openConnection()
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO `posty`.`post_its` (`chat_id`, `text`) VALUES (%s, %s);"
            cursor.execute(sql, (chat_id, text))

        connection.commit()
    finally:
        connection.close()

def all(bot, update):
    response = ''
    post_its = getAllFromDb(update.message.chat.id)

    for post_it in post_its:
        response += '[{}] {}\n'.format(post_it['id'], post_it['text'][:40])

    update.message.reply_text('List of Post-it\n'+
                              '================\n'+
                              response,disable_web_page_preview=True)

def getAllFromDb(chat_id):
    connection = openConnection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT `id`, `text` FROM `posty`.`post_its` WHERE `chat_id` = %s;"
            cursor.execute(sql, (chat_id))
            return cursor.fetchall()
    finally:
        connection.close()

updater = Updater(TOKEN)

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('hello', hello))
updater.dispatcher.add_handler(CommandHandler('save', save))
updater.dispatcher.add_handler(CommandHandler('all', all))
updater.bot.setWebhook(SITE_URL)
updater.start_webhook()
updater.idle()
