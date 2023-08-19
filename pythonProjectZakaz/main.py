import telebot
import sqlite3
import datetime
import requests
import random
import string
import pyperclip
from telebot import types
from config import *
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

bot = telebot.TeleBot('6642921305:AAEL6ZdNP7o7nzHeaQz4haojqnpkWNsbKDE')

# Функция для создания базы данных
def create_database():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS пользователи
                      (user_id text PRIMARY KEY,
                       username text,
                       email text,
                       phone text,
                       full_name text,
                       secret_password text,
                       registration_date text,
                       ip_address text, 
                       course_name text,
                       course_price real,
                       discounted_price real,
                       contest_participation_date text)''')
    conn.commit()
    conn.close()

# Функция для получения IP-адреса пользователя
def get_user_ip():
    try:
        response = requests.get('https://httpbin.org/ip')
        data = response.json()
        ip_address = data['origin']
    except:
        ip_address = 'Unknown'
    return ip_address

# Обработка команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, text=start, parse_mode='Markdown')
    msg = bot.send_message(message.chat.id, login, parse_mode='Markdown')
    bot.register_next_step_handler(msg, process_username_step)


def process_username_step(message):
    username = message.text

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO пользователи (user_id, username) VALUES (?, ?)", (message.chat.id, username))
    cursor.execute("UPDATE пользователи SET username = ? WHERE user_id = ?", (username, message.chat.id))
    conn.commit()
    conn.close()
    bot.send_message(message.chat.id, text=email1, parse_mode='Markdown')
    msg = bot.send_message(message.chat.id, email2, parse_mode='Markdown')
    bot.register_next_step_handler(msg, process_email_step)

def process_email_step(message):
    email = message.text

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE пользователи SET email = ? WHERE user_id = ?", (email, message.chat.id))
    conn.commit()
    conn.close()

    msg = bot.send_message(message.chat.id, text=phone, parse_mode='Markdown')
    bot.register_next_step_handler(msg, process_phone_step)

def process_phone_step(message):
    phone = message.text

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE пользователи SET phone = ? WHERE user_id = ?", (phone, message.chat.id))
    conn.commit()
    conn.close()

    msg = bot.send_message(message.chat.id, text=name, parse_mode='Markdown')
    bot.register_next_step_handler(msg, process_full_name_step)

def process_full_name_step(message):
    full_name = message.text

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE пользователи SET full_name = ? WHERE user_id = ?", (full_name, message.chat.id))
    conn.commit()
    conn.close()

    generate_password_button = telebot.types.InlineKeyboardButton("Сгенерировать", callback_data="generate_password")
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(generate_password_button)

    msg = bot.send_message(message.chat.id, text=password, reply_markup=keyboard, parse_mode='Markdown')
    bot.register_next_step_handler(msg, process_secret_password_step)

def generate_random_password():
    length = 8
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

def process_secret_password_step(message):
    markup = telebot.types.InlineKeyboardMarkup()
    konkye = telebot.types.InlineKeyboardButton('Да', callback_data="participate_in_contest")
    konkno = telebot.types.InlineKeyboardButton('Нет', callback_data="no")
    markup.row(konkye, konkno)
    user_id = message.chat.id
    secret_password = message.text

    if secret_password == "/generate":
        secret_password = generate_random_password()

    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ip_address = get_user_ip()

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE пользователи SET secret_password = ?, registration_date = ?, ip_address = ? WHERE user_id = ?",
        (secret_password, current_date, ip_address, message.chat.id))
    conn.commit()
    conn.close()

    # Регистрация завершена, можно выполнить необходимые действия
    bot.send_message(message.chat.id, text=reg, parse_mode='Markdown')
    keyboard = telebot.types.InlineKeyboardMarkup()
    copy_button = telebot.types.InlineKeyboardButton("Скопировать", callback_data="copy_password")
    keyboard.add(copy_button)
    bot.send_message(message.chat.id, text=sekpas + secret_password, reply_markup=keyboard, parse_mode='Markdown')

    # Отправка сообщения с кнопкой "Принять участие в конкурсе"
    bot.send_message(user_id, text=kon, reply_markup=markup, parse_mode='Markdown')


passwords = {}  # Словарь для хранения паролей по идентификатору пользователя

@bot.callback_query_handler(func=lambda call: call.data == "generate_password")
def generate_password_callback(call):
    keyboard = types.InlineKeyboardMarkup()
    copy_button = types.InlineKeyboardButton("Скопировать", callback_data="copy_password")
    keyboard.add(copy_button)

    markup = types.InlineKeyboardMarkup()
    konkye = types.InlineKeyboardButton('Да', callback_data="participate_in_contest")
    konkno = types.InlineKeyboardButton('Нет', callback_data="no")
    markup.row(konkye,konkno)

    generated_password = generate_random_password()
    user_id = call.message.chat.id

    # Сохраняем пароль в словаре по идентификатору пользователя
    passwords[user_id] = generated_password

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE пользователи SET secret_password = ? WHERE user_id = ?", (generated_password, user_id))
    conn.commit()
    conn.close()

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=sekpas2 + generated_password, parse_mode='Markdown')


    bot.send_message(user_id, text=sekpas + generated_password, reply_markup=keyboard, parse_mode='Markdown')
    bot.send_message(user_id, text=reg, parse_mode='Markdown')
    # Отправка сообщения с кнопкой "Принять участие в конкурсе"
    bot.send_message(user_id, text=kon, reply_markup=markup, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "no")
def no_callback(call):
    bot.send_message(call.message.chat.id,text=otkaz1, parse_mode="Markdown")
    bot.send_message(call.message.chat.id,text=otkaz2, parse_mode="Markdown")

# Обработка Inline-кнопки "Скопировать"
@bot.callback_query_handler(func=lambda call: call.data == "copy_password")
def copy_password_callback(call):
    user_id = call.message.chat.id

    if user_id in passwords:
        generated_password = passwords[user_id]
        pyperclip.copy(generated_password)
        bot.answer_callback_query(call.id, text="Пароль скопирован!")
    else:
        bot.answer_callback_query(call.id, text="Пароль не найден.")
# Создание базы данных перед запуском бота
create_database()

@bot.callback_query_handler(func=lambda call: call.data == "participate_in_contest")
def participate_in_contest_callback(call):
    user_id = call.from_user.id
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE пользователи SET contest_participation_date = ? WHERE user_id = ?", (current_date, user_id))
    conn.commit()
    conn.close()
    send_product_info(user_id)


# Функция, которая отправляет сообщение "Вы приняли участие!"
def send_product_info(user_id):
    random.shuffle(products)  # Перемешиваем список продуктов перед выбором случайного продукта
    product = random.choice(products)
    discount = random.choice(discounts)

    product_name = product["название"]
    product_description = product["описание"]
    product_price = product["стоимость"]
    discounted_price = product_price - (product_price * discount / 100)

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE пользователи SET course_name = ?, course_price = ?, discounted_price = ? WHERE user_id = ?",
                   (product_name, product_price, discounted_price, user_id))
    conn.commit()
    conn.close()

    message = f"Название: {product_name}\n\n" \
              f"Описание: {product_description}\n\n" \
              f"Стоимость: {product_price} руб.\n" \
              f"Скидка: {discount}%\n" \
              f"Цена со скидкой: {discounted_price} руб."

    bot.send_message(user_id, message, parse_mode="Markdown")




@bot.message_handler(commands=['menu'])
def handle_start(message):
    markup = create_main_menu_markup()
    bot.send_message(message.chat.id, 'Добро пожаловать в главное меню!', reply_markup=markup)

def create_main_menu_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    education_button = types.KeyboardButton('Образование')
    market = types.KeyboardButton('Маркет')
    our_projects_button = types.KeyboardButton('Наши проекты')
    personal_cabinet_button = types.KeyboardButton('Личный кабинет')


    markup.add(education_button, market, our_projects_button, personal_cabinet_button)

    return markup

@bot.message_handler(func=lambda message: message.text == 'Маркет')
def market(message):
    bot.send_message(message.chat.id, 'Образование:')

@bot.message_handler(func=lambda message: message.text == 'Образование')
def handle_education(message):
    markup = types.InlineKeyboardMarkup()
    channel_button = types.InlineKeyboardButton('Канал', url='https://t.me/+I2GA5vUkLmc2MTNi')
    chat_button = types.InlineKeyboardButton('Чат', url='https://t.me/+zIYKF6WCdekzY2My')
    back_button = types.InlineKeyboardButton('Назад', callback_data='back')

    markup.row(channel_button, chat_button)
    markup.row(back_button)

    bot.send_message(message.chat.id, 'Образование:', reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Личный кабинет')
def handle_personal_cabinet(message):
    markup = types.InlineKeyboardMarkup()
    subscriptions = types.InlineKeyboardButton('Подписки', callback_data='subscriptions')
    contacts = types.InlineKeyboardButton('Контакты', callback_data='contacts')
    back_button = types.InlineKeyboardButton('Назад', callback_data='back')

    markup.row(subscriptions, contacts)
    markup.row(back_button)

    bot.send_message(message.chat.id, 'Личный кабинет:', reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Наши проекты')
def handle_our_projects(message):
    markup = types.InlineKeyboardMarkup()
    video = types.InlineKeyboardButton('Видео студия', url='https://instagram.com/fresh.ms?igshid=NTc4MTIwNjQ2YQ==')
    brain = types.InlineKeyboardButton('Brain University ', url='https://Brainuniversity.ru')
    back_button = types.InlineKeyboardButton('Назад', callback_data='back')

    markup.row(video)
    markup.row(brain)
    markup.row(back_button)

    bot.send_message(message.chat.id, '*Наши проекты*:', reply_markup=markup, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == 'programs')
def handle_programs(callback_query):
    # Обработка нажатия кнопки "Приобретенные программы"
    bot.answer_callback_query(callback_query.id, text='Открыть список приобретенных программ')

@bot.callback_query_handler(func=lambda call: call.data == 'user_info')
def handle_user_info(callback_query):
    # Обработка нажатия кнопки "Личный кабинет пользователя"
    bot.answer_callback_query(callback_query.id, text='Открыть личный кабинет пользователя')

@bot.callback_query_handler(func=lambda call: call.data == 'contacts')
def contacts(callback_query):
    # Обработка нажатия кнопки "Контакты"
    text = "*Контакты:*\n\n__Сайт__:\nDigitaled.info\n\n__Email:__\nHello@digitaled.info\nSupport@digitaled.info"
    bot.send_message(callback_query.message.chat.id, text, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == 'back')
def handle_back(callback_query):
    # Обработка нажатия кнопки "Назад"
    markup = create_main_menu_markup()
    bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id,
text='Добро пожаловать в главное меню!', reply_markup=markup)



# Запуск бота
bot.polling(none_stop=True)

