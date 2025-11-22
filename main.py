import os
import re
from telethon import TelegramClient, events


api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

SOURCE_CHANNEL = 'https://t.me/dfhsoidfhso'   # канал-источник
TARGET_CHANNEL = 'https://t.me/tetetetetedf'     # куда репостить

STICKER_MAP = {
    # Пример: 123456789012345678 → 'stickers/my_sticker.webp'
}
# Словарь для замены эмодзи в тексте
EMOJI_MAP = {
    '👍': '👍',
    '🍾': '🔥',
    '🧩': '🥰'
}

client = TelegramClient('copy_botik', api_id, api_hash)



def transform_text(text: str) -> str:
    if not text:
        return ""

    for old, new in EMOJI_MAP.items():
        text = text.replace(old, new)

    text = text.replace("@полудуров", "@crazy_giftss")
    text = text.replace("Купить звезды дешево: @poludurov_stars_bot", "")
    text = text.replace("@poludurov_stars_bot", "@crazy_giftss")

    # На случай разных форматов и текста до/после
    if "Купить звезды" in text and "stars" in text:
        text = "@crazy_giftss"

    # Дополнительная подпись
    text += "\n\n🔥 Подписывайся на наш канал!"

    return text


# ---------- АЛЬБОМ ----------
@client.on(events.Album(chats=SOURCE_CHANNEL))
async def album_handler(event):

    print(f"📸 Альбом обнаружен: {len(event.messages)} медиа")

    # первый caption
    caption = transform_text(event.messages[0].message or "")

    # список путей файлов
    files = []

    for msg in event.messages:
        f = await msg.download_media()
        files.append(f)

    # Telethon сам определит медиатипы, mime и атрибуты
    await client.send_file(
        TARGET_CHANNEL,
        files,
        caption=caption,
        supports_streaming=True
    )

    print("✅ Альбом отправлен!")


# ---------- ОДИНОЧНЫЕ ПОСТЫ ----------
@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def single_handler(event):

    if event.grouped_id:
        return

    text = transform_text(event.raw_text)

    if event.media:
        await client.send_file(
            TARGET_CHANNEL,
            event.media,
            caption=text,
            supports_streaming=True
        )
    else:
        await client.send_message(TARGET_CHANNEL, text)

    print(f"➡️ Переслан пост {event.id}")


client.start()
print("🤖 Бот запущен, отслеживаю канал...")
client.run_until_disconnected()