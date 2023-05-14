#-*- coding: utf8 -*-

# CounterBot 
# https://github.com/mrcheateugene/counterbot

import asyncio,threading,time,json,os,requests,hashlib,sys,a2s,inspect,random,logging,telebot
from datetime import *
from time import strftime,gmtime
from telebot import types
configFile = open("./config.json","r")
config = json.loads(configFile.readline())
configFile.close()
botdirectory  = config['directory']
srv_addr = tuple(config['addr'])
botUserName = config['bot']
chatID = config['chatid']
API_TOKEN_FILE = open(botdirectory+"token.txt","r")
API_TOKEN = API_TOKEN_FILE.read()
API_TOKEN_FILE.close()
bot = telebot.TeleBot(API_TOKEN, threaded=True)
fileUsers = open(botdirectory+"usersDB.json",'r+')
users = json.loads(fileUsers.read())
fileMsgs = open(botdirectory+"messages.json",'r', encoding="utf-8")
messages = json.load(fileMsgs)
fileMapsNotifications = open(botdirectory+"notifications.json",'r+', encoding="utf-8")
MNS = json.load(fileMapsNotifications)
fileLangPacket = open(botdirectory+"langPacket.json",'r', encoding="utf-8")
LN = json.load(fileLangPacket)
fileCommands = open(botdirectory+"commands.json","r", encoding="utf-8")
commands = json.load(fileCommands)
commandList = list(commands.keys())
cmdList_inline = None

def reloadmaps():
    global maps
    global fileMaps
    fileMaps = open(botdirectory+"maps.json","r", encoding="utf-8")
    maps = json.load(fileMaps)
    fileMaps.close()

reloadmaps()

def getById(uid):
    return bot.get_chat_member(chatID,int(uid)).user

def getuname(user):
    if user.username == None:
        try:
            return '<a href="tg://user?id='+user.id+'"'+user.full_name+'</a>'
        except:
            return "Неизвестен"
    return '@'+user.username

def getFlooders():
    flooders = []
    for flooder in users:
        flooderName = flooder
        flooder = users[flooder]
        if 'messages' in flooder:
            flooders.append([int(flooder['messages']),flooderName])
    pass
    flooders.sort(reverse=True)
    flooderDict = {}
    for flooder in flooders:
        flooderDict[flooder[1]] = flooder[0]
        pass
    return (flooderDict)

def top10Flooders():
    key = 1
    toReturnSTR = "<b>"+LN['topFlooders']+":</b>\n"
    flooders = getFlooders()
    for flooder in flooders:
        flooderKey="flooder"+str(key)
        username = getuname(getById(flooder))
        uid = getById(flooder).id
        toReturnSTR+=LN[flooderKey]+'<b><b>'+str(username)+"</b></b> ("+str(flooders[flooder])+")\n"
        print(key) 
        key+=1
        if key == 11:
            return toReturnSTR
        pass
    return toReturnSTR
def top10Flooders_msg(message):
    bot.reply_to(message,top10Flooders(),parse_mode="html")

def isSimplifiedCommand(message):
    if message.text.startswith("/") and message.text.replace("/","").replace(botUserName,"").replace(" ","") in maps:
        return True
    else:
        return False

def getSimplifiedCommand(message):
    if isSimplifiedCommand(message) == True:
        return message.text.replace("/","").replace(botUserName,"").replace(" ","").replace("_2x2","")
    else:
        return ""

def processSimplifiedCommand(message):
    command = getSimplifiedCommand(message)
    print(command)
    if getSimplifiedCommand != "":
        message.from_user.id = str(message.from_user.id)
        isSubbedMap = isSubbed(message.from_user.id,command)
        if isSubbedMap == True:
            unsubFromMap(message.from_user.id,command)
            bot.reply_to(message,LN['successUnsub']+" <b>"+str(command)+"</b>. "+LN['youWontBeNotified']+".",parse_mode="html")                        
        elif isSubbedMap == False:
            subtomap = subToMap(message.from_user.id,command)
            if(subtomap == True):
                bot.reply_to(message,LN['successSub']+" <b>"+str(command)+"</b>. "+LN['youWillBeNotified'],parse_mode="html")        
            else:
                #print(command)
                error = LN['unknownError']
                if not (command in maps and command in MNS):
                    error = LN['mapNotExists']
                elif(command in MNS and message.from_user.id in MNS[command]):
                    error = LN['alreadySubbed']
                bot.reply_to(message,LN['errorSub']+" "+error,parse_mode="html")   
        else:
            print("map not exists")
