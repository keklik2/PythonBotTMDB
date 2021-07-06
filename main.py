import telebot
# telebot - это непосредственно pyTelegramBotApi, просто такое название класса в библиотеке
from telebot import types
# Очередной класс, для чего-то он тут нужен ))00))
from requests import get
# Из библиотеки request получаем get(), который нужен для вставления картинок по ссылкам в сообщения
from queue import Queue
# Испорт логики
import tBot

# TOKEN для связи бота и написанного кода
TELEGRAM_TOKEN = '1897248148:AAF0ASP4HS4ChGjdfDPXjqg-X7u0k-Q8KNw'
# Создание бота по токену
bot = telebot.TeleBot(TELEGRAM_TOKEN)


# Функция для отображения в приемлемом для пользователя виде информации о его запросец
def print_request_result(message):
    # Проверка на то, выполнилась ли заданная функция (например, если запросить топ фильмов, то в очереди должно быть 8 фильмов)
    # Если же очередь пустая, то что-то пошло не так и пользователь получает сохранённое сообщение об ошибке
    if tBot.movies_to_be_shown.qsize() != 0:
        # Поскльку элементов в очереди может быть как 1, так и 100 (теоретически), информация выводится в цикле, пока
        # в очереди не останется элементов. Напоминаю, метод .get() в очереди и возвращает запрашиваемый элемент и удаляет его после этого
        while tBot.movies_to_be_shown.qsize() != 0:
            # Получаем "верхний" элемент очереди и сохраняем в переменную
            next_movie = tBot.movies_to_be_shown.get()
            # Вводим новую переменную с текстом, который будет отображён пользователю (для удобства)
            # Сам текст получаем методом .show_info() из класса Movie
            str_to_be_printed = next_movie.show_info()
            # Если у полученного фильма/сериала есть обложка, то добавляем картинку по ссылке к тексту
            # Если постера нет, то ссылка будет равна 'none', на что и идёт проверка. В этом случае говорим пользователю, что фото нет
            if str(next_movie.get_img_url()).lower() != 'none' and str(next_movie.get_img_url()).lower() != 'null':
                # Вызываем у бота метод отправки сообщения, в который передаются id (честно, не до конца понял: пользователя или чата)
                # и вторым аргументом передаётся фотография, полученная по ссылке
                # Методом get() получаем информацию по ссылке (парсим её), после чего получаем уже фотографию из информации методом .content()
                bot.send_photo(message.chat.id, get(tBot.WEB_IMG_URL.format(img=next_movie.get_img_url())).content)
            else:
                bot.send_message(message.chat.id, 'Картинки нет (:')
                # Метод .send_message как и метод отправки фото получае id и текст, который будет отправлен
            bot.send_message(message.chat.id, str_to_be_printed)
    else:
        # Если же бот не получил запрашиваемой информации (произошла ошибка), он сообщает об этом пользователю
        str_to_be_printed = tBot.err_msg
        bot.send_message(message.chat.id, str_to_be_printed)


# Вспомогательная функция
# Получаем от пользователя название сериала, отправляем сообщение о начале работы по запросу и вызываем метод из tBot с логикой запроса
# В конце вызывается метод, который показывает пользователю полученную инфомацию
def get_tv_name(message):
    series_name = message.text.lower()
    bot.send_message(message.chat.id,
                     'Придётся немного подождать, загружаю информацию...')
    tBot.get_info(series_name, tBot.WEB_TYPE_TV)
    print_request_result(message)


# Вспомогательная функция
# Получаем от пользователя название фильма, отправляем сообщение о начале работы по запросу и вызываем метод из tBot с логикой запроса
# В конце вызывается метод, который показывает пользователю полученную инфомацию
def get_movie_name(message):
    series_name = message.text.lower()
    bot.send_message(message.chat.id,
                     'Придётся немного подождать, загружаю информацию...')
    tBot.get_info(series_name, tBot.WEB_TYPE_MOVIE)
    print_request_result(message)


# Вспомогательная функция
# Получаем от пользователя название сериала, отправляем сообщение о начале работы по запросу и вызываем метод из tBot с логикой запроса
# В конце вызывается метод, который показывает пользователю полученную инфомацию
def get_tv_recommend(message):
    series_name = message.text.lower()
    bot.send_message(message.chat.id,
                     'Придётся немного подождать, загружаю информацию...')
    tBot.make_recommendations_to_watch(tBot.WEB_TYPE_TV, series_name)
    print_request_result(message)


