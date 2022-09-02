# #! /usr/bin/env python3

import os
import telebot
from urllib.request import urlretrieve
import subprocess

API_KEY = os.getenv("API_KEY")
bot = telebot.TeleBot(API_KEY)
path = os.path.dirname(os.path.abspath(__file__))+"/upload/"


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, """Usage:
	1. Send the hash as a file and add what type of hash is as caption
	2. Wait for answer""")


def cracking(hashFile, crackingOption, dictionary):
    if os.listdir(path):
        result = subprocess.Popen(f'hashcat -m {crackingOption} -a 3 {hashFile} {dictionary} --quiet',
                                  shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        stdout, stderr = result.communicate()
        if not stderr:
            return stdout.decode('utf-8')
        else:
            return stderr.decode('utf-8')


@bot.message_handler(content_types=['document'])
def handle_docs(message):
    fileName = message.document.file_name
    fileID = message.document.file_id
    file_info = bot.get_file(fileID)
    urlretrieve(
        f'https://api.telegram.org/file/bot{API_KEY}/{file_info.file_path}', path+fileName)
    bot.reply_to(message, "Cracking...")
    message.caption.upper()
    if "WPA" in message.caption or "WPA2" in message.caption:
        bot.reply_to(message, cracking(path+fileName, "22000", "?d?d?d?d?d?d?d?d"))
    elif "NTLM" in message.caption:
        bot.reply_to(message, cracking(
            path+fileName, "1000", "?u?l?l?l?l?l?l?l?d"))
    os.remove(path+fileName)


bot.infinity_polling()
