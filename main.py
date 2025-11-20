from telethon import TelegramClient, events
import re
import os

api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")

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

client = TelegramClient('session', api_id, api_hash)


@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def handler(event):
    try:
        text = event.raw_text or ""

        # Убираем ссылки
        text = re.sub(r'https?://\S+', '', text)

        # Заменяем @полудуров на @crazy_giftss
        text = text.replace('@полудуров', '@crazy_giftss')

        # Заменяем эмодзи
        for old_emoji, new_emoji in EMOJI_MAP.items():
            text = text.replace(old_emoji, new_emoji)

        # Добавляем подпись
        text += "\n\n🔥 Подписывайся на наш канал!"

        # Обработка стикеров
        if event.message.sticker:
            sticker_file = STICKER_MAP.get(event.message.sticker.document.id)
            if sticker_file:
                await client.send_file(TARGET_CHANNEL, sticker_file)
                print("Стикер заменен:", event.message.id)
                return  # если это только стикер, больше ничего не шлем

        # Обработка медиа
        if event.message.media:
            if event.message.photo:
                await client.send_file(TARGET_CHANNEL, event.message.photo, caption=text)
            elif event.message.video:
                await client.send_file(TARGET_CHANNEL, event.message.video, caption=text)
            elif event.message.document:
                await client.send_file(TARGET_CHANNEL, event.message.document, caption=text)
            else:
                # web preview или другое — просто текст
                await client.send_message(TARGET_CHANNEL, text)
        else:
            # только текст
            await client.send_message(TARGET_CHANNEL, text)

        print("Переслано:", event.id)

    except Exception as e:
        print("Ошибка:", e)


client.start()
print("Userbot запущен. Ждем постов...")
client.run_until_disconnected()