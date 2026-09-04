import os
# , dotenv
# dotenv.load_dotenv()  # Load environment variables from .env file
from telethon import TelegramClient, events

# 1. Pull credentials securely from Render's Environment Variables
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")

# 2. Target configuration
TARGET_SENDER = os.environ.get("TARGET_SENDER")       # Target username or numerical ID
DESTINATION_CHAT = os.environ.get("DESTINATION_CHAT")  # Destination username or numerical ID

# Initialize the client session using the uploaded .session file
client = TelegramClient('silent_session', API_ID, API_HASH)

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    sender = await event.get_sender()

    # Check if the message is from our target sender
    if sender and (getattr(sender, 'username', '') == TARGET_SENDER or str(sender.id) == TARGET_SENDER):
        print(f"📩 Message detected from @{sender.username}")

        # Nicely formatted caption/text context
        caption_text = f"📩 **Silent Message from {sender.first_name}:**\n\n{event.text or ''}"

        try:
            # Check if the message contains any media (Photos, Videos, Voice Notes, Files)
            if event.media:
                print("🔄 Downloading media silently...")
                # Download media straight to memory/temp file and send it to destination
                await client.send_file(DESTINATION_CHAT, event.media, caption=caption_text)
                print("✅ Successfully forwarded media file.")
            else:
                # Text-only message
                await client.send_message(DESTINATION_CHAT, caption_text)
                print("✅ Successfully forwarded text message.")

        except Exception as e:
            print(f"❌ Failed to forward message/file: {e}")

        # NOTE: 'event.mark_read()' is omitted. The sender sees a single checkmark.

print("🕵️ Silent Forwarder with File Support is running...")

with client:
    client.run_until_disconnected()