"""
Telegram 2-Way Bot Service for GitHub Streak Sentinel.
Handles:
1. Sending notifications when streak/commit threshold is unmet.
2. Receiving and executing remote commands from Telegram app on phone:
   /status, /check, /open, /commit, /notif, /help
"""
import os
import asyncio
import httpx
from datetime import datetime
from pathlib import Path
from dotenv import set_key
from remote_controller import RemoteController

ENV_PATH = Path(__file__).resolve().parent / ".env"

class TelegramBotService:
    def __init__(self):
        self.controller = RemoteController()
        self.last_update_id = 0
        self.is_running = False

    @property
    def bot_token(self):
        return os.getenv("TELEGRAM_BOT_TOKEN", "").strip()

    @property
    def chat_id(self):
        return os.getenv("TELEGRAM_CHAT_ID", "").strip()

    async def send_message(self, text: str, custom_chat_id: str = None) -> bool:
        """Sends a message to user Telegram with automatic fallback to plain text."""
        token = self.bot_token
        target_chat = custom_chat_id or self.chat_id
        if not token or not target_chat:
            print(f"[Telegram Bot] send_message aborted: token={bool(token)}, target_chat={target_chat}")
            return False

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": target_chat,
            "text": text,
            "parse_mode": "Markdown"
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    return True

                # If Markdown parsing failed, retry as plain text!
                print(f"[Telegram Bot] Markdown send failed ({res.status_code}: {res.text}), retrying as plain text...")
                payload.pop("parse_mode", None)
                res_plain = await client.post(url, json=payload)
                if res_plain.status_code == 200:
                    print("[Telegram Bot] Plain text send succeeded!")
                    return True
                else:
                    print(f"[Telegram Bot] Plain text send also failed: {res_plain.text}")
                    return False
        except Exception as e:
            print(f"[Telegram Bot] Send exception: {e}")
            return False

    async def poll_updates(self):
        """Long-polling loop for incoming commands from user on Telegram."""
        self.is_running = True
        print("[Telegram Bot] Poller initialized...", flush=True)

        while self.is_running:
            token = self.bot_token
            if not token:
                await asyncio.sleep(5)
                continue

            url = f"https://api.telegram.org/bot{token}/getUpdates"
            params = {
                "offset": self.last_update_id + 1,
                "timeout": 5
            }

            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    res = await client.get(url, params=params)
                    if res.status_code == 200:
                        data = res.json()
                        updates = data.get("result", [])
                        for update in updates:
                            self.last_update_id = update["update_id"]
                            await self._handle_update(update)
            except Exception as e:
                print(f"[Telegram Bot] Poll error: {e}", flush=True)
                await asyncio.sleep(3)

            await asyncio.sleep(0.5)

    async def _handle_update(self, update: dict):
        message = update.get("message")
        if not message:
            return

        sender_chat_id = str(message.get("chat", {}).get("id", ""))
        text = message.get("text", "").strip()

        print(f"[Telegram Bot] Received command: '{text}' from chat_id={sender_chat_id}")

        # Auto save chat_id if not set yet!
        env_chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
        if not env_chat_id and sender_chat_id:
            os.environ["TELEGRAM_CHAT_ID"] = sender_chat_id
            try:
                set_key(str(ENV_PATH), "TELEGRAM_CHAT_ID", sender_chat_id)
            except Exception:
                pass
            print(f"[Telegram Bot] Auto-detected & saved Telegram Chat ID: {sender_chat_id}")

        if not text:
            return

        if text.startswith("/start"):
            welcome = (
                "🛡️ *Selamat Datang di GitHub Streak Sentinel!* 🍏\n\n"
                f"Sistem terhubung ke komputer PC kamu.\n"
                f"🎯 *Target*: Minimal 9 commit harian\n"
                f"⏰ *Peringatan*: Jam 18:00 WIB jika < 9 commit\n\n"
                "🌐 *Dashboard Web (Apple Glass):*\n"
                "• Dari HP (Wi-Fi): `http://192.168.0.102:8000`\n"
                "• Dari PC: `http://localhost:8000`\n\n"
                "*Perintah Cepat dari HP:*\n"
                "• `/status` - Cek progress commit hari ini\n"
                "• `/check` - Scan langsung ke GitHub API\n"
                "• `/open` - Buka workspace VS Code di PC\n"
                "• `/commit <pesan>` - Auto commit & push dari HP\n"
                "• `/web` - Tampilkan link dashboard web\n"
                "• `/cmd <perintah>` - Jalankan perintah shell/script di project PC\n"
                "• `/notif` - Tes notifikasi ke layar PC"
            )
            await self.send_message(welcome, sender_chat_id)
            return

        # Execute remote command
        output = self.controller.execute_command(text, sender="telegram")
        print(f"[Telegram Bot] Executed '{text}', output: {output[:60]}... sending to {sender_chat_id}")
        sent = await self.send_message(output, sender_chat_id)
        print(f"[Telegram Bot] Message sent result: {sent}")

    def stop(self):
        self.is_running = False
