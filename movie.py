# Этот класс нужен для хранения информации об отдельно взятом фильме/сериале в удобном виде
# Исходя из итератора (__init__) можно понять, что экземпляр класса хранит в себе:
# название картины, описание картины, её рейтинг на IMDb и ссылку на постер

class Movie:

    def __init__(self, title, description, rate, img):
        self.title = title
        self.description = description
        self.rate = rate
        self.img = img

    # Этот метод нужен для получения хранимой о фильме/сериале инфомации в читабельном виде
    def show_info(self):
        to_return = '«{title}» - {description}\n- Рейтинг: {rate}'
        return to_return.format(title=self.title, description=self.description, rate=self.rate, img=self.img)

    # Этот метод используется для получения ссылки на постер фильма/сериала
    def get_img_url(self):
        return self.img