def notifyAboutMap(info):
    srvmap = info['map']
    print("srvmap in mns srvmap in maps")
    print(srvmap in MNS)
    print(srvmap in maps)
    if((srvmap in maps and srvmap in MNS)== True):
        toReturnSTR = LN['onserver']+" <b>"+srvmap+"</b>!\n\n"
        for usersubbed in MNS[srvmap]:
            usersubbed = getById(str(usersubbed))
            if hasattr(usersubbed,'username') == True:
                usersubbed = '@'+usersubbed.username
            else:
                usersubbed = '<a href="tg://user?id='+str(usersubbed.id)+'"'+usersubbed.full_name+"</a>"
            toReturnSTR+=usersubbed+","
            pass
        if(toReturnSTR==LN['onserver']+" <b>"+srvmap+"</b>!\n\n"):
            return False
        toReturnSTR+=" "+LN['joinMap']+"!"
        return toReturnSTR
    else:
        return False
thismodule = sys.modules[__name__]
def sendNotification(info):
    notifyAboutMapR = notifyAboutMap(info)
    if(notifyAboutMapR != False):
        bot.send_message(text=notifyAboutMapR,chat_id = chatID,parse_mode="html")


# bot.download_file(bot.get_file(message.photo[-1].file_id).file_path)
def info():
    return LN['botInfo']

def escapeStr(message):
    return message.replace("<","").replace(">","").replace("&","")

def isSubbed(user,maptosub):
    if not maptosub in maps:
        return "NE" # not exists
    else:
        if not maptosub in maps:
            return "NE" # not exists
        if not maptosub in MNS:
            return False
        elif(maptosub in MNS and user in MNS[maptosub]):
            return True
        else:
            return False

def subToMap(user,mapToSub):
    user = str(user)
    if(isSubbed(user,mapToSub) == True):
        print("precheck fail")
        return False
    if(mapToSub in maps or mapToSub.replace("_2x2","") in maps):
        if(mapToSub in maps or mapToSub.replace("_2x2","") in MNS):
            if not mapToSub in MNS:
                if mapToSub in maps:
                    MNS[mapToSub] = []
                    updateMNS(fileMapsNotifications,MNS)
            if True:
                MNS[mapToSub] = []
                updateMNS(fileMapsNotifications,MNS)
                if(user not in MNS[mapToSub]):
                    if not (mapToSub in MNS.keys()):
                        MNS[mapToSub]=[user]
                    else:
                        MNS[mapToSub].append(user)
                    if not (mapToSub+"_2x2" in MNS.keys()):
                        MNS[mapToSub+"_2x2"]=[user]
                    else:
                        MNS[mapToSub+"_2x2"].append(user)
                    updateMNS(fileMapsNotifications,MNS)
                    return True
            else:
                 return False
        else:
            MNS[mapToSub] = [user]
            updateMNS(fileMapsNotifications,MNS)
            return True
        updateMNS(fileMapsNotifications,MNS)
    else:
        return False

def unsubFromMap(user,mapToUnsub):
    user = str(user)
    if not mapToUnsub in MNS:
        if mapToUnsub in maps:
            MNS[mapToUnsub] = []
            updateMNS(fileMapsNotifications,MNS)
    if(mapToUnsub in MNS and isSubbed(user,mapToUnsub) and user in MNS[mapToUnsub]):
        print("Unsub 1")
        MNS[mapToUnsub].remove(user)
        updateMNS(fileMapsNotifications,MNS)
    if(mapToUnsub+"_2x2" in MNS and isSubbed(user,mapToUnsub+"_2x2") and user in MNS[mapToUnsub+"_2x2"]):
        print("Unsub 2")
        MNS[mapToUnsub+"_2x2"].remove(user)
        updateMNS(fileMapsNotifications,MNS)
    if(mapToUnsub.replace("_2x2","") in MNS and isSubbed(user,mapToUnsub.replace("_2x2","")) and user in MNS[mapToUnsub.replace("_2x2","")]):
        print("Unsub 3")
        MNS[mapToUnsub.replace("_2x2","")].remove(user)
        updateMNS(fileMapsNotifications,MNS)
    #else:
        #return "not_subscribed"
    return True
