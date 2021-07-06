import random
# Библиотека для генерации случаных событий (в данном случае используется для генерации случайных значений int)
import requests
# Библиотека для реализации запросов http (соединение с web-серверами). В данном случае исп. для парсинга информации
# с IMDb и вставки картинок
from queue import Queue
# Библиотека с "очередью" (тип хранения данных - queue: первый вошёл, первый вышел)
from movie import Movie
# Импорт из файла movie.py (написанный для этого таска) класса Movie

# Ключ для доступа к IMDb API (для разработчиков, получается индивидуально, надо регистрироваться на сайте IMDb)
# В отдельную строку вынесено, чтобы можно было изменить ключ без изменения ВСЕГО дальнейшего кода
WEB_KEY = 'ab2a7be8e975a7295709a5c39b086fdf'
# Общий вид ссылки для осуществления запросов к IMDb API, для парсинга информации
WEB_URL = 'https://api.themoviedb.org/3/{type}/{modifier}?api_key={key}&language={language}&page={page}'
# Тоже ссылка для парсинга с IMDb, но немного видоизменённая для запроса поиска информации по конкретному названию фильма/сериала
# Введена новая переменная, т.к. ссылка немного отличается по структуре от WEB_URL
WEB_URL_SEARCH = 'https://api.themoviedb.org/3/search/{type}?api_key={key}&language={language}&query={name}'
# Ссылка для скачивания изображения с сайта IMDb
WEB_IMG_URL = 'https://image.tmdb.org/t/p/w500/{img}'

# Указатель на русский язык получаемого контента для парсинга
# Вставляется в строку с URL-запросом по ключу, чтобы контент выходил на русском языке
# В отдельную переменную вынесено, чтобы можно было добавить новые и использовать для доступа на другом языке (если понадобится)
WEB_LANGUAGE_RU = 'ru-RU'

# Далее идут модификаторы, которые используются как составная часть ссылки
# В отдельные переменные вынесены, чтобы можно было добавить новые модули и использовать (если понадобится)
# TYPE_MOVIE - для запросов к фильмам, TYPE_TV - запросы к сериалам. На IMDb они имеют разные базы данных, поэтому
# обращение к ним тоже по-разному
WEB_TYPE_MOVIE = 'movie'
WEB_TYPE_TV = 'tv'
# Модуль для доступа к списку популярных (на данный момент по просмотрам среди пользователей) сериалов/фильмов
WEB_MODIFIER_POPULAR = 'popular'
# Модуль для доступа к списку наиболее высоко оценённых фильмам/сериалам
WEB_MODIFIER_TOP_RATED = 'top_rated'
# Модуль для доступа к списку рекомендованных фильмов/сериалов (рекомендации выстраиваются по конкретному фильму)
# То есть, пользователь может получить рекомендации "похожих" фильмов, указав фильм-корень (по которому строится рекомендация)
WEB_MODIFIER_RECOMMENDATIONS = '/recommendations'
# Модуль для доступа к последнему релизу сериала/фильма (выдаёт очень кринжовые варианты, т.к. почти каждые 5 минут
# условный болливуд размещает новый никому неизвестный фильм, а отфильтровать это никак нельзя, но для массы пусть будет)
WEB_MODIFIER_LATEST = 'latest'

# Типовые сообщения об ошибках, без комментариев
ERR_INTERNET = 'Проблемы с интернет-соединением c сайтом-источником, попробуй попозже (:'
ERR_TITLE = 'Неправильно указано название или тип фильма(поменяй на сериал/фильм), попробуй ещё раз (:'
ERR_COMMAND = 'Неправильно набрана команда, попробуй ещё раз (:'
ERR_SMT = 'Что-то пошло не так, попробуй ещё раз (:'

# Переменная типа "очередь", в которую добавляются экземпляры класса Movie, который в свою очередь хранит информацию о фильме/сериале.
# Очередь универсально используется для вывода информации по запросам: будь в ней 0 элементов, 1 или 100
# Подробнее об использовании очереди для вывода в классе main, функция print_request_result()
movies_to_be_shown = Queue()

# Это сообщение хранит в себе последнюю ошибку, которая будет выведена пользователю в случае, собственно, ошибки (:
err_msg = 'Что-то пошло не так, попробуй снова :с'

