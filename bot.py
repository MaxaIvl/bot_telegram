import logging

import time
import datetime

import asyncio
import datetime
import json

import os, re, configparser, pafy
import settings

import hashlib

from aiogram import Bot ,types , utils
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.utils.helper import Helper, HelperMode, ListItem
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import keyboard as nav 
from sqlighter import Database
from filters import IsAdminFilter
from aiogram.utils.markdown import hbold, hunderline, hcode, hlink
from aiogram.dispatcher.filters import Text
from aiogram.types.message import ContentType
from keyboard import back,make_keyboards,dowload
from main import check_news_update
import time 


#Задем уровень логирование
logging.basicConfig(level=logging.INFO)

config = configparser.ConfigParser()
config.read("settings.ini")
TOKEN = config["tgbot"]["token"]
YOOTOKEN="381764678:TEST:32007"

bot = Bot(token=settings.TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())

#активация фильтра
dp.filters_factory.bind(IsAdminFilter)

#инициализируем соеденение с БД
db = Database('db.db')

def days_to_seconds(days):
    return days * 24 * 60 * 60

def time_sub_day(get_time):
    time_now = int(time.time())
    middle_time = int(get_time)-time_now

    if middle_time <=0:
        return False
    else:
        dt = str(datetime.timedelta(seconds=middle_time))
        return dt


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if (not db.user_exists(message.from_user.id)):
        db.add_user(message.from_user.id)
        await bot.send_message(message.from_user.id, "Укажите Ваш никнейм: ")
    else:
        await bot.send_message(message.from_user.id, "Вы уже зарегистрированы!",reply_markup=nav.mainMenu)

@dp.message_handler(text='Скачать')
async def save_video(message: types.Message):
        if db.get_sub_status(message.from_user.id):
            await bot.send_message(chat_id=message.chat.id, text='Введите ссылку на видео: ', reply_markup=back())
            await Info.video.set()
        else:
                await bot.send_message(message.from_user.id,"Купите подписку!")

async def edit_name(message: types.Message, state: FSMContext):
    if message.text.lower() == 'Отмена':
        await bot.send_message(chat_id=message.chat.id, text='Вы вернулись в главное меню.', reply_markup=nav.mainMenu)
        await state.finish()
    else:
        if message.text.startswith('https://www.youtube.com/watch?v='):
            try:
                video_url = message.text
                await bot.send_message(chat_id=message.chat.id, text=f'Название видео: {get_title(video_url)}\nАвтор: {get_author(video_url)}\n\nВыберите качество загрузки:', reply_markup = make_keyboards(video_url))
                await state.finish()
            except OSError:
                await bot.send_message(chat_id=message.chat.id, text=f'Ссылка неверная, либо видео не найдено. Введи ссылку в формате: ```https://www.youtube.com/watch?v=...```', reply_markup = back(), parse_mode="Markdown")
            except ValueError:
                await bot.send_message(chat_id=message.chat.id, text=f'Ссылка неверная, либо видео не найдено. Введи ссылку в формате: ```https://www.youtube.com/watch?v=...```', reply_markup = back(), parse_mode="Markdown")
        else:
            await bot.send_message(chat_id=message.chat.id, text=f'Введите ссылку в формате: ```https://www.youtube.com/watch?v=...```', reply_markup = nav.mainMenu, parse_mode="Markdown")

@dp.message_handler(text=['Помощь'])
async def help(message:types.Message):
    try:
        await message.answer('Вот что умеет наш бот:\nПлатная подписка:\nСкачать - скачивает видео с ютуба\nОтмена- отмена скачивания с ютуба\nБез подписки:\n/ban-забанить пользователя\nВсе новости - просматривает новсти IT\nПросмотр последних 5 новстей\nСвежие новости - просмотри свежих новостей')
        await message.delete()
    except:
        await message.reply('Вот что умеет наш бот:\n/subscribe-подписаться на бота\n/unsubscribe-отписаться от бота')

