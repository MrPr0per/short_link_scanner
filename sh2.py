from threading import Thread
import requests
from fake_useragent import UserAgent
import random
import time
import datetime

# настройки (можно менять)
NUM_OF_RESULTS = 10  # после скольких находок остановить сканирование
NUM_OF_THREADS = 6  # количество потоков (если больше 3, то все после 3-го свалятся с err 429 (слишком много запросов))
domain = "https://clck.ru/"
n = 5  # кол-во символов после домена
max_len_url = 100  # максимальная длина выходной ссылки в html в символах

# константы (нельзя менять)
alpha = "0123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM"
header = {'User-Agent': str(UserAgent().chrome)}
black_list = [
    "ww82.hostingusa4you.com",
    "t2-blocked.com",
    "404.services/404",
    "goroskop.amurheart.com",
    "starcar.in",
    "hugedomains.com",
]

# глобальные переменные
all_results = []
count = 0  # количество записаных результатов


def gen_rand_url():
    url = domain
    for i in range(n):
        url += random.choice(alpha)
    return url


def cut_url(url):
    if len(url) > max_len_url:
        url = url[:max_len_url - 3] + '...'
    return url


def save_line(i: int, line: dict):
    """i - номер записываемой строки"""
    with open(f'results/result.html', 'a', encoding='UTF8') as file:

        if i % 10 == 0:
            file.write('<br>')
        if i == 0:
            file.write(f'<div class="dateTime">[{datetime.datetime.now().strftime("%Y-%b-%d %H:%M")}]</div>\n')

        file.write(f'<div class="line">')
        for k, v in line.items():
            if 'url' in k:
                file.write(
                    f'<a href="{v}" target="_blank"><span class="{k}">{cut_url(v)}</span></a>')
            else:
                file.write(f'<span class="{k}">{v}</span>')
        file.write(f'</div>\n')


def check_the_criteria(response):
    if response.status_code != 200: return False
    for domen in black_list:
        if domen in response.url: return False
    return True


def get_info(url):
    try:
        r = requests.get(url, headers=header, timeout=3)
        if check_the_criteria(r):
            result.append({'url short': url,
                           'code': r.status_code,
                           'url full': r.url, })  # ключ - css классы через пробел
        logs.append((url, r.status_code, r.url))
    except BaseException as e:
        # print('error:', e)
        pass


while count < NUM_OF_RESULTS:
    threads = []
    result = []
    logs = []  # то, что выводится в консоль (отдельные списки нужны, чтобы упорядочить параллельность)

    # получение данных
    t0 = time.time()
    for i in range(NUM_OF_THREADS):
        threads.append(Thread(target=get_info, args=(gen_rand_url(),)))
        threads[-1].start()
    for t in threads:
        t.join()

    # запись результатов
    for r in result:
        save_line(count, r)
        count += 1

    # вывод логов
    print(f'time: {time.time() - t0:.2f} s.')
    for r in logs:
        print(*r)
    print()