# Этот метод написан для тестирования логики в консоли
# Выводит информацию о добавленных в очередь "фильмах", экземплярах класса Movie. Можно удалять
# def print_result():
#     global movies_to_be_shown
#     if movies_to_be_shown.qsize() != 0:
#         while movies_to_be_shown.qsize() != 0:
#             next_movie = movies_to_be_shown.get()
#             print(next_movie.show_info())
#             print('----------==========----------')
#     else:
#         print(err_msg)


# Метод для получения информации о фильме/сериале по его названию
def get_info(series_name, series_type):
    # Объявляется доступ к переменной err_msg, чтобы в случае ошибки присвоить новый текст об ошибке
    global err_msg
    # Поскольку название фильма/сериала может содержать несколько слов, в переменной с именем все пробелы заменяются на "+"
    # Почему именно на +? Потому что в запросе к IMDb, если название состоит из нескольких слов, они должны быть разделены именно +'ом
    series_name = '+'.join(series_name.split())
    # Модуль try - except для "ловли" исключений, например, если отсутствует интернет или сайт IMDb упал
    # Если бы не было try - except, прога бы просто "падала", но в таком случае вместо краша выполняется модуль except, модуль try не выполняется
    # Программа работает дальше
    try:
        # В переменную response записывается объект в формате "карты" (ака. массив с доступом к элементам по ключам,
        # полученный через метод request.get(url). Полученная карта существует в формате большого количества вложенных в неё других карт (а в них ещё других)
        # Метод .get(url) получает (парсит) информацию с сайта по заданной ему ссылке, после чего переводит её в формат "карты" (map) (конкретно json, методом .json())
        # Ссылка (url) для этого метода задаётся как конструктор из переменных, указанных в начале программы
        # В WEB_URL_SEARCH есть "ключи", указанные в {}. С помощью метода String.format() ключам присваиваются значения (строковые)
        response = requests.get(
            WEB_URL_SEARCH.format(type=series_type, key=WEB_KEY, language=WEB_LANGUAGE_RU, name=series_name)).json()
        # В переменную results получаем ещё одну мапу (карту) по ключу 'results'
        results = response['results']
        # Проверка на то, что мы получили искомые данные по запросу и в карте results есть какие-то данные (т.е. размер не равен нулю)
        # Если данных в карте нет, присваивается новое значение ошибки и метод завершается
        if len(results) != 0:

            # У сериалов и фильмов в массивах данных IMDb разные ключи доступа, поэтому в зависимости от того, скачиваем мы
            # информацию о сериале или фильме, меняется ключ для доступа к названию
            # Для сериала - name, для фильма - title (имхо API для IMDb писали какие-то ебланы)
            title_key = 'title'
            if series_type == WEB_TYPE_TV:
                title_key = 'name'

            # Получаем первый карту данных искомого фильма: их может быть несколько, например, если по искомому названию несколько фильмов
            # Первое совпадение всегда наиболее вероятное, поэтому смысла показывать остальные - нет
            main = results[0]

            # Получаем из мапы фильма/сериала необходимую информацию, опять же, по ключам. title - название на русском (если локализовано)
            # description - описание фильма, rate - рейтинг на сайте IMDb, img - ссылка на постер фильма (если есть) (её потом надо соединить
            # с ссылкой WEB_IMG_URL, чтобы получить на выходе именно картинку
            title = main[title_key]
            description = main['overview']
            rate = main['vote_average']
            img = main['poster_path']
            # Полученную информацию записываем в анонимный экземпляр класса Movie и сразу засовываем его в "очередь"
            movies_to_be_shown.put(Movie(title, description, rate, img))
        else:
            err_msg = ERR_TITLE
    except ConnectionError:
        err_msg = ERR_INTERNET


