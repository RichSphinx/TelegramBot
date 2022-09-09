# #! /usr/bin/env python3

from logging import shutdown
import os
import telebot
import telegram
from telebot import types
from urllib.request import urlretrieve
import subprocess

API_KEY = os.getenv("API_KEY")
bot = telebot.TeleBot(API_KEY)
path = os.path.dirname(os.path.abspath(__file__))+"/upload/"


markup = types.InlineKeyboardMarkup()
usrs = types.InlineKeyboardButton('Users', callback_data="Users")
passwd = types.InlineKeyboardButton('Passwords', callback_data="Passwords")
markup.add(usrs, passwd)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, """*Usage:*
    1. *Dictionaries:*
        1.1 To add a dictionary just send the
        dictionary with caption "*dict*"
	2. *Hash:*
        2.1 Send the hash as a file and add
        what type of hash is as caption
        (*WPA*, *WPA2*, *NTLM*)
        2.2 Eg. "WPA dictName.txt"
	3. Wait for answer""", parse_mode='Markdown')


def cracking(hashFile, crackingOption, dictionary):
    result = subprocess.Popen(f'hashcat -m {crackingOption} -a 3 {hashFile} {dictionary} --quiet',
                              shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    stdout, stderr = result.communicate()

    if not stderr:
        if not stdout:
            result = subprocess.Popen(f'hashcat -m {crackingOption} -a 3 {hashFile} --show',
                              shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            stdout, stderr = result.communicate()
            return "Hash already cracked!"+stdout.decode('utf-8')
        return stdout.decode('utf-8')
    else:
        return stderr.decode('utf-8')


@bot.message_handler(content_types=['document'])
def handle_docs(message):
    fileName = message.document.file_name
    fileID = message.document.file_id
    file_info = bot.get_file(fileID)
    if "DICT" in message.caption.upper() or "DICTIONARY" in message.caption.upper():
        urlretrieve(
            f'https://api.telegram.org/file/bot{API_KEY}/{file_info.file_path}', path+'/dicts/'+fileName)
        bot.reply_to(message, "Dictionary Saved")
    else:
        urlretrieve(
            f'https://api.telegram.org/file/bot{API_KEY}/{file_info.file_path}', path+'hashes/'+fileName)
        hashType, dictName = message.caption.split(" ")
        if "WPA" in hashType.upper().strip() or "WPA2" in hashType.upper().strip():
            bot.reply_to(message, "Cracking...")
            bot.reply_to(message, cracking(path+'hashes/' +
                         fileName, "22000", path+'dicts/'+dictName))
        elif "NTLM" in hashType.upper().strip():
            bot.reply_to(message, "Cracking...")
            bot.reply_to(message, cracking(
                path+'hashes/'+fileName, "1000", path+'dicts/'+dictName))


bot.infinity_polling()
