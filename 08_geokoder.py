import os
from sys import executable

import json
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import requests
import json

TOKEN = "804539138:AAFSP6jBGFWKPNev5npFOSfjUpnJFpERfXM"


def setup_proxy_and_start(token, proxy=True):
    # Указываем настройки прокси (socks5)
    address = "aws.komarov.ml"
    port = 1080
    username = "yandexlyceum"
    password = "yandex"

    # Создаем объект updater. В случае отсутствия пакета PySocks установим его
    try:

        updater = Updater(token, request_kwargs={'proxy_url': f'socks5://{address}:{port}/',
                                                 'urllib3_proxy_kwargs': {'username': username,
                                                                          'password': password}} if proxy else None)
        print('Proxy - OK!')

        # Запускаем бота
        main(updater)
    except RuntimeError:
        print('PySocks не установлен!')
        os.system(f'{executable} -m pip install pysocks --user')  # pip.main() не работает в pip 10.0.1

        print('\nЗавистимости установлены!\nПерезапустите бота!')
        exit(0)


def start(bot, update):
    update.message.reply_text("Я бот-геокодер. Ищу объекты на карте.")


# Получаем параметры объекта для рисования карты вокруг него.
def get_ll_spn(toponym):
    # Координаты центра топонима:
    toponym_coodrinates = toponym["Point"]["pos"]
    # Долгота и Широта :
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

    # Собираем координаты в параметр ll
    ll = ",".join([toponym_longitude, toponym_lattitude])

    # Рамка вокруг объекта:
    envelope = toponym["boundedBy"]["Envelope"]

    # левая, нижняя, правая и верхняя границы из координат углов:
    l,b = envelope["lowerCorner"].split(" ")
    r,t = envelope["upperCorner"].split(" ")
  
    # Вычисляем полуразмеры по вертикали и горизонтали
    dx = abs(float(l) - float(r)) / 2.0
    dy = abs(float(t) - float(b)) / 2.0

    # Собираем размеры в параметр span
    span = "{dx},{dy}".format(**locals())

    return (ll, span)

def geocoder(bot, updater):
    geocoder_uri = geocoder_request_template = "http://geocode-maps.yandex.ru/1.x/"
    response = requests.get(geocoder_uri, params = {
        "format": "json",
        "geocode": updater.message.text
    })


    toponym = response.json()["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    
   
    ll, spn = get_ll_spn(toponym)  
    # Можно воспользоваться готовой фукнцией,
    # которую предлагалось сделать на уроках, посвященных HTTP-геокодеру.

    static_api_request = "http://static-maps.yandex.ru/1.x/?ll={ll}&spn={spn}&l=sat".format(**locals())

    bot.sendPhoto(
        updater.message.chat.id,  # Идентификатор чата. Куда посылать картинку.
        # Ссылка на static API по сути является ссылкой на картинку.
        static_api_request
    )                             
    # Телеграму можно передать прямо ее, не скачивая предварительно карту.
    
def main(updater):
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text, geocoder))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    # main()
    setup_proxy_and_start(token=TOKEN, proxy=True)