# Вспомогательная функция
# Получаем от пользователя название фильма, отправляем сообщение о начале работы по запросу и вызываем метод из tBot с логикой запроса
# В конце вызывается метод, который показывает пользователю полученную инфомацию
def get_movie_recommend(message):
    series_name = message.text.lower()
    bot.send_message(message.chat.id,
                     'Придётся немного подождать, загружаю информацию...')
    tBot.make_recommendations_to_watch(tBot.WEB_TYPE_MOVIE, series_name)
    print_request_result(message)


# Метод для обработки нажатия по кнопкам (не команд, а именно кнопок)
@bot.callback_query_handler(func=lambda call: True)
def data(call):
    if call.message:
        # Все перечисленные ниже методы выполняют разные действия по одному принципу:
        # В зависимости от запрашиваемого функционала они либо просят от пользователя дополнительную инфу,
        # либо непосредственно запускают метод логики из tBot и переходят к функции печати вывода
        if call.data == 'info_tv':
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id,
                             'Напиши название сериала, желательно полное, чтобы мне было легче его найти (:')
            # register_next_step_handler(id, функция) - запускает следующую функцию, указанную вторым аргументом
            # и передаёт в неё информацию, указанную первым аргументом. При этом ждёт от пользователя ответа на следующий шаг
            # и на это время бот не воспринимает другие команды
            bot.register_next_step_handler(call.message, get_tv_name)

        elif call.data == 'info_movie':
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id,
                             'Напиши название фильма, желательно полное, чтобы мне было легче его найти (:')
            # register_next_step_handler(id, функция) - запускает следующую функцию, указанную вторым аргументом
            # и передаёт в неё информацию, указанную первым аргументом. При этом ждёт от пользователя ответа на следующий шаг
            # и на это время бот не воспринимает другие команды
            bot.register_next_step_handler(call.message, get_movie_name)

        elif call.data == 'latest_tv':
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id,
                             'Придётся немного подождать, загружаю информацию...')
            tBot.get_latest_release(tBot.WEB_TYPE_TV)
            print_request_result(call.message)

        elif call.data == 'latest_movie':
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id,
                             'Придётся немного подождать, загружаю информацию...')
            tBot.get_latest_release(tBot.WEB_TYPE_MOVIE)
            print_request_result(call.message)

        elif call.data == 'top_tv':
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id,
                             'Придётся немного подождать, загружаю информацию...')
            tBot.get_with_modifier(tBot.WEB_TYPE_TV, tBot.WEB_MODIFIER_POPULAR)
            print_request_result(call.message)

        elif call.data == 'top_movie':
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id,
                             'Придётся немного подождать, загружаю информацию...')
            tBot.get_with_modifier(tBot.WEB_TYPE_MOVIE, tBot.WEB_MODIFIER_POPULAR)
            print_request_result(call.message)

        elif call.data == 'top_rated_tv':
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id,
                             'Придётся немного подождать, загружаю информацию...')
            tBot.get_with_modifier(tBot.WEB_TYPE_TV, tBot.WEB_MODIFIER_TOP_RATED)
            print_request_result(call.message)

        elif call.data == 'top_rated_movie':
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id,
                             'Придётся немного подождать, загружаю информацию...')
            tBot.get_with_modifier(tBot.WEB_TYPE_MOVIE, tBot.WEB_MODIFIER_TOP_RATED)
            print_request_result(call.message)

        elif call.data == 'recommend_tv':
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id,
                             'Введи название любимого сериала. На его основе я предложу тебе 5 кино-картин, которые могу тебя заинтересовать (:')
            # register_next_step_handler(id, функция) - запускает следующую функцию, указанную вторым аргументом
            # и передаёт в неё информацию, указанную первым аргументом. При этом ждёт от пользователя ответа на следующий шаг
            # и на это время бот не воспринимает другие команды
            bot.register_next_step_handler(call.message, get_tv_recommend)

        elif call.data == 'recommend_movie':
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id,
                             'Введи название любимого фильма. На его основе я предложу тебе 5 кино-картин, которые могу тебя заинтересовать (:')
            # register_next_step_handler(id, функция) - запускает следующую функцию, указанную вторым аргументом
            # и передаёт в неё информацию, указанную первым аргументом. При этом ждёт от пользователя ответа на следующий шаг
            # и на это время бот не воспринимает другие команды
            bot.register_next_step_handler(call.message, get_movie_recommend)

        elif call.data == 'watch_tv':
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id,
                             'Придётся немного подождать, загружаю информацию...')
            tBot.make_series_to_watch(0)
            print_request_result(call.message)

        elif call.data == 'watch_movie':
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id,
                             'Придётся немного подождать, загружаю информацию...')
            tBot.make_series_to_watch(1)
            print_request_result(call.message)

        elif call.data == 'watch_mixed':
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id,
                             'Придётся немного подождать, загружаю информацию...')
            tBot.make_series_to_watch(2)
            print_request_result(call.message)


