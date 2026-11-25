"""
Diagnostic script for GitHub Streak Sentinel Telegram Bot.
Tests token validity, network connectivity, and message transmission latency.
"""
import sys
import asyncio
import os
import time

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from dotenv import load_dotenv

load_dotenv()

from telegram_bot import TelegramBotService

async def run_diagnostics():
    print("=" * 60)
    print(" [Sentinel] Telegram Bot Diagnostics Tool")
    print("=" * 60)

    bot = TelegramBotService()
    token = bot.bot_token
    chat_id = bot.chat_id

    if not token:
        print("[!] Error: TELEGRAM_BOT_TOKEN is not configured in .env")
        return

    print(f"[*] Bot Token   : {token[:10]}...{token[-5:]}")
    print(f"[*] Target Chat : {chat_id or 'Not yet set (send /start to bot to link)'}")

    if not chat_id:
        print("[!] Warning: Send /start to your bot in Telegram first to auto-link your chat ID.")
        return

    print("\n[1/2] Menguji pengiriman pesan ke Telegram...")
    start_t = time.time()
    success = await bot.send_message(
        "⚡ *Sentinel Diagnostic Test*: Koneksi PC ke Telegram berhasil diverifikasi!\n"
        "⏱️ Menghitung latensi..."
    )
    latency = round((time.time() - start_t) * 1000, 2)

    if success:
        print(f"[+] Pesan berhasil dikirim!")
        print(f"[+] Latensi HTTP Round-Trip: {latency} ms")
        print("\n[2/2] Mengirim konfirmasi latensi...")
        await bot.send_message(f"✅ *Sentinel Terhubung!* Latensi round-trip: `{latency} ms`.")
        print("[+] Semua sistem Telegram Sentinel beroperasi normal.")
    else:
        print("[-] Gagal mengirim pesan. Periksa koneksi internet atau validitas token.")

if __name__ == "__main__":
    asyncio.run(run_diagnostics())
