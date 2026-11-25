"""
Telegram 2-Way Bot Service for GitHub Streak Sentinel.
Handles:
1. Sending notifications when streak/commit threshold is unmet.
2. Receiving and executing remote commands from Telegram app on phone:
   /status, /check, /open, /commit, /ping, /web, /cmd, /notif, /help
3. Persistent connection with auto-reconnect and health monitoring.
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
        self.is_connected = False
        self.last_seen = None

    @property
    def bot_token(self):
        return os.getenv("TELEGRAM_BOT_TOKEN", "").strip()

    @property
    def chat_id(self):
        return os.getenv("TELEGRAM_CHAT_ID", "").strip()

    @property
    def last_seen_str(self):
        if self.last_seen:
            return self.last_seen.strftime("%H:%M:%S WIB")
        return "Belum terdeteksi"

    async def send_message(self, text: str, custom_chat_id: str = None) -> bool:
        """Sends a message to user Telegram with automatic fallback to plain text."""
        token = self.bot_token
        target_chat = custom_chat_id or self.chat_id
        if not token or not target_chat:
            print(f"[Telegram Bot] send_message aborted: token={bool(token)}, target_chat={target_chat}", flush=True)
            return False

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": target_chat,
            "text": text,
            "parse_mode": "Markdown"
        }

        timeout = httpx.Timeout(connect=10.0, read=15.0, write=10.0, pool=10.0)
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    self.is_connected = True
                    self.last_seen = datetime.now()
                    return True

                # Fallback to plain text if Markdown parsing fails
                payload.pop("parse_mode", None)
                res_plain = await client.post(url, json=payload)
                if res_plain.status_code == 200:
                    self.is_connected = True
                    self.last_seen = datetime.now()
                    return True
                else:
                    print(f"[Telegram Bot] Plain text send failed: {res_plain.text}", flush=True)
                    return False
        except Exception as e:
            print(f"[Telegram Bot] Send exception: {e}", flush=True)
            return False

    async def poll_updates(self):
        """
        Resilient long-polling loop with persistent client,
        automatic reconnection, and timeout handling.
        """
        self.is_running = True
        print("[Telegram Bot] Poller initialized and running...", flush=True)

        timeout = httpx.Timeout(connect=15.0, read=30.0, write=15.0, pool=15.0)
        limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)

        consecutive_errors = 0

        async with httpx.AsyncClient(timeout=timeout, limits=limits) as client:
            while self.is_running:
                token = self.bot_token
                if not token:
                    self.is_connected = False
                    await asyncio.sleep(5)
                    continue

                url = f"https://api.telegram.org/bot{token}/getUpdates"
                params = {
                    "offset": self.last_update_id + 1,
                    "timeout": 15
                }

                try:
                    res = await client.get(url, params=params)
                    if res.status_code == 200:
                        self.is_connected = True
                        self.last_seen = datetime.now()
                        consecutive_errors = 0
                        
                        data = res.json()
                        updates = data.get("result", [])
                        for update in updates:
                            self.last_update_id = update["update_id"]
                            try:
                                await self._handle_update(update)
                            except Exception as handle_err:
                                print(f"[Telegram Bot] Error handling update: {handle_err}", flush=True)
                    else:
                        print(f"[Telegram Bot] getUpdates returned {res.status_code}: {res.text}", flush=True)
                        consecutive_errors += 1
                        await asyncio.sleep(min(30, 2 ** consecutive_errors))

                except (httpx.ReadTimeout, httpx.ConnectTimeout):
                    # Normal long polling timeout: no new messages, simply loop again
                    self.is_connected = True
                    self.last_seen = datetime.now()
                    consecutive_errors = 0
                    await asyncio.sleep(0.1)
                except Exception as e:
                    consecutive_errors += 1
                    self.is_connected = False
                    backoff = min(20, 2 + consecutive_errors * 2)
                    print(f"[Telegram Bot] Connection hiccup ({e}), reconnecting in {backoff}s...", flush=True)
                    await asyncio.sleep(backoff)

    async def _handle_update(self, update: dict):
        message = update.get("message")
        if not message:
            return

        sender_chat_id = str(message.get("chat", {}).get("id", ""))
        text = message.get("text", "").strip()

        print(f"[Telegram Bot] Received command: '{text}' from chat_id={sender_chat_id}", flush=True)

        # Auto save chat_id if not set yet!
        env_chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
        if not env_chat_id and sender_chat_id:
            os.environ["TELEGRAM_CHAT_ID"] = sender_chat_id
            try:
                set_key(str(ENV_PATH), "TELEGRAM_CHAT_ID", sender_chat_id)
            except Exception:
                pass
            print(f"[Telegram Bot] Auto-detected & saved Telegram Chat ID: {sender_chat_id}", flush=True)

        if not text:
            return

        # Special handler for /start
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
                "• `/ping` - Tes kecepatan koneksi bot ke PC\n"
                "• `/web` - Tampilkan link dashboard web\n"
                "• `/cmd <perintah>` - Jalankan perintah shell/script di project PC\n"
                "• `/notif` - Tes notifikasi toast ke layar PC"
            )
            await self.send_message(welcome, sender_chat_id)
            return

        # Execute remote command
        output = self.controller.execute_command(text, sender="telegram")
        print(f"[Telegram Bot] Executed '{text}', sending response to {sender_chat_id}", flush=True)
        await self.send_message(output, sender_chat_id)

    def stop(self):
        self.is_running = False
