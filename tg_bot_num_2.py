from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ContentType
from random import choice

# Вместо BOT TOKEN HERE нужно вставить токен вашего бота, полученный у @BotFather
BOT_TOKEN = '7537108602:AAF6_dm3QU6DXQR71uouxu7NClAarPbIkGM'

# Создаем объекты бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

videos_list = ["Хорошее видео", "Очень даже не дурно", "Я балдею бом бом", "Пофиг, я Мопс", "Обязательно скачаю"]
photo_list = ["Я это пожалуй сохраню", "Я польщён", "ААААААААААААААа, пиксели", "Фотографы тебе завидуют"]
sticker_list = ["О это же", "Му..Му..Муся, это т..т..ты? Нет, это", "АААААа, красавчик", "Пчёл :)", "Это маленький бибизян )", "Надо четки?", "Нормально всё говорю?"]

# Этот хэндлер будет срабатывать на команду "/start"
async def process_start_command(message: Message):
    await message.answer('Привет!\nМеня зовут Эхо-бот!\nНапиши мне что-нибудь')


# Этот хэндлер будет срабатывать на команду "/help"
async def process_help_command(message: Message):
    await message.answer(
        'Напиши мне что-нибудь и в ответ '
        'я пришлю тебе твое сообщение'
    )



async def send_photo(message: Message):
    await message.answer_photo(message.photo[0].file_id )
    await message.reply(f"{choice(photo_list)}")

async def send_video(message: Message):
    await message.answer_video(message.video.file_id)
    await message.reply(f"{choice(videos_list)}")

async def send_sticker(message:Message):
    await message.answer_sticker(message.sticker.file_id)
    s = choice(sticker_list)
    if s != "Пчёл :)":
        await message.reply(f"{s} {message.chat.username}")
    else:
        await message.reply(f"{message.chat.username} {s}")

async def send_audio(message: Message):
    await message.reply_audio(message.audio.file_id)

async def send_voice(message: Message):
    await message.reply_voice(message.voice.file_id)

async def send_animation(message: Message):
    await message.reply_animation(message.animation.file_id)

async def send_document(message: Message):
    await message.reply_document(message.document.file_id)

async def send_location(message: Message):
    await message.reply_location(message.location.longitude, message.location.latitude)

# Этот хэндлер будет срабатывать на любые ваши текстовые сообщения,
# кроме команд "/start" и "/help"
async def send_echo(message: Message):
    await message.reply(text=message.text)


dp.message.register(process_start_command, Command(commands='start'))
dp.message.register(process_help_command, Command(commands='help'))
dp.message.register(send_video, F.content_type == ContentType.VIDEO)
dp.message.register(send_photo, F.photo)
dp.message.register(send_sticker, F.sticker)
dp.message.register(send_audio, F.audio)
dp.message.register(send_voice, F.voice)
dp.message.register(send_animation, F.animation)
dp.message.register(send_document, F.document)
dp.message.register(send_location, F.location)
dp.message.register(send_echo)

if __name__ == '__main__':
    dp.run_polling(bot)