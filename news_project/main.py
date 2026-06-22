#finder music from tiktok video and message from telegram
import asyncio
import logging
import os
import re
from typing import Optional

import aiohttp
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    BufferedInputFile,
    InputMediaPhoto,
    Message,
    URLInputFile,
)

# ──────────────────────────────────────────────
#  КОНФИГУРАЦИЯ
# ──────────────────────────────────────────────
BOT_TOKEN = "7537108602:AAF6_dm3QU6DXQR71uouxu7NClAarPbIkGM"   # <- вставьте токен от @BotFather

TIKWM_API = "https://www.tikwm.com/api/"
HEADERS = {"User-Agent": "TikTokBot/1.0"}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
#  УТИЛИТЫ
# ──────────────────────────────────────────────

def extract_tiktok_url(text: str) -> Optional[str]:
    """Извлекаем первую TikTok-ссылку из текста."""
    urls = re.findall(r"https?://[^\s]+", text)
    for url in urls:
        if "tiktok.com" in url:
            return url
    return None

async def resolve_short_url(url: str, session: aiohttp.ClientSession) -> str:
    """Разворачиваем короткие ссылки (vm.tiktok.com / vt.tiktok.com)."""
    try:
        async with session.head(url, allow_redirects=True, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            return str(resp.url)
    except Exception:
        return url


async def fetch_tiktok_info(url: str, session: aiohttp.ClientSession) -> Optional[dict]:
    """Запрашиваем данные о посте через TikWM API."""
    try:
        params = {"url": url, "hd": 1}
        async with session.post(TIKWM_API, data=params, timeout=aiohttp.ClientTimeout(total=30)) as resp:
            data = await resp.json(content_type=None)
        if data.get("code") == 0 and data.get("data"):
            return data["data"]
    except Exception as e:
        logger.error("TikWM API error: %s", e)
    return None


async def download_bytes(url: str, session: aiohttp.ClientSession) -> Optional[bytes]:
    """Скачиваем файл в память."""
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=60)) as resp:
            if resp.status == 200:
                return await resp.read()
    except Exception as e:
        logger.error("Download error: %s", e)
    return None


# ──────────────────────────────────────────────
#  HANDLERS
# ──────────────────────────────────────────────
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "👋 <b>Привет!</b> Я умею скачивать видео и фото из TikTok без водяного знака.\n\n"
        "📌 <b>Как использовать:</b>\n"
        "Просто отправь мне ссылку на видео или фото-карусель TikTok\n\n"
        "🔗 <b>Поддерживаемые форматы:</b>\n"
        "• <code>https://www.tiktok.com/@user/video/123</code>\n"
        "• <code>https://vm.tiktok.com/XXXXXXX</code>\n"
        "• <code>https://vt.tiktok.com/XXXXXXX</code>\n"
        "• <code>https://www.tiktok.com/@user/photo/123</code>\n\n"
        "✅ Видео скачиваются <b>без водяного знака</b> в HD-качестве!",
        parse_mode="HTML",
    )


@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "ℹ️ <b>Помощь</b>\n\n"
        "Отправь ссылку на TikTok-видео или пост с фото — я автоматически определю тип контента и пришлю медиафайл.\n\n"
        "<b>Команды:</b>\n"
        "/start — приветственное сообщение\n"
        "/help — эта справка",
        parse_mode="HTML",
    )


@dp.message(F.text)
async def handle_message(message: Message):
    url = extract_tiktok_url(message.text or "")
    if not url:
        await message.answer(
            "⚠️ Пожалуйста, отправь <b>ссылку на TikTok</b>.",
            parse_mode="HTML",
        )
        return

    status_msg = await message.answer("⏳ Загружаю данные...")

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        # Разворачиваем короткую ссылку если нужно
        if any(d in url for d in ["vm.tiktok.com", "vt.tiktok.com", "m.tiktok.com"]):
            url = await resolve_short_url(url, session)

        info = await fetch_tiktok_info(url, session)

    if not info:
        await status_msg.edit_text("❌ Не удалось получить информацию о посте. Проверь ссылку.")
        return

    author = info.get("author", {})
    desc = info.get("title", "")[:800]
    nickname = author.get("nickname", "")
    unique_id = author.get("unique_id", "")
    is_image = info.get("images")          # фото-карусель
    caption = (
        f"👤 <b>{nickname}</b> (@{unique_id})\n"
        + (f"📝 {desc}\n" if desc else "")
        + f"\n🔗 <a href=\"{url}\">Открыть в TikTok</a>"
    )

    await status_msg.edit_text("⏬ Скачиваю медиафайл...")

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        # ── ФОТО-КАРУСЕЛЬ ──────────────────────────────────
        if is_image:
            images = info["images"]          # список URL картинок
            media_group = []
            for idx, img_url in enumerate(images[:10]):  # TG лимит — 10
                img_bytes = await download_bytes(img_url, session)
                if img_bytes:
                    buf = BufferedInputFile(img_bytes, filename=f"photo_{idx+1}.jpg")
                    if idx == 0:
                        media_group.append(InputMediaPhoto(media=buf, caption=caption, parse_mode="HTML"))
                    else:
                        media_group.append(InputMediaPhoto(media=buf))

            if media_group:
                await status_msg.delete()
                await message.answer_media_group(media=media_group)
            else:
                await status_msg.edit_text("❌ Не удалось скачать фото.")

        # ── ВИДЕО ─────────────────────────────────────────
        else:
            # Пробуем HD, потом обычное, потом с водяным знаком
            video_url = (
                info.get("hdplay")
                or info.get("play")
                or info.get("wmplay")
            )
            if not video_url:
                await status_msg.edit_text("❌ URL видео не найден.")
                return

            video_bytes = await download_bytes(video_url, session)

            if video_bytes and len(video_bytes) < 50 * 1024 * 1024:  # < 50 МБ
                buf = BufferedInputFile(video_bytes, filename="tiktok_video.mp4")
                await status_msg.delete()
                await message.answer_video(
                    video=buf,
                    caption=caption,
                    parse_mode="HTML",
                    supports_streaming=True,
                )
            elif video_url:
                # Fallback — отправляем по URL (работает если TG может достучаться)
                await status_msg.delete()
                await message.answer_video(
                    video=URLInputFile(video_url, filename="tiktok_video.mp4"),
                    caption=caption,
                    parse_mode="HTML",
                    supports_streaming=True,
                )
            else:
                await status_msg.edit_text("❌ Не удалось скачать видео.")


# ──────────────────────────────────────────────
#  ЗАПУСК
# ──────────────────────────────────────────────
async def main():
    logger.info("Бот запущен!")
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())