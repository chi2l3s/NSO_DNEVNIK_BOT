from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import telebot
from telebot import types
import sqlite3 as sq
from dotenv import load_dotenv

connection = sq.connect('users.db', check_same_thread=False)  # check_same_thread для потокобезопасности
connection.row_factory = sq.Row
cursor = connection.cursor()

# Создаем таблицу, если не существует
users_table = '''
CREATE TABLE IF NOT EXISTS "users" (
	"user_id" INTEGER NOT NULL UNIQUE,
	"gos_login" TEXT NOT NULL,
	"gos_password" TEXT
);
'''
cursor.execute(users_table)
connection.commit()

# Запрос для сохранения пользователя
save_user = '''
INSERT OR REPLACE INTO "users" (user_id, gos_login, gos_password) VALUES (?, ?, ?)
'''

class User:
    def __init__(self, user_id, gos_login, gos_password):
        self.user_id = user_id
        self.gos_login = gos_login
        self.gos_password = gos_password

    def __repr__(self):
        return f"User(user_id={self.user_id}, gos_login={self.gos_login}, gos_password={self.gos_password})"


bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))

user_agreement = """
ПОЛЬЗОВАТЕЛЬСКОЕ СОГЛАШЕНИЕ
Настоящее Пользовательское Соглашение (далее — "Соглашение") регулирует отношения между администрацией сервиса (далее — "Сервис") и пользователями (далее — "Пользователь") Telegram-бота, который получает доступ к электронному дневнику посредством авторизации на портале Госуслуги и отправляет данные в мессенджер.

Пожалуйста, внимательно ознакомьтесь с данным Соглашением перед началом использования Сервиса. Используя Сервис, вы соглашаетесь с условиями данного Соглашения.

1. Общие положения
1.1. Настоящее Соглашение является публичной офертой в соответствии со статьей 437 Гражданского кодекса РФ. 1.2. Использование Сервиса возможно только после принятия Пользователем условий данного Соглашения. 1.3. Администрация оставляет за собой право изменять условия настоящего Соглашения в одностороннем порядке. Продолжение использования Сервиса после внесения изменений считается согласием Пользователя с изменениями.

2. Описание Сервиса
2.1. Сервис предоставляет Пользователю возможность получать данные из электронного школьного дневника через портал Госуслуги и отправлять их в Telegram. 2.2. Для использования Сервиса Пользователь должен пройти авторизацию на портале Госуслуги, предоставив необходимые данные для входа. Сервис использует эти данные исключительно для авторизации и получения информации из электронного дневника.

3. Использование персональных данных
3.1. Сервис собирает и обрабатывает минимальные данные, необходимые для авторизации на портале Госуслуги, в соответствии с Политикой конфиденциальности. 3.2. Все полученные данные используются исключительно для выполнения функционала Сервиса — доступа к электронному дневнику и отправки информации в Telegram. 3.3. Администрация Сервиса принимает все необходимые меры для защиты персональных данных Пользователей в соответствии с действующим законодательством РФ.

4. Ответственность Пользователя
4.1. Пользователь обязуется использовать Сервис исключительно в законных целях и не предпринимать действий, направленных на взлом, нарушение работы Сервиса или получение несанкционированного доступа к данным. 4.2. Пользователь несет ответственность за сохранность своих учетных данных от несанкционированного доступа.

5. Ограничение ответственности
5.1. Администрация Сервиса не несет ответственности за возможные перебои в работе портала Госуслуги, некорректную работу внешних API или задержки в получении данных из электронного дневника. 5.2. Сервис предоставляется "как есть", и Администрация не гарантирует его бесперебойную и безошибочную работу.

6. Прекращение использования
6.1. Пользователь имеет право прекратить использование Сервиса в любой момент, прекратив взаимодействие с Telegram-ботом. 6.2. Администрация оставляет за собой право прекратить доступ к Сервису Пользователю в случае нарушения им условий данного Соглашения.

7. Заключительные положения
7.1. Настоящее Соглашение регулируется законодательством Российской Федерации. 7.2. Все споры, возникающие в рамках настоящего Соглашения, подлежат разрешению в соответствии с действующим законодательством РФ.
"""

def create_driver():
    return webdriver.Chrome()

def get_user_by_id(user_id):
    query = '''SELECT user_id, gos_login, gos_password FROM users WHERE user_id = ?'''
    
    # Выполнение запроса
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()  # Получаем одну строку из результата
    
    # Проверяем, найден ли пользователь
    if result:
        # Создаем экземпляр класса User с полученными данными
        user = User(result['user_id'], result['gos_login'], result['gos_password'])
        return user
    else:
        return None