# Метод для получения информации о топ-просматриваемых и наиболее высоко оценённых сериалах/фильмах
def get_with_modifier(series_type, series_modifier):
    # Искуственное ограничение на количество выводимых фильмах, т.к. при большом количестве начинает тормозить процесс загрузки
    # Это питон, за его лёгкость приходится платить медленностью работы
    series_amount = 7
    global err_msg
    try:
        # Запрос как и в get_info(), но по другой ссылке. Принцип тот же: скачиваем карту с картами с картами (:
        response = requests.get(
            WEB_URL.format(type=series_type, modifier=series_modifier, key=WEB_KEY, language=WEB_LANGUAGE_RU,
                           page=1)).json()
        results = response['results']

        title_key = 'title'
        if series_type == WEB_TYPE_TV:
            title_key = 'name'

        # Поскольку в этой функции нам уже надо получить информацию о нескольких фильмах за раз, они проходятся в цикле
        # В целом принцип тот же, что и в get_info(), просто теперь доступ идёт к элементам от 0 до 7 включительно (всего 8 шт)
        # Получаем информацию об одном, создаём анонимный экземпляр класса Movie и сразу отправляем его в очередь
        for i in range(0, series_amount):
            main = results[i]
            title = main[title_key]
            description = main['overview']
            rate = main['vote_average']
            img = main['poster_path']
            movies_to_be_shown.put(Movie(title, description, rate, img))
    except ConnectionError:
        err_msg = ERR_INTERNET


# Вспомогательная функция для получения id фильма по его названию. id нужен для рекомендации похожих фильмов
def get_id(series_type, series_name):
    # Переменная series_id будет возвращена в конце работы функции. Если значение не будет изменено в силу
    # каких-либо ошибок (не нашлось такого фильма, например), то значение -100 вызовет ошибку в следующем методе и
    # это в свою очередь приведёт к выведению ошибки пользователю, программа не сломается
    series_id = -100
    global err_msg
    series_name = '+'.join(series_name.split())
    try:
        # Опять получаем данные об искомом фильме, но в этот раз нас интересует только id, в очередь ничего не добавляем
        response = requests.get(
            WEB_URL_SEARCH.format(type=series_type, key=WEB_KEY, language=WEB_LANGUAGE_RU, name=series_name)).json()
        results = response['results']
        if len(results) != 0:
            # Если искомый фильм существует, назначаем его id в переменную series_id, после чего она будет возвращена
            main = results[0]
            series_id = main['id']
        else:
            err_msg = ERR_TITLE
    except ConnectionError:
        err_msg = ERR_INTERNET
    return series_id


# Метод для получения последнего релиза сериала/фильма, всё как в get_with_modifier, только получаем другие поля
def get_latest_release(series_type):
    global err_msg
    try:
        response = requests.get(
            WEB_URL.format(type=series_type, modifier=WEB_MODIFIER_LATEST, key=WEB_KEY, language=WEB_LANGUAGE_RU,
                           page=1)).json()

        # В этот раз от типа (сериал/фильм) зависит уже 2 поля, поэтому release_key и title_key меняются в зависимости от искомого типа
        title_key = 'title'
        release_key = 'release_date'
        if series_type == WEB_TYPE_TV:
            title_key = 'name'
            release_key = 'last_air_date'
            # Если фильм уже вышел в "прокат", в карте у него не будет даты релиза, поэтому в таком случае
            # целесообразнее получить статус "выпущен", чем пустое поле даты релиза
        if str(response['status']).lower() == 'released':
            release_key = 'status'

        # Получаем информацию о фильме/сериале и записываем её в аномнимный экземпляр класса Movie, добавляем его в очередь
        # Последний релиз всегда один (так решило API IMDb, поэтому никаких циклов)
        title = response[title_key]
        description = 'Дата релиза: ' + response[release_key]
        rate = response['vote_average']
        img = response['poster_path']
        movies_to_be_shown.put(Movie(title, description, rate, img))
    except ConnectionError:
        err_msg = ERR_INTERNET