def getMap():
    try:
        info = a2s.info(srv_addr)
        players = a2s.players(srv_addr)
        return {"info":info,"players":players,"map":info.map_name}
    except Exception as e:
        print("exception")
        print(e)
        return "null"
def serverInfo():
    print(srv_addr)
    try:
        if(True):
            res = getMap()
            info = res['info']
            players = res['players']
            #toReturnSTR = "На сервере онлайн: "+str(players['player_count'])+" игроков.\nТекущая карта: "+str(info['map'])+"\nИгра: "+info['game']+"\nИгроки онлайн:\n"
            toReturnSTR = "🔫 "+LN['headerServInfo']+" (<code>"+str(srv_addr[0])+":"+str(srv_addr[1])+"</code>)\n\n\
🗺 <b>"+LN['srvinfo_map']+"</b>: "+escapeStr(str(info.map_name))+"\n\
👥 <b>"+LN['srvinfo_online']+"</b>: "+escapeStr(str(info.player_count))+"/"+escapeStr(str(info.max_players))+"\n\n\
<b>"+LN['srvinfo_players']+"</b>:\n"
            for player in players:
                if player.name:
                    toReturnSTR+= "👤 <strong>"+escapeStr(player.name)+"</strong> ("+LN['srvinfo_score']+": "+escapeStr(str(player.score))+", "+LN['srvinfo_time']+": "+escapeStr(str(strftime("%H:%M:%S", gmtime(player.duration))))+")\n"
            if(int(info.player_count) == 0):
                toReturnSTR+=LN['srvinfo_noPlayers']+"\n"
            return toReturnSTR
    except Exception as e:
        print(e)
        return LN['srvinfo_exception']
def updateMNS(MNSFile,MNSItself):
    MNSFile.close()
    os.remove(botdirectory+"notifications.json")
    os.mknod(botdirectory+"notifications.json")
    MNSFile = open(botdirectory+"notifications.json",'r+')
    MNSFile.write(json.dumps(MNSItself))
    MNSFile.close()
    MNSFile = open(botdirectory+"notifications.json",'r+')
    MNS = json.loads(MNSFile.read())
    return 0

def foolOfDay():
    return LN['freakOfDay']+' - '+open(botdirectory+"foolOfDay",'r').readline()+". "+LN['congratsDay']

def pairOfDay():
    print("pOd called")
    print(open(botdirectory+"pairOfDay",'r').readline())
    return LN['pairOfDay']+' - '+(open(botdirectory+"pairOfDay",'r').readline()).replace("{ANDSIGN}","и")+". "+LN['congratsThem']

def nicestOfDay():
    return LN['nicestOfDay']+' - '+open(botdirectory+"nicestOfDay",'r').readline()+". "+LN['congratsDay']

def getCmdList_inline(inline_query):
    global cmdList_inline
    #if isinstance(cmdList_inline,list):
#        return cmdList_inline
    #else:
    if True:
        cmdList = []
        key = 0
        for command in commands:
            command =  command.replace(' ','').strip()
            commandFunName = commands[command][1].replace(' ','').strip()
            commandFUN = globals()[commandFunName]
            if len(list(inspect.signature(commandFUN).parameters)) == 1 and list(inspect.signature(commandFUN).parameters)[0] == 'username' :
                cmd = types.InlineQueryResultArticle(str(int(inline_query.id)+random.randint(0,999)), command, types.InputTextMessageContent(message_text = commandFUN(inline_query.from_user.id),parse_mode="html"), description = (commands[command])[0])
                cmdList.append(cmd)
            elif(len(list(inspect.signature(commandFUN).parameters)) == 0):
                cmd = types.InlineQueryResultArticle(str(int(inline_query.id)+random.randint(0,999)), command, types.InputTextMessageContent(message_text = commandFUN(),parse_mode="html"), description = (commands[command])[0])
                cmdList.append(cmd)
            key+=1
            pass
        cmdList_inline = cmdList
        return cmdList