@bot.message_handler(commands=['start'])
def start_cmd(message):
    reply_markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton('Пользовательское соглашение ❗❕', callback_data='user_agreement')
    reply_markup.add(btn)
    bot.send_message(message.chat.id, 'Добро пожаловать в бот! \n\nОбратите внимание: данный бот не является официальным источником информации ГИС "Электронная школа" или портала Госуслуги. Мы предоставляем удобный способ доступа к данным вашего электронного дневника через авторизацию на портале Госуслуги, но мы не являемся частью государственных систем и не несем ответственности за их работу или актуальность предоставляемой информации.', reply_markup=reply_markup)

@bot.callback_query_handler(func=lambda call: call.data == 'user_agreement')
def user_agreement_message(call):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton('Я согласен с данным пользовательским соглашением', callback_data='agree')
    markup.add(btn)
    bot.send_message(call.message.chat.id, user_agreement, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'agree')
def start_use(call):
    bot.send_message(call.message.chat.id, "Отлично. Для начала используй команду /login, чтобы сохранить свои данные для входа.")

@bot.message_handler(commands=['login'])
def get_login(message):
    bot.reply_to(message, 'Отправьте данные для входа в формате {логин}-{пароль}.')
    bot.register_next_step_handler(message, save)

def save(message):
    user_message = message.text
    if '-' in user_message:
        # Разделяем сообщение на логин и пароль
        login, password = user_message.split('-', 1)
        login_info = (message.from_user.id, login, password)

        # Сохраняем данные в базу
        cursor.execute(save_user, login_info)
        connection.commit()  # Подтверждаем изменения

        bot.send_message(message.chat.id, "Вы успешно авторизованы!")
    else:
        bot.send_message(message.chat.id, "Сообщение должно быть в формате 'login-password'. Попробуйте снова.")
        bot.register_next_step_handler(message, save)  # Повторная регистрация для обработки следующего сообщения

@bot.message_handler(commands=['test'])
def test_cmd(message):
    user = get_user_by_id(message.from_user.id)
    if user:
        bot.reply_to(message, f"{user.gos_login} {user.gos_password}")
    else:
        bot.reply_to(message, "Пользователь не найден.")

# Создаем словарь для хранения соответствий уникальных идентификаторов и URL
user_urls = {}

