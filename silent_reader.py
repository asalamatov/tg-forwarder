import os
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events
from dotenv import load_dotenv

load_dotenv()

# --- DUMMY FLASK SERVER FOR RENDER FREE TIER ---
app = Flask('')
@app.route('/')
def home(): return "Silent Forwarder Is Alive!", 200
def run_flask(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
def keep_alive(): Thread(target=run_flask).start()
# -----------------------------------------------

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
DESTINATION_CHAT = os.environ.get("DESTINATION_CHAT")

# Read the comma-separated string and split it into a clean Python list
TARGETS_RAW = os.environ.get("TARGET_SENDERS", "")
TARGET_SENDERS_LIST = [t.strip() for t in TARGETS_RAW.split(",") if t.strip()]

client = TelegramClient('silent_session', API_ID, API_HASH)

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    sender = await event.get_sender()
    if not sender:
        return

    # Check both username variations and numerical/phone IDs against our allowed list
    sender_username = getattr(sender, 'username', '') or ''
    sender_phone = getattr(sender, 'phone', '') or ''
    sender_id = str(sender.id)

    is_target = (
        sender_id in TARGET_SENDERS_LIST or
        sender_phone in TARGET_SENDERS_LIST or
        sender_username in TARGET_SENDERS_LIST
    )

    if is_target:
        print(f"📩 Target message detected from: {sender.first_name} (ID: {sender_id})")
        caption_text = f"📩 **Silent Message from {sender.first_name}:**\n\n{event.text or ''}"

        try:
            if event.media:
                await client.send_file(DESTINATION_CHAT, event.media, caption=caption_text)
            else:
                await client.send_message(DESTINATION_CHAT, caption_text)
            print("✅ Successfully forwarded.")
        except Exception as e:
            print(f"❌ Forwarding failed: {e}")

print("🕵️ Starting background components...")
keep_alive()  # Safe to leave active locally or on cloud

with client:
    print(f"📋 Monitoring senders: {TARGET_SENDERS_LIST}")
    client.run_until_disconnected()