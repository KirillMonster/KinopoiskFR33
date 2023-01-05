from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import requests
from bs4 import BeautifulSoup

TOKEN = 'TOKEN'
PLAYER_URL = 'https://kirlovon.dev/Kinopoisk-Watch/?id='

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

HEADERS = {'User-Agent': 'Your User Agent'}


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await bot.send_message(message.chat.id, f'''
👋 Привет, {message.from_user.mention}
🆓 Это бесплатный Kinopoisk
🔎 Чтобы найти нужный вам фильм нужно написать:
🎥 /kino название фильма или ссылка на него

📋 Пример:
🎥 /kino Волк с Уолл-стрит

💲 Поддержать - /donate

👨‍💻 Разработчик - /coder''')


@dp.message_handler(commands=['kino'])
async def kino(message: types.Message):
    text = ' '.join(message.text.strip().split()[1:])
    keyboard = InlineKeyboardMarkup()
    if text == '':
        return await bot.send_message(message.chat.id, '🎥 Укажите название или ссылку на фильм')
    if text.startswith('https://www.kinopoisk.ru/film/'):
        film_id = text.replace('https://www.kinopoisk.ru/film/', '').replace('/', '')
        keyboard.add(InlineKeyboardButton('👁‍🗨 Смотреть', url=PLAYER_URL + film_id))
        return await bot.send_message(message.chat.id,
                               f'🍿 Готовь попкорн!\n🎥 Держи фильм:', reply_markup=keyboard)

    response = requests.get(f'https://www.kinopoisk.ru/index.php?kp_query={text}', headers=HEADERS)
    soup = BeautifulSoup(response.text, 'lxml')

    count = 0

    film_most = soup.find('div', class_='element most_wanted')
    if film_most is None:
        msg = '''
🔗 Попробуй указать на него ссылку с Kinopisk

Пример:
/kino https://www.kinopoisk.ru/film/462682
'''
        if 'https://captcha-backgrounds.s3.yandex.net/static/kinopoisk-background.jpg' in response.text:
            return await bot.send_message(message.chat.id, '😔 Наткнулся на капчу.\n' + msg)
        return await bot.send_message(message.chat.id, '😔 Я не нашёл фильм с таким названием.\n' + msg)

    
    for element in soup.find_all('div', class_='search_results'):
        e = element.find('p', class_='header').find('a')
        if e is not None:
            if 'имена' in e.get_text(strip=True):
                break

        for film in element.find_all('div', class_='element'):
            count += 1
            film_rating = film.find('div', class_='right').find('div')
            film_rating = '0' if film_rating is None else film_rating.get_text(strip=True)
            film = film.find('p', class_='name')
            film_name = film.find('a').get_text(strip=True)
            film_id = film.find('a').get('data-id')
            keyboard.add(InlineKeyboardButton(text=f'{film_name} | {film_rating}⭐', url=PLAYER_URL + film_id))

    await bot.send_message(message.chat.id, f'🍿 Готовь попкорн!\n🎥 Я нашёл для тебя фильм{"ы" if count > 1 else ""}:', reply_markup=keyboard)


@dp.message_handler(commands=['donate'])
async def donate(message: types.Message):
    await bot.send_message(message.chat.id, '💳 Карта Тинькофф - 2200 7004 6754 1347 (Кирилл. И)')

@dp.message_handler(commands=['coder'])
async def coder(message: types.Message):
    await bot.send_message(message.chat.id, '''👨‍💻 Кодер этого бота - @Kirill_Monster
📋 И его проекты не забудь посмотреть - @kirill_monster_projects''')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