@bot.message_handler(commands=['test_login'])
def test_login(message):
    user = get_user_by_id(message.from_user.id)
    bot.send_message(message.chat.id, "Производится вход... В конце операции бот выведет имя вашего аккаунта.")
    if user:
        driver = create_driver()
        try:
            driver.get('https://school.nso.ru/journal-esia-action/')
            time.sleep(2)

            # Вводим логин
            login_field = driver.find_element(By.ID, 'login')
            login_field.send_keys(user.gos_login)

            # Вводим пароль
            pass_field = driver.find_element(By.ID, 'password')
            pass_field.send_keys(user.gos_password)

            # Нажимаем кнопку входа
            submit_button = driver.find_element(By.CLASS_NAME, 'plain-button')
            submit_button.click()

            time.sleep(4)

            bot.send_message(message.chat.id, "Введите шестизначный код, который пришел вам.")

            def code_handler(code_message):
                code = code_message.text
                try:
                    code_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="tel"]')
                    for i, digit in enumerate(code):
                        code_inputs[i].send_keys(digit)

                    bot.send_message(message.chat.id, "Ожидайте...")

                    time.sleep(10)

                    # Получаем имена пользователей и ссылки на них
                    markup = types.InlineKeyboardMarkup()
                    try:
                        users_els = WebDriverWait(driver, 20).until(
                            EC.presence_of_all_elements_located((By.CLASS_NAME, 'login-esia__user-fio'))
                        )
                    except Exception as e:
                        bot.send_message(message.chat.id, f"Ошибка при поиске пользователей: {str(e)}")
                        return

                    if not users_els:
                        bot.send_message(message.chat.id, "Не удалось найти элементы с именем пользователя.")
                        return

                    for i, el in enumerate(users_els):
                        parent_element = el.find_element(By.XPATH, "../..")
                        user_url = parent_element.get_attribute("url")  # Получаем URL атрибут родительского элемента
                        
                        # Создаем уникальный идентификатор
                        user_id = f"user_{i}"
                        
                        # Сохраняем соответствие ID и URL
                        user_urls[user_id] = user_url
                        
                        # Добавляем кнопку с коротким идентификатором
                        markup.add(types.InlineKeyboardButton(text=el.text, callback_data=user_id))  # Передаем ID

                    bot.send_message(message.chat.id, "Выберите пользователя: ", reply_markup=markup)
                except Exception as e:
                    bot.send_message(message.chat.id, f"Ошибка при вводе кода: {str(e)}")

            bot.register_next_step_handler(message, code_handler)

            @bot.callback_query_handler(func=lambda call: call.data.startswith('user_'))
            def open_dnevnik(call):
                try:
                    # Используем callback_data для нахождения нужного URL
                    selected_id = call.data
                    user_url = user_urls.get(selected_id)

                    if not user_url:
                        bot.send_message(call.message.chat.id, "Ошибка: не удалось найти URL для данного пользователя.")
                        return

                    user_button = driver.find_element(By.XPATH, f"//div[@url='{user_url}']")
                    user_button.click()

                    # Здесь можно добавить дополнительные шаги после успешного клика
                    bot.send_message(call.message.chat.id, "Пользователь выбран. Ожидайте...")

                    time.sleep(4)

                    markup = types.InlineKeyboardMarkup()

                    markup.add(types.InlineKeyboardButton('Оценки за 8 класс', callback_data='marks'))
                    markup.add(types.InlineKeyboardButton('Пероснал', callback_data='pers'))

                    bot.send_message(message.chat.id, 'Че те надо нахуй?', reply_markup=markup)

                    @bot.callback_query_handler(func=lambda call: call.data in ['marks', 'pers'])
                    def call(call):
                        if call.data == 'marks':
                            print_marks()
                        elif call.data == 'pers':
                            print_personal()

                    def print_marks():

                        driver.get('https://school.nso.ru/journal-student-resultmarks-action/view.results/?year=2023/2024')

                        time.sleep(3)

                        try:
                            # Ожидаем появления таблицы с оценками
                            table = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.ID, 'g0_marks'))
                            )

                            # Находим все элементы с классом 'cell', которые содержат оценки
                            cells = table.find_elements(By.CLASS_NAME, 'cell')

                            # Если нет элементов, информируем пользователя
                            if not cells:
                                bot.send_message(call.message.chat.id, "Нет оценок для отображения.")
                                return

                            # Обрабатываем каждый элемент
                            msg = ''
                            for cell in cells:
                                subject = cell.get_attribute('name')  # Название предмета
                                mark = cell.find_element(By.CLASS_NAME, 'cell-data').text  # Оценка
                                row = f'{subject} - {mark}. Так держать!'
                                
                                msg += row + "\n"

                                # Отправляем сообщение с названием предмета и оценкой
                                bot.send_message(call.message.chat.id, msg)

                        except Exception as e:
                            bot.send_message(call.message.chat.id, f"Ошибка при извлечении оценок: {str(e)}")

                        finally:
                            driver.quit()

                    def print_personal():
                        try:
                            # Открытие страницы
                            driver.get('https://school.nso.ru/journal-people-action')

                            # Ожидание появления элемента с ID 'people-list'
                            people_list = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.ID, 'people-list'))
                            )

                            # Получение таблицы и её содержимого
                            table = people_list.find_element(By.TAG_NAME, 'table')
                            tbody = table.find_element(By.TAG_NAME, 'tbody')
                            trs = tbody.find_elements(By.TAG_NAME, 'tr')

                            # Формирование сообщения
                            msg = 'Состав школы: \n\n'
                            for tr in trs:
                                td = tr.find_element(By.TAG_NAME, 'td')
                                # Получение позиции и имени
                                position = td.find_element(By.CLASS_NAME, 'people__person__position').text
                                name = td.find_element(By.CSS_SELECTOR, '.people__person__name span').text
                                msg += f"{position} - {name}" + "\n"

                            # Отправка сообщения через бота
                            bot.send_message(message.chat.id, msg)

                        except Exception as e:
                            # Обработка исключений, если что-то пойдёт не так
                            bot.send_message(message.chat.id, "Произошла ошибка при получении данных.")
                            print(f"Ошибка: {e}")

                        finally:
                            # Закрытие браузера
                            driver.quit()

                except Exception as e:
                    bot.send_message(call.message.chat.id, f"Ошибка при выборе пользователя: {str(e)}")


        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка: {str(e)}")
            driver.quit()
    else:
        bot.send_message(message.chat.id, "Пользователь не найден.")

bot.infinity_polling()
