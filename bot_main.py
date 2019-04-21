import os
from sys import executable
from backend import Map

import json
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, Filters, ConversationHandler
from telegram import ReplyKeyboardRemove
from telegram import ReplyKeyboardMarkup

hello_keyboard = [['Регистрация'], ['Вход']] 
map_keyboard = [['Схема'], ['Спутник'], ['Гибрид']]
markup_hello = ReplyKeyboardMarkup(hello_keyboard, one_time_keyboard=True)
markup_map = ReplyKeyboardMarkup(map_keyboard, one_time_keyboard=True)

mapa = Map()

new_b = {"name": '', "adress": ''}

filename = 'ac.txt'

data = open(filename, mode='r', encoding='UTF-8')
file = json.load(data)
data.close()

profile = None
adress = None

TOKEN = "804539138:AAFSP6jBGFWKPNev5npFOSfjUpnJFpERfXM"


def setup_proxy_and_start(token, proxy=True):
    address = "aws.komarov.ml"
    port = 1080
    username = "yandexlyceum"
    password = "yandex"
    try:
        updater = Updater(token, request_kwargs={'proxy_url': f'socks5://{address}:{port}/',
                                                 'urllib3_proxy_kwargs': {'username': username,
                                                                          'password': password}} if proxy else None)
        print('Proxy - OK!')
        main(updater)
    except RuntimeError:
        sleep(1)
        print('PySocks не установлен!')
        os.system(f'{executable} -m pip install pysocks --user')
        print('\nЗавистимости установлены!\nПерезапустите бота!')
        exit(0)
        
        
def first_response_reg(bot, update): #Первый этап регистрации
    global new_b
    login = update.message.text 
    for i in range(len(file)):
        if file[i]["name"] == login:
            update.message.reply_text("Ввведите другой никнейм, так как этот уже есть в нашей системе")
            return 1
    new_b["name"] = login
    update.message.reply_text("Введите город, в котором вы проживаете")
    return 3


def second_response_reg(bot, update):   #второй этап регистрации
    global new_b
    global profile
    global adress
    new_b["adress"] = update.message.text
    data = open(filename, mode='w', encoding='UTF-8')
    file.append(new_b)
    json.dump(file, data)
    data.close() 
    profile = file[-1]["name"]
    adress = file[-1]["adress"]
    new_b = {"name": '', "adress": ''}
    update.message.reply_text("Поздравляю, вы создали нового пользователя!\nЧтобы узнать команды для бота, напишите /help.")
    return ConversationHandler.END


def log(bot, update):
    global profile
    global adress    
    login = update.message.text
    for i in range(len(file)):
        if file[i]["name"] == login:
            profile = file[i]["name"]
            adress = file[i]["adress"]
            break
    update.message.reply_text("Поздравляю, вы снова с нами!\nЧтобы узнать команды для бота, напишите /help.")
    return ConversationHandler.END


def cinema(bot, update):    #Выдает список кинотеатров города, посредстов поиска в google
    global profile
    global adress  
    if adress == None:
        update.message.reply_text("Ввойдите, в систему, чтобы воспользоваться этой командой")
    else:
        update.message.reply_text("Поиск по всем кинотеатрам вашего города:\nhttps://www.google.com/search?q=Кинотеатры+{}&oq=Кинотеатры+{}&aqs=chrome..69i57j0l5.3288j0j7&sourceid=chrome&ie=UTF-8".format(adress, adress))
        
        
        
def park(bot, update):    #Выдает список парков города, посредстов поиска в google
    global profile
    global adress    
    if adress == None:
        update.message.reply_text("Ввойдите, в систему, чтобы воспользоваться этой командой")
    else:
        update.message.reply_text("Поиск по всем паркам вашего города:\nhttps://www.google.com/search?q=парки+{}&oq=парки+{}&aqs=chrome..69i57j0l5.3288j0j7&sourceid=chrome&ie=UTF-8".format(adress, adress))
        
        
def school(bot, update):    #Выдает список школ и учебных заведений города, посредстов поиска в google
    global profile
    global adress    
    if adress == None:
        update.message.reply_text("Ввойдите, в систему, чтобы воспользоваться этой командой")
    else:
        update.message.reply_text("Поиск по всем школам и учебным заведениям вашего города:\nhttps://www.google.com/search?q=школы+и+учебные+заведения+{}&oq=школы+и+учебные+заведения+{}&aqs=chrome..69i57j0l5.3288j0j7&sourceid=chrome&ie=UTF-8".format(adress, adress))
        
        