def getStats(username):
    username = str(username)
    if(username in users and isinstance(users[username],dict) ):
        updateUsers(fileUsers,users)
        if not('symbols' in users[username]):
            symbols = 0
        else:
            symbols = users[username]['symbols']
        if not('messages' in users[username]):
            messages = 0
        else:
            messages = users[username]['messages']
        if not('photosAmount' in users[username]):
            photosAmount = 0
        else:
            photosAmount = users[username]['photosAmount']
        if not('videos' in users[username]):
            videos = 0
        else:
            videos = users[username]['videos']
        if not('stickers' in users[username]):
            stickers = 0
        else:
            stickers = users[username]['stickers']
        if not('voice' in users[username]):
            voice = 0
        else:
            voice = users[username]['voice']
        if not('audio' in users[username]):
            audio = 0
        else:
            audio = users[username]['audio']
        usrname =getuname(getById(username))
        return "<b>"+LN['statsName']+" "+usrname+"</b>: \n"+LN['wroteSymbols']+': '+str(symbols)+'\n'+LN['wroteMessages']+': '+str(messages)+'\n'+LN['sentImages']+': '+str(photosAmount)+'\n'+LN['sentVideos']+': '+str(videos)+'\n'+LN['sentStickers']+': '+str(stickers)+'\n'+LN['sentVoice']+': '+str(voice)+'\n'+LN['sentAudio']+': '+str(audio)
    else:
        return LN['statsUnavailable']

def updateUsers(fileUsers,users):
    #print(users)
    fileUsers.close()
    os.remove(botdirectory+"usersDB.json")
    os.mknod(botdirectory+"usersDB.json")
    fileUsers = open(botdirectory+"usersDB.json",'r+')
    fileUsers.write(json.dumps(users))
    fileUsers.close()
    fileUsers = open(botdirectory+"usersDB.json",'r+')
    users = json.loads(fileUsers.read())
    return 0

def size(username):
    username = str(username)
    updateUsers(fileUsers,users)
    userinfo = users.get(username)
    size = ""
    numSize=0
    isMale =1
    if isinstance(userinfo,dict) == False:
        users[username] = {}
        userinfo = {}
    if not 'isMale' in userinfo:
        isMale = random.randint(1,100)%2
    else:
        isMale = userinfo['isMale']
    if not 'numSize' in userinfo:
        if(isMale==1):
            numSize=random.randint(3,35)
        else:
            numSize=random.randint(10, 30)
    else:
        numSize = userinfo['numSize']
    users[username]['isMale'] = isMale
    users[username]['numSize'] = numSize
    updateUsers(fileUsers,users)
    if(isMale == 1):
        size+=LN['dickLength']+" "
    else:
        size=size+LN['vaginaDepth']+" "
    pass
    size+=str(numSize)
    if(isMale == 0 and numSize < 13):
        size+=' 👍'
    elif(isMale == 0 and numSize > 13):
        size+=' 😳'
    elif(isMale == 0 and numSize > 20):
        size+=' 🤯'
    elif(isMale == 1 and numSize > 30):
        size+=' 🤯'
    elif(isMale == 1 and numSize > 20):
        size+=' 👍😊'
    elif(isMale == 1 and numSize > 15):
        size+=' 👍'
    elif(isMale == 1 and numSize < 15):
        size+=' 😔'
    elif(isMale == 1 and numSize < 10):
        size+=' 😢'
    elif(isMale == 1 and numSize < 5):
        size+=' 😭😭😭😭😭'
    else:
        size+=' 👍'
    pass
    return LN['size_UserMention']+" "+getuname(getById(username))+" "+size+" "+LN['size_cm']+"!"
def listmaps(username):
    username = str(username)
    toReturnSTR = LN['subUnsubcommands']+": \n"
    if(True):
        showNot = True
        for mapCanSub in maps:
            if isSubbed(username,mapCanSub) != True:
                 if(showNot == True):
                     showNot = False
                 toReturnSTR+="▪️ /"+mapCanSub+"\n"
            else:
                if(showNot == True):
                    showNot = False
                toReturnSTR+="▪️ /"+mapCanSub+" "+LN['mapSubbedSign']+" \n"
            if(showNot):
                toReturnSTR+=LN['subUnsubcommands_none']
                showNot = True
            key =0
    return toReturnSTR
def dochoice(array):
    return array[random.randint(0,len(array)-1)]

