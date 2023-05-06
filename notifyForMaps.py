#-*- coding: utf8 -*-
import a2s
srv_addr = ("188.35.185.185",27016)
from PIL import Image
from pytesseract import pytesseract
import schedule
import logging
import sys
import time,json,os
import datetime
import random
from time import strftime
from time import gmtime
import telebot
from telebot import types

#img = Image. open(path_to_image)
#text = pytesseract. image_to_string(img)
#print(text)
API_TOKEN_FILE = open("/test/vagina-agd-bot/token.txt","r")
API_TOKEN = API_TOKEN_FILE.read()
API_TOKEN_FILE.close()
chat_id = config['chat_id']
bot = telebot.TeleBot(API_TOKEN)
#telebot.logger.setLevel(logging.DEBUG)
fileUsers = open("/test/vagina-agd-bot/usersDB.json",'r+')
users = json.loads(fileUsers.read())
fileMsgs = open("/test/vagina-agd-bot/messages.json",'r', encoding="utf-8")
messages = json.load(fileMsgs)
fileMaps = open("/test/vagina-agd-bot/maps.json","r", encoding="utf-8")
maps = json.load(fileMaps)
fileMapsNotifications = open("/test/vagina-agd-bot/notifications.json",'r+', encoding="utf-8")
MNS = json.load(fileMapsNotifications)
os.system("screen -S agdebot -X quit")

def getMap():
    try:
        info = a2s.info(srv_addr)
        return str(info.map_name)
    except Exception as e:
        print(e)
        return "null"

def notifyAboutMap():
    srvmap = getMap()
    if((srvmap in maps or srvmap.replace("_2x2","") in maps) and (srvmap in MNS or srvmap.replace("_2x2","") in MNS)):
        toReturnSTR = "На сервере "+srvmap+"! "
        nobodySubbed = True
        is2b2 = False
        for usersubbed in MNS[srvmap.replace("_2x2","")]:
            if not is2b2:
                nobodySubbed = False
                pass
            toReturnSTR+="@"+usersubbed+","
            pass
        if(srvmap.endswith("2x2") ==True and srvmap in MNS):
            is2b2 = True
            for usersubbed in MNS[srvmap]:
                nobodySubbed = False
                toReturnSTR+="@"+usersubbed+","
            pass
        if not (nobodySubbed):
            toReturnSTR+="заходите! Хотите отписаться от карты? Пропиши \"<code>/unsubmap "+srvmap+"</code>\", и тебя больше не побеспокоит это уведомление."
            return toReturnSTR
        else:
            return False
    else:
        return False
def sendNotification():
    notifyAboutMapR = notifyAboutMap()
    if(notifyAboutMapR != False):
        bot.send_message(text=notifyAboutMapR,chat_id = -1001696718262,parse_mode="html")
sendNotification()
os.system("screen -dmS agdebot python3 /test/vagina-agd-bot/main.py")