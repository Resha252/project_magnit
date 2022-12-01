"""Парсер акционных товаров сети магазинов Магнит"""

#pip install bs4 selenium openpyxl pandas
#необходио скачать вебдрайвер для версии вашего браузера

import time                                               # для таймаута
import datetime
import pandas                                             # для записи данных в xlsx формат
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver                            # для запуска и выполнения действий в браузере
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options     # Опции селениума

opts = Options()
ua = UserAgent()
us_ag = ua.random    # регулярно меняет юзер-агенты
opts.add_argument(f"user-agent={us_ag}")

"""Следующие действия чтобы скрыть от сайта, что ты зашел на него при помощи Selenium"""
opts.add_experimental_option("excludeSwitches", ["enable-automation"])
opts.add_experimental_option('useAutomationExtension', False)
opts.add_argument("--disable-blink-features=AutomationControlled")

"""Функция сбора данных с кода загружаемой страницы"""
def collect_data(html):

    cur_time = datetime.datetime.now().strftime('%d_%m_%Y_%H_%M')

    soup = BeautifulSoup(html, 'html.parser')

    city = soup.find('a', class_='header__contacts-link_city').text.strip()
    cards = soup.find_all('a', class_='card-sale_catalogue')

    data_list = []

    for card in cards:
        card_title = card.find('div', class_='card-sale__title').text.strip()

        try:
            card_discount = card.find('div', class_='card-sale__discount').text.strip()
        except AttributeError:
            continue

        card_price_old_integer = card.find('div', class_='label__price_old').find('span', class_='label__price-integer').text.strip()
        card_price_old_decimal = card.find('div', class_='label__price_old').find('span', class_='label__price-decimal').text.strip()
        card_old_price = f'{card_price_old_integer}.{card_price_old_decimal}'

        card_price_integer = card.find('div', class_='label__price_new').find('span', class_='label__price-integer').text.strip()
        card_price_decimal = card.find('div', class_='label__price_new').find('span', class_='label__price-decimal').text.strip()
        card_price = f'{card_price_integer}.{card_price_decimal}'

        card_sale_date = card.find('div', class_='card-sale__date').text.strip().replace('\n', ' ')

        if card_title in data_list:    # Исключаем повторяющиеся позиции
            pass
        else:
            data_list.append({
                'Название': card_title,
                'Старая цена': card_old_price,
                'Цена со скидкой': card_price,
                'Размер скидки': card_discount,
                'Период акции': card_sale_date
            })

    print(f'{city}_{cur_time}. Данные загружены!')
    return data_list

"""Основная функция парсера, перемотка страницы до конца и считывание кода"""
def parser(url):
    #Указываем путь до драйвера и запускаем парсер
    driver = webdriver.Chrome(
        executable_path="/home/chromedriver",                                         #здесь необходимо указать путь до вебдрайвера
        options=opts
    )
    try:
        driver.get("https://magnit.ru/promo/")                                        # запускаем раоту драйвера
        time.sleep(2)                                                                 # время для загрузки страницы
        driver.maximize_window()                                                      # Разворачиваем окно браузера на полный экран
        last_height = driver.execute_script("return document.body.scrollHeight")      # Находим высоту прокрутки
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)            # Нажимаем PAGE_DOWN для прогрузки первого блока
        time.sleep(1)                      
        data_list_pages = []
        while True:
            data_list_pages.extend(collect_data(driver.page_source))                  #вызывая функцию collect_data парсит прогруженную страницу

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # прокручивает страницу вниз
            time.sleep(1)                                                             # время для загрузки страницы

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:                                             # Сравниваем высоту прокрутки с последней высотойй прокрутки
                print("Конец загрузки")
                break                                                                 # завершает прокрутку если дошли до конца страницы
            last_height = new_height
            print(f'Собрано {len(data_list_pages)} позиций')
        return data_list_pages

    except Exception as ex:
        print(f'Непредвиденная ошибка: {ex}')
        driver.close()
        driver.quit()                        #Завершает работу драйвера в случае непредвиденной ошибки
    driver.close()
    driver.quit()                            #Завершает работу драйвера

"""Функция сохранения полученных данных в файл формата xlsx"""
def save_exel(data):
    dataframe = pandas.DataFrame(data)
    writer = pandas.ExcelWriter(f'data_magnit.xlsx')
    dataframe.to_excel(writer, 'data_magnit')
    writer.save()
    print(f'Данные успешно загружены и сохранены в файл "data_magnit.xlsx"')


def main():
    print('Запуск парсера...')
    save_exel(parser(url='https://magnit.ru/promo/'))

if __name__ == '__main__':
    main()
