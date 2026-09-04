import os
import asyncio
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events
from dotenv import load_dotenv

load_dotenv()

# --- DUMMY FLASK SERVER FOR RENDER ---
app = Flask('')
@app.route('/')
def home(): return "Silent Hybrid Forwarder Is Alive!", 200
def run_flask(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
def keep_alive(): Thread(target=run_flask, daemon=True).start()
# -------------------------------------

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
DESTINATION_CHAT = os.environ.get("DESTINATION_CHAT")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

TARGETS_RAW = os.environ.get("TARGET_SENDERS", "")
TARGET_SENDERS_LIST = [t.strip() for t in TARGETS_RAW.split(",") if t.strip()]

# 1. Initialize the passive User client (listens to incoming texts without going online)
client = TelegramClient('silent_session', API_ID, API_HASH)

# 2. Initialize the active Bot client (handles all sending securely out-of-sight)
bot_client = TelegramClient('bot_session', API_ID, API_HASH)

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    sender = await event.get_sender()
    if not sender:
        return

    sender_username = getattr(sender, 'username', '') or ''
    sender_phone = getattr(sender, 'phone', '') or ''
    sender_id = str(sender.id)

    is_target = (
        sender_id in TARGET_SENDERS_LIST or
        sender_phone in TARGET_SENDERS_LIST or
        sender_username in TARGET_SENDERS_LIST
    )

    if is_target:
        print(f"📩 Target message intercepted from: {sender.first_name}")
        caption_text = f"📩 **Silent Message from {sender.first_name}:**\n\n{event.text or ''}"

        try:
            # We explicitly use the bot_client here to forward files and messages.
            if event.media:
                print("🔄 Bot is downloading and forwarding media...")
                await bot_client.send_file(DESTINATION_CHAT, event.media, caption=caption_text)
            else:
                await bot_client.send_message(DESTINATION_CHAT, caption_text)
            print("✅ Bot successfully mirrored message anonymously.")
        except Exception as e:
            print(f"❌ Bot forwarding failed: {e}")

async def main():
    print("🕵️ Connecting clients...")

    # Start both clients cleanly using await syntax
    await client.start()
    await bot_client.start(bot_token=BOT_TOKEN)

    print(f"📋 Monitoring senders anonymously: {TARGET_SENDERS_LIST}")

    # Keep the script running until disconnected
    await client.run_until_disconnected()

if __name__ == '__main__':
    print("🕵️ Starting background components...")
    keep_alive()

    # Run the main async loop properly
    asyncio.run(main())