def unsubFromMap_msg(message):
    args = message.text.split()
    if(len(args)>=2):
        args[1] = args[1].replace("_2x2","")
        if unsubFromMap(message.from_user.id,args[1]) == True:
            bot.reply_to(message,LN['successUnsub']+" <b>"+str(args[1])+"</b>. "+LN['youWontBeNotified']+".",parse_mode="html")                        
        else:
            mapToUnsub = args[1]
            error = LN['unknownError']
            if not(args[1] in maps and args[1] in MNS):
                error = LN['mapNotExists']
            elif isSubbed(uid,mapToUnsub) or isSubbed(uid,mapToUnsub+"_2x2") or isSubbed(uid,mapToUnsub.replace("_2x2","")) == False:
                error = LN['notsubbed']
            bot.reply_to(message,LN['errorUnsub']+". "+error,parse_mode="html")   
    else:
        bot.reply_to(message,LN['unsubCommandUsage'],parse_mode="html")
    return 0

def test(username):
    username = str(username)
    updateUsers(fileUsers,users)
    userinfo = users.get(username)
    lines = 0
    isMale = 1
    if isinstance(userinfo,dict) == False:
        users[username] = {}
        userinfo = {}
    if 'isMale' in userinfo:
        isMale = userinfo['isMale']
    else:
        isMale = random.randint(1,100)%2
    if 'test' in userinfo: 
        lines = userinfo['test']
    else:
        lines=int((random.randint(0, 3)+random.randint(0, 3)+random.randint(0, 3)+random.randint(0, 3)+random.randint(0, 3))/6)
    users[username]['isMale'] = isMale
    users[username]['test'] = lines
    updateUsers(fileUsers,users)
    linesMeaning= ""
    strLines = ""
    if(lines == 0):
        strLines=LN['lines0']
        linesMeaning = str(dochoice(messages["zero"])).replace("*ник*","@"+username)
    elif(lines == 1):
        strLines=LN['lines1']
        linesMeaning = str(dochoice(messages["one"])).replace("*ник*","@"+username)
    elif(lines == 2):
        strLines=LN['lines2or3']
        if(isMale == 1):
            hasCancer = LN['hasCancer']
            linesMeaning=hasCancer
        else:
            hasCancer = ""
            linesMeaning = str(dochoice(messages["two"])).replace("*ник*","@"+username)+" "+hasCancer
    elif(lines== 3):
        strLines=LN['lines2or3']
        linesMeaning = str(dochoice(messages["three"])).replace("*ник*","@"+username)
    escapedmsg = str(LN['size_UserMention']+" "+getuname(getById(username))+" "+str(lines)+" "+strLines+". "+linesMeaning)
    return escapedmsg

def listmaps_msg(message):
    bot.reply_to(message,listmaps(message.from_user.id),parse_mode="html")

def subToMap_msg(message):
    args = message.text.split()
    if(len(args)>=2):
        args[1] = args[1].replace("_2x2","")
        if subToMap(message.from_user.id,args[1]) == True:
            bot.reply_to(message,LN['successSub']+" <b>"+str(args[1])+"</b>. "+LN['youWillBeNotified'],parse_mode="html")        
        else:
            error = LN['unknownError']
            if not (args[1] in maps and args[1] in MNS):
                error = LN['mapNotExists']
            elif(args[1] in MNS and message.from_user.id in MNS[args[1]]):
                error = LN['alreadySubbed']
            bot.reply_to(message,LN['errorSub']+" "+error,parse_mode="html")   
    else:
        bot.reply_to(message,LN['subtomap_usage'],parse_mode="html")

times=0
mapToEmul = "none"
secondMap = "nonetwo"
def mapEmul():
    global times
    global mapToEmul
    global secondMap
    times+=1
    if times%2 == 1:
        return mapToEmul
    else:
        return secondMap
#print("** TEST**")
#print(mapEmul())
#print(mapEmul())
#print(mapEmul())
#print(mapEmul())
#print("** TEST DONE **")

prevmap = None
def mapChanged():
    global prevmap
    cmap = getMap()
    #cmap = {'map':mapEmul()}
    if(cmap == "null"):
        return False
    if prevmap == cmap['map']:
        return False
    elif(prevmap != cmap['map']):
        sendNotification(cmap)
        prevmap =cmap['map']
        return True