# Функция, которая рекомендует пользователю "похожие" фильмы, основываясь на заданном им фильме-якоре
def make_recommendations_to_watch(series_type, series_name):
    global err_msg
    try:
        # Получаем id фильма-якоря (для которого ищем похожие фильмы) по его названию, для этого была функция get_id
        # Напомню, она просто возвращает полученный id фильма/сериала
        series_id = get_id(series_type, series_name)
        # Если id фильма найден не был (например, неправильно указано название), то выдаётся ошибка (программа при это продолжает работать)
        if series_id != -100:
            # Видоизменяем модификатор для ссылки, т.к. в начале требуется указывать id фильма, а потом уже модификатор
            series_modifier = str(series_id) + '' + WEB_MODIFIER_RECOMMENDATIONS

            # Опять типичный запрос по ссылке, вставляем ключи в ссылку и получаем очередную карту с картами с картами
            response = requests.get(
                WEB_URL.format(type=series_type, modifier=series_modifier, key=WEB_KEY,
                               language=WEB_LANGUAGE_RU, page=1)).json()
            results = response['results']

            # Искуственно ограничиваем количество выводимых фильмов, т.к., опять же, слишком большое количество ведёт к увеличению времени работы
            # Так же не забываем, что может быть ситуация, когда рекомендуемых фильмов ещё меньше заданного нами ограничения
            # Поэтому надо проверить этот момент и, если фильмов меньше 5, переменная получает новое значение
            end_point = 5
            if len(results) < 5:
                end_point = len(results)

            # Код выполняется, если есть хотя бы один фильм для рекомендации, иначе пользователь видит ошибку
            if end_point != 0:

                # Опять меняем ключ в зависимости от того, что нам надо: сериал или фильм
                title_key = 'title'
                if series_type == WEB_TYPE_TV:
                    title_key = 'name'

                # Поскольку фильмов может быть больше 1го, проходим их в цикле
                # Полученные значения записываем в анонимный экземпляр класса Movie и отправляем сразу в очередь
                for i in range(0, end_point):
                    main = results[i]
                    title = main[title_key]
                    description = main['overview']
                    rate = main['vote_average']
                    img = main['poster_path']
                    movies_to_be_shown.put(Movie(title, description, rate, img))
                else:
                    err_msg = ERR_TITLE
        else:
            err_msg = ERR_TITLE
    except ConnectionError:
        err_msg = ERR_INTERNET
    return 1


# Функция, которая генерирует 5 случайных фильмов или сериалов для просмотра пользователю из наиболее популярных
# Эта функция как раз содержит в себе логику, что необходимо на 8+ баллов по требованиям
# В качестве аргумента получает тип (только фильмы/только сериалы/смешанный)
def make_series_to_watch(combine_type):
    global err_msg
    # Создаём очередь из типов запрашиваемых картин (сериалы или фильмы), это необходимо для реализации комбинированного режима
    type_queue = Queue()

    # Если требуются только сериалы, очередь заполняется 5ю типами WEB_TYPE_TV (условие == 0)
    if combine_type == 0:
        for i in range(5):
            type_queue.put(WEB_TYPE_TV)
    # Если требуются только фильмы, очередь заполняется 5ю типами WEB_TYPE_MOVIE (условие == 1)
    elif combine_type == 1:
        for i in range(5):
            type_queue.put(WEB_TYPE_MOVIE)
    # Если же необходим комбинированный тип, очередь в случайном порядке генерирует 5 типов (условие ==2)
    else:
        for i in range(0, 5):
            # Генерируется случайное целое число, если оно чётное, то в очередь добавляется сериал, если нечётное, то фильм
            rnd_series_type = random.randint(1, 10)
            if (rnd_series_type % 2) == 0:
                type_queue.put(WEB_TYPE_TV)
            else:
                type_queue.put(WEB_TYPE_MOVIE)

    # Проходим по засунутым в очередь типам (сериал/фильм). Ссылка меняется каждую итерацию цикла, т.к. метод .get() у очереди
    # не только возвращает запрашиваемый элемент, но и удаляет его из очереди
    for i in range(5):
        # Генерируем случайную страницу от 1 до 200 для ссылки
        rnd_page = random.randint(1, 200)

        try:
            series_type = type_queue.get()

            # Запрос-конструктор, которые уже были
            response = requests.get(
                WEB_URL.format(type=series_type, modifier=WEB_MODIFIER_POPULAR, key=WEB_KEY, language=WEB_LANGUAGE_RU,
                               page=rnd_page)).json()
            results = response['results']

            # Проверка на наличие элементов
            if len(results) != 0:
                # Генерируем случайный фильм (на каждой странице их по 20 штук, т.е. от 0 до 19 или меньше (если страница последняя))
                rnd_number = random.randint(0, len(results) - 1)

                # Опять меняем ключ для карты в зависимости от типа картины (сериал/фильм)
                title_key = 'title'
                if series_type == WEB_TYPE_TV:
                    title_key = 'name'

                # Получаем карту искомого фильма (по случайному числу, сгенерированному ранее)
                # Записываем все полученные поля в анонимный экземпляр класса Movie и отправляем его в очередь
                main = results[rnd_number]
                title = main[title_key]
                description = main['overview']
                rate = main['vote_average']
                img = main['poster_path']
                movies_to_be_shown.put(Movie(title, description, rate, img))
            else:
                err_msg = ERR_SMT
        except ConnectionError:
            err_msg = ERR_INTERNET


