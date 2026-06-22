import asyncio
import glob
import logging
import os
import re
import tempfile
from dataclasses import dataclass
from typing import Optional

import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from yt_dlp import YoutubeDL


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("music-bot")


TIKTOK_URL_RE = re.compile(
    r"(https?://(?:www\.)?(?:vm|vt|m)\.tiktok\.com/[^\s]+|"
    r"https?://(?:www\.)?tiktok\.com/[^\s]+)",
    re.IGNORECASE,
)


class BotError(Exception):
    pass


class RecognitionError(BotError):
    pass


class DownloadError(BotError):
    pass


class TrackNotFoundError(BotError):
    pass


@dataclass
class TrackInfo:
    title: str
    artist: str


def extract_tiktok_url(text: str) -> Optional[str]:
    match = TIKTOK_URL_RE.search(text or "")
    if not match:
        return None
    return match.group(1).rstrip(".,)")


def _safe_audio_path(base_filename: str, output_dir: str) -> Optional[str]:
    stem = os.path.splitext(os.path.basename(base_filename))[0]
    expected = os.path.join(output_dir, f"{stem}.mp3")
    if os.path.exists(expected):
        return expected

    mp3_files = sorted(glob.glob(os.path.join(output_dir, "*.mp3")), key=os.path.getmtime)
    return mp3_files[-1] if mp3_files else None


def download_audio_from_url(url: str, output_dir: str) -> str:
    logger.info("Downloading audio from URL: %s", url)
    outtmpl = os.path.join(output_dir, "%(title).80s-%(id)s.%(ext)s")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": outtmpl,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            prepared = ydl.prepare_filename(info)
        audio_path = _safe_audio_path(prepared, output_dir)
        if not audio_path:
            raise DownloadError("Failed to locate downloaded MP3 file")
        return audio_path
    except Exception as exc:
        raise DownloadError(f"Unable to download audio: {exc}") from exc


import subprocess

def make_snippet(input_audio_path: str, snippet_path: str, snippet_ms: int = 15000) -> str:
    """
    Обрезает первые snippet_ms миллисекунд из input_audio_path,
    сохраняет как MP3 в snippet_path, используя ffmpeg.
    """
    # ffmpeg принимает длительность в секундах
    snippet_sec = snippet_ms / 1000.0
    cmd = [
        "ffmpeg",
        "-i", input_audio_path,      # входной файл
        "-t", str(snippet_sec),      # длительность обрезки (первые N секунд)
        "-acodec", "mp3",            # выходной кодек (MP3)
        "-y",                        # перезаписывать без запроса
        snippet_path
    ]
    logger.info("Running ffmpeg: %s", " ".join(cmd))
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        raise RecognitionError(f"ffmpeg failed: {e.stderr}") from e
    return snippet_path


def recognize_with_audd(snippet_path: str, token: str) -> TrackInfo:
    logger.info("Recognizing audio via AudD")
    url = "https://api.audd.io/"
    with open(snippet_path, "rb") as f:
        response = requests.post(
            url,
            data={"api_token": token, "return": "spotify,apple_music"},
            files={"file": f},
            timeout=60,
        )

    if response.status_code != 200:
        raise RecognitionError(f"AudD HTTP error: {response.status_code}")

    payload = response.json()
    if payload.get("status") != "success":
        raise RecognitionError(f"AudD error: {payload.get('error')}")

    result = payload.get("result")
    if not result:
        raise RecognitionError("Track not recognized")

    title = (result.get("title") or "").strip()
    artist = (result.get("artist") or "").strip()
    if not title or not artist:
        raise RecognitionError("AudD returned incomplete track info")

    logger.info("Recognized: %s - %s", artist, title)
    return TrackInfo(title=title, artist=artist)


