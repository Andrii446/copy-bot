import os
import asyncio
import re
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError, RPCError

# ------------ ENVIRONMENT ------------
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

SOURCE_CHANNEL = 'https://t.me/poludurove'
TARGET_CHANNEL = 'https://t.me/crazy_giftss'
LOG_CHANNEL = 'https://t.me/reklama_logg'  # замените на ID или @username для логирования рекламы

# ------------ EMOJI MAP ------------
EMOJI_MAP = {
    '👍': '👍',
    '🍾': '🔥',
    '🧩': ''
}

client = TelegramClient('copy_bo', api_id, api_hash)

# ---------- DETECTOR CONFIG ----------
WHITELIST = {
    "полудуров",
    "crazy_giftss"
}

CTA_KEYWORDS = [
    "смотреть", "участвуй", "проверить", "итоги",
    "не пропусти", "кликни", "жми", "7️⃣7️⃣7️⃣", "777", "прокрут", "🎰"
]

EXTERNAL_LINK_PATTERN = re.compile(
    r"(t\.me\/[A-Za-z0-9_]+|@[\w_]+|https?://[^\s]+)"
)

REF_PATTERN = re.compile(r"(startapp=|ref_|devapp\?)", re.IGNORECASE)

def detect_ad_elements(text: str) -> dict:
    if not text:
        return {'is_ad': False, 'referral': [], 'external_links': [], 'cta_keywords': []}

    result = {
        'is_ad': False,
        'referral': [],
        'external_links': [],
        'cta_keywords': []
    }

    text_lower = text.lower()

    # 1️⃣ Реферальные ссылки
    referral_matches = REF_PATTERN.findall(text)
    if referral_matches:
        result['referral'] = referral_matches
        result['is_ad'] = True

    # 2️⃣ Внешние ссылки / юзернеймы
    links = EXTERNAL_LINK_PATTERN.findall(text)
    external_links = []
    for link in links:
        clean_link = link.replace("t.me/", "").replace("@", "")
        if clean_link not in WHITELIST:
            external_links.append(link)
    if external_links:
        result['external_links'] = external_links
        result['is_ad'] = True

    # 3️⃣ Рекламные CTA
    cta_hits = [kw for kw in CTA_KEYWORDS if kw in text_lower]
    if cta_hits:
        result['cta_keywords'] = cta_hits
        result['is_ad'] = True

    return result

# ---------- TEXT TRANSFORM ----------
def transform_text(text: str) -> str:
    if not text:
        return ""
    for old, new in EMOJI_MAP.items():
        text = text.replace(old, new)

    # Исправление текста
    text = text.replace("@полудуров", "")
    text = text.replace("@GiftsTracker", "")
    text = text.replace("@GiftsBuyer", "")
    text = text.replace("⭐️Купить звезды дешево: @poludurov_stars_bot", "")

    if "Купить звезды" in text and "stars" in text:
        text = "@crazy_giftss"

    return text

def final_text(text: str) -> str:
    text += "❤️Самые дешевые звезды тут: @craazy_stars_bot❤️"
    return text

# ---------- ALBUM HANDLER ----------
@client.on(events.Album(chats=SOURCE_CHANNEL))
async def album_handler(event):
    print(f"📸 Альбом: {len(event.messages)} медиа")

    full_text = "\n".join([m.message or "" for m in event.messages])
    transformed_text = transform_text(full_text)  # проверка уже после трансформации

    temp_files = []
    try:
        for msg in event.messages:
            f = await msg.download_media()
            temp_files.append(f)

        # Проверка на рекламу по трансформированному тексту
        ad_info = detect_ad_elements(transformed_text)
        if ad_info['is_ad']:
            print("🚫 Альбом содержит рекламу:", ad_info)
            await client.send_message(LOG_CHANNEL, f"🚫 Альбом содержит рекламу:\n{ad_info}\n\nТекст:\n{transformed_text}")
            return  # не пересылаем в основной канал

        await client.send_file(
            TARGET_CHANNEL,
            temp_files,
            caption=transformed_text,
            supports_streaming=True
        )

        print("✅ Альбом отправлен!")

    finally:
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

    transformed_text = transform_text(event.raw_text)  # проверка и трансформация сразу
    final= final_text(transformed_text)

    # Проверка на рекламу по трансформированному тексту
    ad_info = detect_ad_elements(transformed_text)
    if ad_info['is_ad']:
        print(f"🚫 Пост {event.id} содержит рекламу:", ad_info)
        await client.send_message(LOG_CHANNEL, f"🚫 Пост {event.id} содержит рекламу:\n{ad_info}\n\nТекст:\n{transformed_text}")
        return  # не пересылаем пост в основной канал

    if event.media:
        f = await event.download_media()
        try:
            await client.send_file(
                TARGET_CHANNEL,
                f,
                caption=final,
                supports_streaming=True
            )
        finally:
            try:
                os.remove(f)
            except:
                pass
    else:
        await client.send_message(TARGET_CHANNEL, final)

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