@dp.message_handler(is_admin=True,commands=["ban"],commands_prefix="!/")
async def cmd_ban(message: types.Message):
    if not message.reply_to_message:
        await message.reply("Эта команда должна быть ответом на сообщение")
        return

    await message.bot.delete_message(config.GROUP_ID, message.message_id)
    await message.bot.kick_chat_member(chat_id=config.GROUP_ID, user_id=message.reply_to_message.from_user.id)
    await message.reply_to_message.reply('Пользователь забанен за нарушение!')

@dp.message_handler(Text(equals="Все новости"))
async def get_all_news(message: types.Message):
    with open("news_dict.json",encoding="utf-8") as file:
        news_dict = json.load(file)

    for k, v in sorted(news_dict.items()):
        news = f"{hbold(datetime.datetime.fromtimestamp(v['article_date_timestamp']))}\n" \
               f"{hlink(v['article_title'], v['article_url'])}"

        await message.answer(news)


@dp.message_handler(Text(equals="Последние 5 новостей"))
async def get_last_five_news(message: types.Message):
    with open("news_dict.json",encoding="utf-8") as file:
        news_dict = json.load(file)

    for k, v in sorted(news_dict.items())[-5:]:
        news = f"{hbold(datetime.datetime.fromtimestamp(v['article_date_timestamp']))}\n" \
               f"{hlink(v['article_title'], v['article_url'])}"

        await message.answer(news)


@dp.message_handler(Text(equals="Свежие новости"))
async def get_fresh_news(message: types.Message):
    fresh_news = check_news_update()

    if len(fresh_news) >= 1:
        for k, v in sorted(fresh_news.items()):
            news = f"{hbold(datetime.datetime.fromtimestamp(v['article_date_timestamp']))}\n" \
                   f"{hlink(v['article_title'], v['article_url'])}"

            await message.answer(news)

    else:
        await message.answer("Пока нет свежих новостей...")

async def news_every_minute():
    while True:
        fresh_news = check_news_update()

        if len(fresh_news) >= 1:
            for k, v in sorted(fresh_news.items()):
                news = f"{hbold(datetime.datetime.fromtimestamp(v['article_date_timestamp']))}\n" \
                       f"{hlink(v['article_title'], v['article_url'])}"

                # get your id @userinfobot
                await bot.send_message(user_id, news, disable_notification=True)

        else:
            await bot.send_message(user.id, "Пока нет свежих новостей...", disable_notification=True)

        await asyncio.sleep(40)

@dp.message_handler()
async def bot_message(message:types.Message):
    if message.chat.type == 'private':
        if message.text == 'Профиль':
            user_nickname = "Ваш ник: " + db.get_nickname(message.from_user.id)        
            users_sub = time_sub_day(db.get_time_sub(message.from_user.id))
            if users_sub == False:
                users_sub = "Не активна"
            users_sub = "\nПодписка: " + users_sub
            await bot.send_message(message.from_user.id, user_nickname + users_sub)

        elif message.text == 'Подписка':
            await bot.send_message(message.from_user.id, "Подписка на месяц для скачивания видео с ютуба", reply_markup=nav.sub_inline_markup)

        else:
            if db.get_signup(message.from_user.id) == "setnickname":
                if(len(message.text) > 20):
                    await bot.send_message(message.from_user.id, "Никнейм не должен превышать 20 символов")
                elif '@' in message.text or '/' in message.text:
                    await bot.send_message(message.from_user.id, "Вы ввели запрещенные символы : @/")
                else:
                    db.set_nickname(message.from_user.id, message.text)
                    db.set_signup(message.from_user.id,"done")
                    await bot.send_message(message.from_user.id, "Регистрация прошла успешно",reply_markup=nav.mainMenu)
            else:
                await bot.send_message(message.from_user.id, "Данной функции нет")


@dp.callback_query_handler(text='submonth')
async def submoth(call: types.CallbackQuery):
    await bot.delete_message(call.from_user.id,call.message.message_id)
    await bot.send_invoice(chat_id=call.from_user.id, title="Оформление подписки", description="Подписка на месяц", payload="month_sub", provider_token=YOOTOKEN, currency="RUB", start_parameter="test_bot", prices=[{"label":"Руб.","amount":15000}])

