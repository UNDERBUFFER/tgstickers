import os
import random
import shutil
import uuid
import zipfile

from aiogram.utils.exceptions import FileIsTooBig
from PIL import Image

from migration import *


def get_user(message, db=False, cursor=None):
    result = {
        'username': message.chat.username,
        'user_id': message.from_user.id,
        'stage': None,
        'pk': -1
    }
    if db is True:
        db_data = select_account(cursor, result['username'])
        result['pk'] = db_data[0]
        result['stage'] = db_data[3]
    return result


def get_file(message):
    return {
        'file_id': message.document.file_id,
        'file_name': message.document.file_name,
        'mime_type': message.document.mime_type
    }


def get_random_emoji():
    emojis = [
        '😀', '😁', '🤣', '😃',
        '😄', '😅', '😆', '😉',
        '😊', '😋', '😎', '😍',
        '😘', '😗', '👍', '😳'
    ]
    return random.choice(emojis)


async def set_file(bot, user, document, cursor):
    file = await bot.get_file(
        document['file_id']
    )
    file_path = file.file_path
    file_name = './tmp/{}-{}.zip'.format(
        os.path.splitext(document['file_name'])[0],
        str(uuid.uuid4())[0:8]
    )
    await bot.download_file(
        file_path,
        file_name
    )
    insert_file(cursor, file_name, user['pk'])


def unzip_file(file_path):
    out_dir = os.path.splitext(file_path)[0]
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(
            out_dir
        )

    title = os.listdir(out_dir)[0]
    out_dir = os.path.join(
        out_dir,
        title
    )

    images_paths = [os.path.join(
        out_dir, rel_path
    ) for rel_path in os.listdir(out_dir)]

    for image_path in  images_paths:
        im = Image.open(image_path)
        new_image = im.resize((512, 512))
        new_image.save(
            image_path,
            optimize=True,
            quality=85
        )

    return (title, images_paths)


async def set_sticker_set(bot, user, message, title, images_paths):
    name = 'ub2_{}_by_ub_stickers_bot'.format(
        str(uuid.uuid4())[0:8]
    )
    emoji = get_random_emoji()

    for index, image_path in enumerate(images_paths):
        try:
            await bot.create_new_sticker_set(
                user_id=user['user_id'],
                name=name,
                title=title,
                emojis=emoji,
                png_sticker=open(image_path, 'rb')
            )
            images_paths.pop(index)
            images_paths.insert(0, image_path)
            break
        except FileIsTooBig:
            pass
    else:
        await message.answer("No")
        return

    for image_path in images_paths[1:]:
        emoji = get_random_emoji()
        try:
            await bot.add_sticker_to_set(
                user_id=user['user_id'],
                name=name,
                emojis=emoji,
                png_sticker=open(image_path, 'rb')
            )
        except FileIsTooBig:
            pass

    sticker_set = await bot.get_sticker_set(
        name=name
    )
    file_id = sticker_set.stickers[0].file_id

    await bot.send_sticker(
        chat_id=message.chat.id,
        sticker=file_id
    )

    catalog = os.path.dirname(
        os.path.dirname(images_paths[0])
    )
    shutil.rmtree(catalog)
    os.remove('{}.zip'.format(catalog))