def search_track_url(query: str) -> Optional[str]:
    logger.info("Searching track: %s", query)
    search_patterns = ["ytsearch5", "scsearch5"]

    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "noplaylist": True,
        "no_warnings": True,
    }

    for pattern in search_patterns:
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"{pattern}:{query}", download=False)
            for entry in info.get("entries", []) or []:
                if not entry:
                    continue
                url = entry.get("url") or entry.get("webpage_url")
                if url and str(url).startswith("http"):
                    logger.info("Found candidate URL: %s", url)
                    return str(url)
        except Exception as exc:
            logger.warning("Search failed for pattern %s: %s", pattern, exc)

    return None


async def get_source_audio_path(update: Update, context: ContextTypes.DEFAULT_TYPE, work_dir: str) -> str:
    message = update.effective_message

    if message.text:
        tiktok_url = extract_tiktok_url(message.text)
        if tiktok_url:
            return await asyncio.to_thread(download_audio_from_url, tiktok_url, work_dir)

    tg_audio = message.audio or message.voice
    if not tg_audio:
        raise BotError("Send a TikTok URL or attach audio/voice message")

    logger.info("Downloading Telegram media file")
    telegram_file = await context.bot.get_file(tg_audio.file_id)
    ext = ".ogg" if message.voice else ".mp3"
    local_path = os.path.join(work_dir, f"telegram_input{ext}")
    await telegram_file.download_to_drive(custom_path=local_path)
    return local_path


async def find_and_download_track(track: TrackInfo, work_dir: str) -> str:
    queries = [
        f"{track.artist} {track.title} remix",
        f"{track.artist} {track.title}",
    ]

    for idx, query in enumerate(queries):
        mode = "remix" if idx == 0 else "original"
        logger.info("Trying to find %s: %s", mode, query)
        candidate_url = await asyncio.to_thread(search_track_url, query)
        if not candidate_url:
            continue

        try:
            return await asyncio.to_thread(download_audio_from_url, candidate_url, work_dir)
        except DownloadError as exc:
            logger.warning("Failed to download found candidate: %s", exc)

    raise TrackNotFoundError("Could not find remix or original track")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(
        "Send TikTok URL or voice/audio message. I will recognize the song and return a track file."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    status = await message.reply_text("Processing your request...")

    with tempfile.TemporaryDirectory(prefix="tg-music-bot-") as work_dir:
        try:
            source_audio = await get_source_audio_path(update, context, work_dir)

            snippet_path = os.path.join(work_dir, "snippet.mp3")
            await asyncio.to_thread(make_snippet, source_audio, snippet_path, 15000)

            audd_token = os.getenv("AUDD_TOKEN")
            if not audd_token:
                raise BotError("AUDD_TOKEN is not configured")

            track = await asyncio.to_thread(recognize_with_audd, snippet_path, audd_token)
            found_audio = await find_and_download_track(track, work_dir)

            caption = f"{track.artist} - {track.title}"
            await message.reply_audio(
                audio=found_audio,
                title=track.title,
                performer=track.artist,
                caption=caption,
            )
            await status.edit_text(f"Done: {caption}")

        except RecognitionError as exc:
            logger.exception("Recognition failed")
            await status.edit_text(f"Recognition error: {exc}")
        except TrackNotFoundError as exc:
            logger.exception("Track search failed")
            await status.edit_text(f"Search error: {exc}")
        except DownloadError as exc:
            logger.exception("Download failed")
            await status.edit_text(f"Download error: {exc}")
        except BotError as exc:
            logger.exception("Bot logic error")
            await status.edit_text(str(exc))
        except Exception as exc:
            logger.exception("Unexpected error")
            await status.edit_text(f"Unexpected error: {exc}")


def main() -> None:
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise RuntimeError("BOT_TOKEN is not set")

    application = Application.builder().token(bot_token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.TEXT | filters.VOICE | filters.AUDIO, handle_message)
    )

    logger.info("Bot started")
    application.run_polling(close_loop=False)


if __name__ == "__main__":
    main()