@dp.pre_checkout_query_handler()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def procces_pay(message: types.Message):
    if message.successful_payment.invoice_payload == "month_sub":
        time_sub = int(time.time()) + days_to_seconds(30)
        db.set_time_sub(message.from_user.id, time_sub)
        await bot.send_message(message.from_user.id, "Вам выдана подписка на месяц!")

@dp.callback_query_handler()
async def handler_call(call: types.CallbackQuery, state: FSMContext):
    chat_id = call.from_user.id
    if call.data.startswith('best_with_audio'):
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        video_url = get_url(call.data)
        download_link = get_download_url_with_audio(video_url)
        await bot.send_message(chat_id=chat_id, text=f' Вот ваша ссылка на скачивание видео: {download_link}', reply_markup =dowload())
    elif call.data.startswith('best_video'):
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        video_url = get_url(call.data)
        download_link = get_download_url_best_video(video_url)
        await bot.send_message(chat_id=chat_id, text=f' Вот ваша ссылка на скачивание видео: {download_link}', reply_markup = dowload())
    elif call.data.startswith('best_audio'):
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        video_url = get_url(call.data)
        download_link = get_download_url_best_audio(video_url)
        await bot.send_message(chat_id=chat_id, text=f' Вот ваша ссылка на скачивание аудио: {download_link}', reply_markup = dowload())
    elif call.data == 'cancel':
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await bot.send_message(chat_id=chat_id, text='Вы вернулись в главное меню.', reply_markup=nav.mainMenu)

def get_title(url):
    yVideo = pafy.new(url)
    title = yVideo.title
    return title

def get_author(url):
    yVideo = pafy.new(url)
    author = yVideo.author
    return author

def get_url(call):
    url = call.split('|')
    video_url = url[1]
    return video_url

def get_download_url_with_audio(url_video):
    yVideo = pafy.new(url_video)
    video = yVideo.getbest()
    return video.url_https

def get_download_url_best_video(url_video):
    yVideo = pafy.new(url_video)
    video = yVideo.getbestvideo()
    return video.url_https

def get_download_url_best_audio(url_video):
    yVideo = pafy.new(url_video)
    video = yVideo.getbestaudio()
    return video.url_https

class Info(StatesGroup):
    video = State()


@dp.message_handler(state=Info.video, content_types=types.ContentTypes.TEXT)
async def edit_name(message: types.Message, state: FSMContext):
    if message.text.lower() == 'отмена':
        await bot.send_message(chat_id=message.chat.id, text='Вы вернулись в главное меню.', reply_markup=nav.mainMenu)
        await state.finish()
    else:
        if message.text.startswith('https://www.youtube.com/watch?v='):
            try:
                video_url = message.text
                await bot.send_message(chat_id=message.chat.id, text=f'Название видео: {get_title(video_url)}\nАвтор: {get_author(video_url)}\n\nВыберите качество загрузки:', reply_markup = make_keyboards(video_url))
                await state.finish()
            except OSError:
                await bot.send_message(chat_id=message.chat.id, text=f'Ссылка неверная, либо видео не найдено. Введи ссылку в формате: ```https://www.youtube.com/watch?v=...```', reply_markup = back(), parse_mode="Markdown")
            except ValueError:
                await bot.send_message(chat_id=message.chat.id, text=f'Ссылка неверная, либо видео не найдено. Введи ссылку в формате: ```https://www.youtube.com/watch?v=...```', reply_markup = back(), parse_mode="Markdown")
        else:
            await bot.send_message(chat_id=message.chat.id, text=f'Введи ссылку в формате: ```https://www.youtube.com/watch?v=...```', reply_markup = nav.mainMenu, parse_mode="Markdown")



#Вход в точку программы
if __name__ =='__main__':
    executor.start_polling(dp,skip_updates=False)