# Метод обработки команды help
@bot.message_handler(commands=['help', 'помощь'])
def help_func(message):
    # Отправляет простое сообщение с информацией, команды на английском становятся кликабельными
    bot.send_message(message.from_user.id,
                     "С моей помощью можно:\n"
                     "- Узнать информацию о фильме/сериале. Для этого напиши /info или /инфа;\n"
                     "- Узнать о самом последнем релизе фильма или сериала. Для этого напиши /latest или /последний;\n"
                     "- Увидеть топ самых популярных на сегодняшний день фильмов/сериалов. Для этого напиши /top или /топ;\n"
                     "- Увидеть самые рейтинговые на сегодняшний день фильмы/сериалы. Для этого напиши /rating или /рейтинг;\n"
                     "- Получить рекомендации похожих фильмов/сериалов по любимой кино-картине. Для этого напиши /recommend или /рекомендация;\n"
                     "- Если не знаешь, что посмотреть, могу порекомендовать 5 случайных кино-картин для просмотра. Для этого напиши \"Что посмотреть\" или /watch, или /посмотреть;\n"
                     "- Не забывай, что я всего лишь бот, а если хочешь побольше узнать о моих разработчиках, напиши: /developers.")


# Метод обработки команды info
@bot.message_handler(commands=['info', 'инфа'])
def info_func(message):
    # Создаём двумерный массив с кнопками
    # types.InlineKeyboardButton() создаёт одну кнопку, где text - то, что написано на кнопке для пользователя,
    # а callback_data - текстовый маркер, который указывает callback_query_handler'у какая кнопка была нажата и что надо сделать
    keyboard_info_buttons = [[types.InlineKeyboardButton(text='О сериале', callback_data='info_tv'),
                              types.InlineKeyboardButton(text='О фильме', callback_data='info_movie')]]
    # Создаём InlineKeyboardMarkup из массива кнопок, это то, что будет отображаться. По сути контейнер с кнопками
    keyboard_info = types.InlineKeyboardMarkup(keyboard_info_buttons)
    # Отправляем обычное сообщение, но третьм параметром указывается контейнер с кнопками, который должен отобразиться
    bot.send_message(message.from_user.id, "Ты хочешь узнать что-то о фильме или сериале?",
                     reply_markup=keyboard_info)


# Метод обработки команды latest
@bot.message_handler(commands=['latest', 'последний'])
def latest_func(message):
    # Создаём двумерный массив с кнопками
    # types.InlineKeyboardButton() создаёт одну кнопку, где text - то, что написано на кнопке для пользователя,
    # а callback_data - текстовый маркер, который указывает callback_query_handler'у какая кнопка была нажата и что надо сделать
    keyboard_latest_buttons = [[types.InlineKeyboardButton(text='Сериала', callback_data='latest_tv'),
                                types.InlineKeyboardButton(text='Фильма', callback_data='latest_movie')]]
    # Создаём InlineKeyboardMarkup из массива кнопок, это то, что будет отображаться. По сути контейнер с кнопками
    keyboard_latest = types.InlineKeyboardMarkup(keyboard_latest_buttons)
    # Отправляем обычное сообщение, но третьм параметром указывается контейнер с кнопками, который должен отобразиться
    bot.send_message(message.from_user.id, text="Ты хочешь узнать последний релиз фильма или сериала?",
                     reply_markup=keyboard_latest)


# Метод обработки команды top
@bot.message_handler(commands=['top', 'топ'])
def top_func(message):
    # Создаём двумерный массив с кнопками
    # types.InlineKeyboardButton() создаёт одну кнопку, где text - то, что написано на кнопке для пользователя,
    # а callback_data - текстовый маркер, который указывает callback_query_handler'у какая кнопка была нажата и что надо сделать
    keyboard_top_buttons = [[types.InlineKeyboardButton(text='Сериалов', callback_data='top_tv'),
                             types.InlineKeyboardButton(text='Фильмов', callback_data='top_movie')]]
    # Создаём InlineKeyboardMarkup из массива кнопок, это то, что будет отображаться. По сути контейнер с кнопками
    keyboard_top = types.InlineKeyboardMarkup(keyboard_top_buttons)
    # Отправляем обычное сообщение, но третьм параметром указывается контейнер с кнопками, который должен отобразиться
    bot.send_message(message.from_user.id, text="Тебе нужен топ фильмов или сериалов?",
                     reply_markup=keyboard_top)