mapChanged()
def randomUser():
    return getById((random.choice(list(users.keys()))))
def updateDaily():
    updateUsers(fileUsers,users)
    pairOfDayONE = getuname(randomUser())
    pairOfDayTWO = getuname(randomUser())
    pairOfDay = pairOfDayONE+" {ANDSIGN} "+pairOfDayTWO
    nicestOfDay = getuname(randomUser())
    foolOfDay = getuname(randomUser())
    podfile = open(botdirectory+"pairOfDay","w+")
    podfile.write(pairOfDay)
    podfile.close()
    fodfile = open(botdirectory+"foolOfDay","w+")
    fodfile.write(foolOfDay)
    fodfile.close()
    nodfile = open(botdirectory+"nicestOfDay","w+")
    nodfile.write(nicestOfDay)
    nodfile.close()
    print("Updated daily")
def checkIfMidnight():
    now = datetime.now()
    now = "{:02d}:{:02d}".format(now.hour, now.minute)
    return now == "00:00"

def updateMaplist():
    try:
        lines = requests.get(config['maplistdl']).text.replace('\r\n','\n').split('\n')
        maps = []
        for line in lines:
            if line.startswith(";") or len(line.split("_"))==1:
                continue
            if line.replace("\r\n","") !="" and line.replace("\n","") != "":
                maps.append(line.replace("\n","").replace("\r","").replace(" ",""))
            else:
                print("sc")
        fileCommands = open(botdirectory+'maps.json','w+', encoding="utf-8")
        fileCommands.write(json.dumps(maps))
        fileCommands.close()
        print(maps)
        reloadmaps()
    except Exception as e:
        raise (e)
updateMaplist()
def timer(f_stop):
    updateMaplist()
    updateUsers(fileUsers,users)
    mapChanged()
    if(checkIfMidnight()):
        updateDaily()
    if not f_stop.is_set():
        threading.Timer(30, timer, [f_stop]).start()
@bot.message_handler(commands=commandList)
def message_handler(message):
    
    uid  = str(message.from_user.id)
    updateUsers(fileUsers,users)
    if(message.chat.id == chatID)==True:
        if((message.content_type == 'text' and message.text.startswith(message.text.split()[0]) or message.text.startswith(message.text.split()[0]+botUserName+""))):
            command = message.text.split()[0]
            command =  command.replace(' ','').strip().replace(botUserName,"").replace("/","")
            commandFunName = commands[command][1].replace(' ','').strip()
            if (commandFunName+"_msg" in globals()) == False and commandFunName in globals() == True:
                commandFUN = globals()[commandFunName]
            elif commandFunName+"_msg" in globals():
                commandFUN = globals()[commandFunName+"_msg"]
            elif commandFunName in globals():
                commandFUN = globals()[commandFunName]
            if commandFunName+"_msg" in globals() and len(list(inspect.signature(commandFUN).parameters)) == 0:                
                commandFUN = globals()[commandFunName+"_msg"]
                bot.reply_to(message,commandFUN(),parse_mode="html")
            elif commandFunName+"_msg" in globals() and len(list(inspect.signature(commandFUN).parameters)) == 1 and list(inspect.signature(commandFUN).parameters)[0] == 'message':
                commandFUN = globals()[commandFunName+"_msg"]
                commandFUN(message)
            elif commandFunName in globals() and len(list(inspect.signature(commandFUN).parameters)) == 1 and list(inspect.signature(commandFUN).parameters)[0] == 'username':
                commandFUN = globals()[commandFunName]
                bot.reply_to(message,commandFUN(message.from_user.id),parse_mode="html")
            elif commandFunName in globals() and len(list(inspect.signature(commandFUN).parameters)) == 0:
                commandFUN = globals()[commandFunName]
                bot.reply_to(message,commandFUN(),parse_mode="html")
    else:
        bot.reply_to(message,f"Этот бот предназначен для другого чата. {f'(Chat ID {message.chat.id})' if config['showChatId'] else '' }")
@bot.inline_handler(lambda query: len(query.query) == 0)
#@bot.inline_handler(lambda query: query.query == 'size')
def query_text(inline_query):
    updateUsers(fileUsers,users)
    cmdList = getCmdList_inline(inline_query)
    cmdList = getCmdList_inline(inline_query)
    bot.answer_inline_query(inline_query.id, cmdList, cache_time=1)
