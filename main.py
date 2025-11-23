import os
import asyncio
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError, RPCError  # корректный импорт для вашей версии

# ------------ ENVIRONMENT ------------
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

SOURCE_CHANNEL = 'https://t.me/poludurove'
TARGET_CHANNEL = 'https://t.me/crazy_giftss'

# ------------ EMOJI MAP ------------
EMOJI_MAP = {
    '👍': '👍',
    '🍾': '🔥',
    '🧩': '🥰'
}

client = TelegramClient('copy_botik', api_id, api_hash)


# ---------- TEXT TRANSFORM ----------
def transform_text(text: str) -> str:
    if not text:
        return ""

    for old, new in EMOJI_MAP.items():
        text = text.replace(old, new)

    # Исправление текста
    text = text.replace("@полудуров", "@crazy_giftss")
    text = text.replace("Купить звезды дешево: @poludurov_stars_bot", "")
    text = text.replace("@poludurov_stars_bot", "@crazy_giftss")

    if "Купить звезды" in text and "stars" in text:
        text = "@crazy_giftss"

    return text + "\n\n🔥 Подписывайся на наш канал!"


# ---------- ALBUM HANDLER ----------
@client.on(events.Album(chats=SOURCE_CHANNEL))
async def album_handler(event):
    print(f"📸 Альбом: {len(event.messages)} медиа")

    caption = transform_text(event.messages[0].message or "")
    temp_files = []

    try:
        for msg in event.messages:
            f = await msg.download_media()
            temp_files.append(f)

        await client.send_file(
            TARGET_CHANNEL,
            temp_files,
            caption=caption,
            supports_streaming=True
        )

        print("✅ Альбом отправлен!")

    finally:
        # Удаление временных файлов
        for f in temp_files:
            try:
                os.remove(f)
            except:
                pass


# ---------- SINGLE POST HANDLER ----------
@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def single_handler(event):
    if event.grouped_id:
        return

    text = transform_text(event.raw_text)

    if event.media:
        f = await event.download_media()
        try:
            await client.send_file(
                TARGET_CHANNEL,
                f,
                caption=text,
                supports_streaming=True
            )
        finally:
            try:
                os.remove(f)
            except:
                pass
    else:
        await client.send_message(TARGET_CHANNEL, text)

    print(f"➡️ Переслан пост {event.id}")


# ---------- MAIN LOOP (24/7 Safety Loop) ----------
async def main_loop():
    while True:
        try:
            print("🚀 Запуск клиента...")
            await client.start()
            print("🤖 Бот запущен, слушаю канал...")

            await client.run_until_disconnected()

        except FloodWaitError as e:
            print(f"⏳ FloodWait: {e.seconds} сек, пауза...")
            await asyncio.sleep(e.seconds)

        except ConnectionError as e:
            print(f"🔌 Проблемы сети: {e}. Перезапуск через 5 сек...")
            await asyncio.sleep(5)

        except RPCError as e:
            print(f"⚠️ RPC ошибка Telegram: {e}. Перезапуск через 5 сек...")
            await asyncio.sleep(5)

        except Exception as e:
            print(f"💥 Неизвестная ошибка: {e}. Перезапуск через 10 сек...")
            await asyncio.sleep(10)


asyncio.run(main_loop())