import logging
import os

from aiogram import Bot, Dispatcher, executor, types

from utils import *
from migration import *


API_TOKEN = os.getenv('API_TOKEN', '')


cursor = create_connection()
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    insert_account( cursor, **get_user(message) )
    await message.answer("Yes")


@dp.message_handler(commands=['send'])
async def register_to_pack(message: types.Message):
    user = get_user( message )
    update_account(
        cursor,
        user['username'],
        1
    )
    await message.answer("Ho-ho-ho")


@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def file_handle(message: types.Document):
    user = get_user(message, db=True, cursor=cursor)
    doc = get_file(message)
    if user['stage'] != 1 or doc['mime_type'] != 'application/zip':
        await message.answer("No")
        return

    await message.answer("Yes")
    await set_file(bot, user, doc, cursor)
    file_path = select_file(cursor, user['pk'])[1]
    await set_sticker_set(bot, user, message, *unzip_file(file_path))
    update_account(
        cursor,
        user['username'],
        0
    )


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

