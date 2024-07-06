import os
import telebot
import requests
from telebot import types
from dotenv import load_dotenv

load_dotenv()

bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))

region_id = None
name = None
salary_to = 2147483647
salary_from = 0
time_day = None
data = None
k = 1


def vacancy(vac):
    salary = 'не указана оплата\n'
    if int(vac['salaryFrom']) != 0 and int(vac['salaryTo']) != 0:
        salary = f"от {vac['salaryFrom']} до {vac['salaryTo']}\n"
    elif int(vac['salaryFrom']) != 0 and int(vac['salaryTo']) == 0:
        salary = f"от {vac['salaryFrom']}\n"
    elif int(vac['salaryFrom']) == '0' and int(vac['salaryTo']) != 0:
        salary = f"до {vac['salaryTo']}\n"
    mes = f"{vac['vacancy']}\n" \
          f"Компания: {vac['employer']}\n" + salary +\
          f"Адреc: {vac['address']} \n" \
          f"Требования: {vac['requirement']}\n" \
          f"Описание: {vac['requirement']}\n" \
          f"{vac['timeDay']}\n" \
          f"Дата: {vac['time']}\n" \
          f"Ссылка: {vac['alternate_url']}"
    return mes


@bot.message_handler(commands=['start', 'menu'])
def start(message):
    global k
    k = 1
    markup = types.ReplyKeyboardMarkup()
    btn = types.KeyboardButton("Поиск работы")
    markup.add(btn)
    bot.send_message(message.chat.id, "Привтствую, вас смертный, сей бот поможет определиться кто же ты, может быть воин?",
                     reply_markup=markup)
    bot.register_next_step_handler(message, open_search)


def open_search(message):
    if message.text == "Поиск работы":
        bot.send_message(message.chat.id, "В какой регион вы хотите направить свои стопы?",
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_id_region)
    else:
        bot.send_message(message.chat.id, "Ничего не понял, но очень интересно",
                         reply_markup=types.ReplyKeyboardRemove())


def get_id_region(message):
    url = f"http://app:5000/region/{message.text}"
    data = requests.get(url).json()
    global region_id
    if data.get('id') is not None:
        region_id = data["id"]
        bot.send_message(message.chat.id, "Какая профессия вас интересует")
        bot.register_next_step_handler(message, get_name)
    else:
        bot.send_message(message.chat.id, "Если когда то этот регион и существовал, то у меня для вас плохие новости")
        bot.register_next_step_handler(message, get_id_region)


def get_name(message):
    global name
    name = message.text.replace(" ", "+")
    markup = types.ReplyKeyboardMarkup()
    btn = types.KeyboardButton("Не важно")
    markup.add(btn)
    bot.send_message(message.chat.id, "От скольки желаем получать",
                     reply_markup=markup)
    bot.register_next_step_handler(message, get_salary_from)


def get_salary_from(message):
    global salary_from
    if message.text != "Не важно":
        salary_from = message.text
    markup = types.ReplyKeyboardMarkup()
    btn = types.KeyboardButton("Не важно")
    markup.add(btn)
    bot.send_message(message.chat.id, "До скольки желаем получать",
                     reply_markup=markup)
    bot.register_next_step_handler(message, get_salary_to)


def get_salary_to(message):
    global salary_to
    if message.text != "Не важно":
        salary_to = message.text
    markup = types.ReplyKeyboardMarkup()
    td1 = types.KeyboardButton("Полная занятость")
    td2 = types.KeyboardButton("Частичная занятость")
    markup.row(td1, td2)
    btn = types.KeyboardButton("Не важно")
    markup.row(btn)
    bot.send_message(message.chat.id, "Как работаем?",
                     reply_markup=markup)
    bot.register_next_step_handler(message, get_time_day)


def get_time_day(message):
    global time_day
    if message.text != "Пропустить":
        time_day = message.text
    url = f"http://app:5000/vacancy?vacancy={name}&salaryFrom={salary_from}&salaryTo={salary_to}&" \
          f"timeDay={time_day}&area={region_id}"
    global data
    data = requests.get(url).json()
    if not data:
        bot.send_message(message.chat.id, "Увы, но такой работёнке тут нет", reply_markup=types.ReplyKeyboardRemove())
    else:
        vac = data[0]
        markup = types.ReplyKeyboardMarkup()
        btn1 = types.KeyboardButton("Скип")
        btn2 = types.KeyboardButton("Меню")
        markup.row(btn1,btn2)
        bot.send_message(message.chat.id, vacancy(vac), reply_markup=markup)
        bot.register_next_step_handler(message, next_vacancy)


def next_vacancy(message):
    global k
    if message.text == 'Скип' and k < len(data)-1:
        vac = data[k]
        markup = types.ReplyKeyboardMarkup()
        btn1 = types.KeyboardButton("Скип")
        btn2 = types.KeyboardButton("Меню")
        markup.row(btn1, btn2)
        bot.send_message(message.chat.id, vacancy(vac), reply_markup=markup)
        k += 1
        bot.register_next_step_handler(message, next_vacancy)
    elif message.text == 'Скип' and k == len(data)-1:
        vac = data[k]
        markup = types.ReplyKeyboardMarkup()
        btn = types.KeyboardButton("Меню")
        markup.add(btn)
        bot.send_message(message.chat.id, vacancy(vac), reply_markup=markup)
        bot.register_next_step_handler(message, start)
    elif message.text == 'Меню':
        bot.send_message(message.chat.id, "Для выхода в меню нажимать сюда: /menu", reply_markup=types.ReplyKeyboardRemove())
    else:
        bot.send_message(message.chat.id, "Ничего не понял, но очень интересно",
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, next_vacancy)


bot.polling(none_stop=True)