# Этот метод так же написан для теста логики в консоли. Можно удалить
# Если есть нужна им воспользоваться, раскомментируй его (выдели весь код и нажми Ctrl + / на английской раскладке)
# Так же для работы необходим метод print_result() (он в самом начале)
# print('Введите запрос:')
# request = input()
#
# while request != 'стоп' or request != 'Стоп':
#     request = request.lower()
#     if request == 'фильм':
#         print('Введите название искомого фильма')
#         name = input().lower()
#
#         get_info(name, WEB_TYPE_MOVIE)
#         print_result()
#     elif request == 'сериал':
#         print('Введите название искомого сериала')
#         name = input().lower()
#
#         get_info(name, WEB_TYPE_TV)
#         print_result()
#     elif request == 'топ фильмы':
#         print('Введите количество желаемого топа (от 3 до 20)')
#         amount = int(input())
#
#         get_with_modifier(WEB_TYPE_MOVIE, WEB_MODIFIER_POPULAR, amount)
#         print_result()
#     elif request == 'топ сериалы':
#         print('Введите количество желаемого топа (от 3 до 20)')
#         amount = int(input())
#
#         get_with_modifier(WEB_TYPE_TV, WEB_MODIFIER_POPULAR, amount)
#         print_result()
#     elif request == 'рейтинг фильмы':
#         print('Введите количество желаемого топа (от 3 до 20)')
#         amount = int(input())
#
#         get_with_modifier(WEB_TYPE_MOVIE, WEB_MODIFIER_TOP_RATED, amount)
#         print_result()
#     elif request == 'рейтинг сериалы':
#         print('Введите количество желаемого топа (от 3 до 20)')
#         amount = int(input())
#
#         get_with_modifier(WEB_TYPE_TV, WEB_MODIFIER_TOP_RATED, amount)
#         print_result()
#     elif request == 'что посмотреть':
#         print('Сериалы/Фильмы/Смешанные:')
#         series_type_to_send = input().lower()
#
#         if series_type_to_send == 'сериалы':
#             series_num_to_send = 0
#             make_series_to_watch(series_num_to_send)
#             print_result()
#         elif series_type_to_send == 'фильмы':
#             series_num_to_send = 1
#             make_series_to_watch(series_num_to_send)
#             print_result()
#         elif series_type_to_send == 'смешанные':
#             series_num_to_send = 2
#             make_series_to_watch(series_num_to_send)
#             print_result()
#         else:
#             print('Неправильно написан тип желаемого контента, попробуйте ещё раз (:')
#     elif request == 'рекомендация':
#         print('Сериал/Фильм:')
#         series_type_to_enter = input().lower()
#
#         if series_type_to_enter == 'сериал':
#             print('Введите название любимого сериала:')
#             series_name_to_send = input().lower()
#
#             make_recommendations_to_watch(WEB_TYPE_TV, series_name_to_send)
#             print_result()
#         elif series_type_to_enter == 'фильм':
#             print('Введите название любимого фильма:')
#             series_name_to_send = input().lower()
#
#             make_recommendations_to_watch(WEB_TYPE_MOVIE, series_name_to_send)
#             print_result()
#         else:
#             print('Неправильно написан тип желаемого контента, попробуйте ещё раз (:')
#     elif request == 'релиз':
#         print('Сериал/Фильм:')
#         series_type_to_enter = input().lower()
#
#         if series_type_to_enter == 'сериал':
#             get_latest_release(WEB_TYPE_TV)
#             print_result()
#         elif series_type_to_enter == 'фильм':
#             get_latest_release(WEB_TYPE_MOVIE)
#             print_result()
#         else:
#             print('Неправильно написан тип желаемого контента, попробуйте ещё раз (:')
#     else:
#         print('Такой команды мы не знаем (:')
#     print('Введите новый запрос:')
#     request = input()
#
# print('Программа завершила работу')
