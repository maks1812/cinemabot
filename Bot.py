import aiohttp
import re
import logging
import typing as tp
from aiogram import Bot, Dispatcher, executor, types
from BotData import BotData

API_TOKEN = '1143813755:AAEymb7pO6-BRsSB_7DEOmE3SdzZQwYbQsw'
BASE_URL = 'https://www.ivi.ru'

HI_MESSAGE = 'Меня зовут cinemabot, и я помогу тебе в поиске фильма!\n Чтобы узнать, что я могу, введи /help'

HELP_MESSAGE = 'Чтобы я нашёл фильм для тебя, отправь мне сообщение в которм фильм выдели двойными кавычками\n \
Например: Найди "Властелин Колец".\n Также я могу дать тебе краткое описание фильма и подсказать  \
 ссылки для его просмотра. '

NOT_FOUND_MESSAGE = 'К сожалению такого фильма нет в моей базе. Но не расстраивайся,  фильм с таким \
названием обязательно когда-нибудь снимут и ты сможешь его посмотреть)\nА пока давай поищем что-нибудь другое!'

WRONG_REQUEST_MESSAGE = 'К сожалению пока я ещё не способен поддерживать беседу, но зато я могу искать фильмы!\n \
Введи название фильма в двойных кавычках чтобы я мог найти его.'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
cinemabot = BotData(base_url=BASE_URL, api_token=API_TOKEN)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message) -> None:
    """
        Process "\start" command: send some elcome phrase
        :param message: message object
        """
    name = message.from_user.first_name
    await message.answer(f"Привет {name}!\n {HI_MESSAGE}")


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message) -> None:
    """
    Process "\help" command: send to user some help info.
    :param message: message object
    """
    await message.answer(HELP_MESSAGE)


@dp.message_handler(commands=['description'])
async def process_description_command(message: types.Message) -> None:
    """
     Process "\help" command: send to user film description
     :param message: message object
    """
    await message.answer(f'Описание фильма {cinemabot._film_name}:\n {cinemabot._description}')


@dp.message_handler(commands=['all'])
async def process_all_command(message: types.Message) -> None:
    """
     Process "\all"  command: send to user all film urls
     :param message: message object
    """
    urls = "\n".join(cinemabot.give_urls())
    await message.answer(f'Все найденные ссылки для просмотра: {urls}')


@dp.message_handler()
async def search_film(message: types.Message) -> None:
    """
    Process film request.
    :param message: message object
    """
    if not cinemabot.find_film_name(message.text):
        await message.answer(WRONG_REQUEST_MESSAGE)
        return
    async with aiohttp.ClientSession() as session:
        async with session.get(cinemabot._base_url + '/search/', params={'q': cinemabot._film_name}) as resp:
            html = await resp.text()

        if not cinemabot.search_film(html):
            await message.answer(NOT_FOUND_MESSAGE)
            return
        async with session.get(cinemabot.give_urls(only_best=True)) as film_resp:
            html = await film_resp.text()
    cinemabot.search_info(html)
    await message.answer(f'Вот, что я нашёл:\n {cinemabot.give_film_info()} ')
    await message.answer('Если ты хочешь узнать об этом фильме подробнее напиши /description')
    if len(cinemabot._all_res) > 1:
        await message.answer('Да, ещё я нашёл другие варианты по твоему запросу.'
                             ' Если хочешь посмотреть их все, напиши /all')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
