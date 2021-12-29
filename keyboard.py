from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


btnProfile = KeyboardButton('Профиль')
btnSub = KeyboardButton('Подписка')
helper = KeyboardButton('Помощь')
nonvosti = KeyboardButton('Все новости')
nonvosti1 = KeyboardButton('Последние 5 новостей')
nonvosti3 = KeyboardButton('Свежие новости')
download_button = KeyboardButton('Скачать')
mainMenu = ReplyKeyboardMarkup(resize_keyboard=True)
mainMenu.add(btnProfile,btnSub)
mainMenu.add(nonvosti).add(nonvosti1).add(nonvosti3).add(download_button)
mainMenu.add(helper)

sub_inline_markup = InlineKeyboardMarkup(row_width=1)
btnSubMonth = InlineKeyboardButton(text="Месяц - 150 рублей", callback_data="submonth")
sub_inline_markup.insert(btnSubMonth)

def dowload():
    download_button = KeyboardButton('Скачать')
    menu_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    menu_kb.add(download_button)
    return menu_kb
def back():
    button_back = KeyboardButton('Отмена')
    back_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    back_kb.add(button_back)
    return back_kb
    return mainMenu
def make_keyboards(url):
    inline_kb1 = InlineKeyboardMarkup()
    button = InlineKeyboardButton('Лучшее качество до 720p(с звуком).', callback_data=f'best_with_audio|{url}')
    button2 = InlineKeyboardButton('Лучшее качество(без звука).', callback_data=f'best_video|{url}')
    button3 = InlineKeyboardButton('Звук в лучшем качестве.', callback_data=f'best_audio|{url}')
    button4 = InlineKeyboardButton('Отмена', callback_data=f'cancel')
    inline_kb1.add(button)
    inline_kb1.add(button2)
    inline_kb1.add(button3)
    inline_kb1.add(button4)
    return inline_kb1