# Метод обработки команды rating
@bot.message_handler(commands=['rating', 'рейтинг'])
def top_rated_func(message):
    # Создаём двумерный массив с кнопками
    # types.InlineKeyboardButton() создаёт одну кнопку, где text - то, что написано на кнопке для пользователя,
    # а callback_data - текстовый маркер, который указывает callback_query_handler'у какая кнопка была нажата и что надо сделать
    keyboard_top_buttons = [[types.InlineKeyboardButton(text='Сериалов', callback_data='top_rated_tv'),
                             types.InlineKeyboardButton(text='Фильмов', callback_data='top_rated_movie')]]
    # Создаём InlineKeyboardMarkup из массива кнопок, это то, что будет отображаться. По сути контейнер с кнопками
    keyboard_top = types.InlineKeyboardMarkup(keyboard_top_buttons)
    # Отправляем обычное сообщение, но третьм параметром указывается контейнер с кнопками, который должен отобразиться
    bot.send_message(message.from_user.id, text="Тебе нужен топ фильмов или сериалов?",
                     reply_markup=keyboard_top)


# Метод обработки команды recommend
@bot.message_handler(commands=['recommend', 'рекомендация'])
def recommend_func(message):
    # Создаём двумерный массив с кнопками
    # types.InlineKeyboardButton() создаёт одну кнопку, где text - то, что написано на кнопке для пользователя,
    # а callback_data - текстовый маркер, который указывает callback_query_handler'у какая кнопка была нажата и что надо сделать
    keyboard_recommend_buttons = [[types.InlineKeyboardButton(text='По сериалу', callback_data='recommend_tv'),
                                   types.InlineKeyboardButton(text='По фильму', callback_data='recommend_movie')]]
    # Создаём InlineKeyboardMarkup из массива кнопок, это то, что будет отображаться. По сути контейнер с кнопками
    keyboard_recommend = types.InlineKeyboardMarkup(keyboard_recommend_buttons)
    # Отправляем обычное сообщение, но третьм параметром указывается контейнер с кнопками, который должен отобразиться
    bot.send_message(message.from_user.id, text="Тебе нужна рекомендация по фильму или по сериалу?",
                     reply_markup=keyboard_recommend)


# Метод обработки команды watch
@bot.message_handler(commands=['watch', 'посмотреть'])
def watch_func(message):
    # Создаём двумерный массив с кнопками
    # types.InlineKeyboardButton() создаёт одну кнопку, где text - то, что написано на кнопке для пользователя,
    # а callback_data - текстовый маркер, который указывает callback_query_handler'у какая кнопка была нажата и что надо сделать
    keyboard_watch_buttons = [[types.InlineKeyboardButton(text='По сериалам', callback_data='watch_tv'),
                               types.InlineKeyboardButton(text='По фильмам', callback_data='watch_movie')],
                              [types.InlineKeyboardButton(text='Смешанная', callback_data='watch_mixed')]]
    # Создаём InlineKeyboardMarkup из массива кнопок, это то, что будет отображаться. По сути контейнер с кнопками
    keyboard_watch = types.InlineKeyboardMarkup(keyboard_watch_buttons)
    # Отправляем обычное сообщение, но третьм параметром указывается контейнер с кнопками, который должен отобразиться
    bot.send_message(message.from_user.id,
                     text="Тебе нужна рекомендация по фильмам, сериалам или смешанная рекомендация?",
                     reply_markup=keyboard_watch)


# Метод обработки команды developers
# Выводит информацию о "разработчиках", т.е. о вас, только внесите эту информацию сюда
@bot.message_handler(commands=['developers'])
def developers_func(message):
    # Отправляем обычное сообщение, поменяйте текст на тот, что нужен вам
    bot.send_message(message.from_user.id,
                     "Бот был разработан командой учащихся *название ВУЗа*: *перечисление всех причастных*.\n"
                     "Спасибо за использование (:")


# Метод обработки входящих сообщений (кроме команд, перечисленных выше)
# Реагирует на любой, даже не указанный отдельным условием текст
@bot.message_handler(content_types=['text'])
def text_reply(message):
    # "что посмотреть" запускает функцию /watch
    if message.text.lower() == 'что посмотреть' or message.text.lower() == 'что посмотреть?' or message.text.lower() == 'что посмотреть.':
        watch_func(message)
    # Если написать боту /start или "привет", он выведет приветственное письмо
    elif message.text.lower() == '/start' or message.text.lower() == 'привет':
        bot.send_message(message.from_user.id,
                         "Привет, я бот-киноман. Могу помочь тебе побольше узнать об известных фильмах и сериалах, "
                         "показать самые популярные кино-картины на сегодняшний день и порекомендовать что-нибудь к просмотру.\n"
                         "Чтобы побольше узнать о моих возможностях, напиши: /help или /помощь.")
    else:
        bot.send_message(message.from_user.id, "Если ты забыл, что я умею, напиши: /help.")


# Метод, который заставляет бота работать непрерывно и всё время слушать запросы пользователя
bot.polling(none_stop=True)