def default_query(inline_query):
    try:
         updateUsers(fileUsers,users)
         cmdList = getCmdList_inline(inline_query)
         cmdList = getCmdList_inline(inline_query)
         bot.answer_inline_query(inline_query.id, cmdList, cache_time=1)
    except Exception as e:
        print(e)
@bot.message_handler(content_types = ['new_chat_members', 'left_chat_member'])
def onJoinOnLeft(msg):
    print("ojonjeft")
    updateUsers(fileUsers,users)
    if msg.left_chat_member != None and type(msg.left_chat_member) == telebot.types.User:
        del users[str(msg. left_chat_member.id)]
        updateUsers(fileUsers,users)
    if msg.new_chat_members != None and type(msg.new_chat_members) == list:
        for member in msg.new_chat_members:
            if not str(member.id) in users:
                users[str(member.id)] = {}
        updateUsers(fileUsers,users)


@bot.message_handler(func=lambda message:True, content_types=['text'])
def onmessage(message):
    print("onmessage")
    #print(message.from_user.id)
    message.from_user.id = str(message.from_user.id)
    if (message.chat.id == chatID) and (isSimplifiedCommand(message) == True):
        print("simplified")
        processSimplifiedCommand(message)
    pass
    updateUsers(fileUsers,users)
    defaultuser(message)
    pass
    if('messages' in users[message.from_user.id]):
         users[message.from_user.id]['messages']+=1
    else:
         users[message.from_user.id]['messages']=1
    if('symbols' in users[message.from_user.id]):
         users[message.from_user.id]['symbols']+=len(message.text)
    else:
         users[message.from_user.id]['symbols']=len(message.text)
    updateUsers(fileUsers,users)

@bot.message_handler(func=lambda message: True,content_types =['photo'] )
def processPhotos(message):
    message.from_user.id = str(message.from_user.id)
    updateUsers(fileUsers,users)
    defaultuser(message)
    if('photosAmount' in users[message.from_user.id]):
         users[message.from_user.id]['photosAmount']+=1
    else:
         users[message.from_user.id]['photosAmount']=1
    updateUsers(fileUsers,users)

def defaultuser(message):
    global users
    if (message.from_user.id in users)==False or (message.from_user.id in users and isinstance(users[message.from_user.id],dict)) == False:
        users[message.from_user.id] = {}
        updateUsers(fileUsers,users)
@bot.message_handler(func=lambda message: True,content_types =['sticker'] )
def processStickers(message):
    message.from_user.id = str(message.from_user.id)
    updateUsers(fileUsers,users)
    defaultuser(message)
    if('stickers' in users[message.from_user.id]):
         users[message.from_user.id]['stickers']+=1
    else:
         users[message.from_user.id]['stickers']=1
    updateUsers(fileUsers,users)

@bot.message_handler(func=lambda message: True,content_types =['voice'] )
def processVoice(message):
    message.from_user.id = str(message.from_user.id)
    updateUsers(fileUsers,users)
    defaultuser(message)
    if('voice' in users[message.from_user.id]):
         users[message.from_user.id]['voice']+=1
    else:
         users[message.from_user.id]['voice']=1
    updateUsers(fileUsers,users)

@bot.message_handler(func=lambda message: True,content_types =['audio'] )
def processMusic(message):
    message.from_user.id = str(message.from_user.id)
    updateUsers(fileUsers,users)
    defaultuser(message)
    if('audio' in users[message.from_user.id]):
         users[message.from_user.id]['audio']+=1
    else:
         users[message.from_user.id]['audio']=1
    updateUsers(fileUsers,users)

@bot.message_handler(func=lambda message: True,content_types =['video','video_note'] )
def processVideos(message):
    message.from_user.id = str(message.from_user.id)
    updateUsers(fileUsers,users)
    defaultuser(message)
    if('videos' in users[message.from_user.id]):
         users[message.from_user.id]['videos']+=1
    else:
         users[message.from_user.id]['videos']=1
    updateUsers(fileUsers,users)

def main_loop():
    bot.infinity_polling()

if __name__ == '__main__':
    try:
        f_stop = threading.Event()
        timer(f_stop)
        main_loop()
    except KeyboardInterrupt:
        print('\nStopping.\n')
        sys.exit(0)