def maps(bot, update):    #Выдает карту города города, запросив вид карты (схема, спутник, гибрид)
    global adress    
    if adress == None:
        update.message.reply_text("Ввойдите, в систему, чтобы воспользоваться этой командой")
        return ConversationHandler.END
    else:
        update.message.reply_text("Выберите вид карты", reply_markup=markup_map)
        return 1


def kind(bot, update):
    global profile
    global adress    
    kin = update.message.text
    if kin == "Схема":
        mapa.setMode('map')
        topo = mapa.getObject(adress)
        mapa.setCenter(topo.getCoords())
        mapa.render()
        photo_loader(mapa.render())
    elif kin == "Спутник":
        mapa.setMode('sat')
        topo = mapa.getObject(adress)
        mapa.setCenter(topo.getCoords())
        mapa.render()
        photo_loader(mapa.render())        
    elif kin == "Гибрид":
        mapa.setMode('hyb')
        topo = mapa.getObject(adress)
        mapa.setCenter(topo.getCoords())
        mapa.render()
        photo_loader(mapa.render())        
    else:
        update.message.reply_text("Выберите вид карты", reply_markup=markup_map)
        return 1


def photo_loader(bot, updater, mapi):
    bot.sendPhoto(updater.message.chat.id, mapi)


def stop_map(bot, update):
    update.message.reply_text(
        "вы прервали выбор вида карты", ReplyKeyboardRemove())
    update.message.text("Чтобы узнать команды для ботма, напишите /help")
    return ConversationHandler.END


def stop_start(bot, update):    #останавливает регистрацию или вход
    update.message.reply_text(
        "Вы прервали создание аккаунта или вход в него.\nЧтобы начать заново, напишите команду /start", ReplyKeyboardRemove())
    return ConversationHandler.END  # Константа, означающая конец диалога.    


def start(bot, update):    #Выдает список кинотеатров города, посредстов поиска в google
    update.message.reply_text("Приветствую!\nЯ буду вашим личным ботом-справочником.")
    update.message.reply_text("Войдите в систему или зарегестрируйтесь, если вы с нами в перый раз!", 
                              reply_markup=markup_hello) 
    return 1


def check(bot, update):    #Выдает список кинотеатров города, посредстов поиска в google
    if update.message.text == "Регистрация":
        update.message.reply_text("Введите свой будущий никнейм")
        return 2
    elif update.message.text == "Вход":
        update.message.reply_text("Введите свой никнейм, чтобы войти в систему")
        return 4
    

def log_out(bot, update):
    global profile
    global adress  
    profile = None
    adress = None
    update.message.reply_text("Вы вышли из системы")
    

def help(bot, update):
    update.message.reply_text("Вот команды, доступные на этом боте")
    update.message.reply_text("/help - вывод списка доступных комманд\n/log_out - выход из системы\n/cinema - бот скидывает ссылку на поиск кинотеатров вашего города в google\n/park - бот скидывает ссылку на поиск парков вашего города в google\n/school - бот скидывает ссылку на поиск школ и учебных заведений вашего города в google")
    update.message.reply_text("Планировалась команда /map, которая спрашивала у пользователя тип карты и скидывала фото города с, выбранным пользователем, типом, но создатель оказался человеком с руками из одного места, так что, возможно, как-то потом будет\n¯\_(ツ)_/¯")
def main(updater):    #основная функция бота
    dp = updater.dispatcher
    start_conv = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points = [CommandHandler('start', start)],  
        
        # Состояние внутри диалога. Вариант с двумя обработчиками, фильтрующими текстовые сообщения.
        states={  
            # Функция читает ответ на первый вопрос и задаёт второй.
            1: [MessageHandler(Filters.text, check)],
            # Функция читает ответ на второй вопрос и завершает диалог.
            2: [MessageHandler(Filters.text, first_response_reg)],
            3: [MessageHandler(Filters.text, second_response_reg)],
            4: [MessageHandler(Filters.text, log)]
        },
        
        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks = [CommandHandler('stop', stop_start)]
    )  
    
    map_conv = ConversationHandler(
        entry_points = [CommandHandler('map', maps)], 
        states={ 
            1: [MessageHandler(Filters.text, kind)]
        },
        fallbacks = [CommandHandler('stop', stop_map)]
        )  
    dp.add_handler(map_conv)
    dp.add_handler(start_conv)
    dp.add_handler(CommandHandler("log_out", log_out))
    dp.add_handler(CommandHandler("cinema", cinema))
    dp.add_handler(CommandHandler("park", park))
    dp.add_handler(CommandHandler("school", school))
    dp.add_handler(CommandHandler("help", help))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    setup_proxy_and_start(token=TOKEN, proxy=True)