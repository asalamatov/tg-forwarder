import os
from threading import Thread
from flask import Flask
from telethon import TelegramClient, events
from dotenv import load_dotenv

load_dotenv()

# --- 1. DUMMY FLASK SERVER TO KEEP RENDER HAPPY ---
app = Flask('')

@app.route('/')
def home():
    return "Silent Forwarder Is Alive!", 200

def run_flask():
    # Render assigns a dynamic port via environment variables
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()
# --------------------------------------------------

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
TARGET_SENDER = os.environ.get("TARGET_SENDER")
DESTINATION_CHAT = os.environ.get("DESTINATION_CHAT")

client = TelegramClient('silent_session', API_ID, API_HASH)

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    sender = await event.get_sender()
    if sender and (getattr(sender, 'username', '') == TARGET_SENDER or str(sender.id) == TARGET_SENDER):
        caption_text = f"📩 **Silent Message from {sender.first_name}:**\n\n{event.text or ''}"
        try:
            if event.media:
                await client.send_file(DESTINATION_CHAT, event.media, caption=caption_text)
            else:
                await client.send_message(DESTINATION_CHAT, caption_text)
        except Exception as e:
            print(f"Error: {e}")

print("🕵️ Starting background components...")
keep_alive()  # Starts the fake web page thread

with client:
    client.run_until_disconnected()