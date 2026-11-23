"""
GitHub Streak Sentinel Server.
FastAPI web server providing:
1. Apple Glassmorphism Dashboard UI (accessible from PC and Mobile).
2. WhatsApp & Telegram 2-Way Bot & Remote Control Receiver.
3. Background scheduled checking at 18:00 WIB with 9 commit threshold.
"""
import os
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv, set_key

from github_checker import GitHubStreakChecker
from notifier_whatsapp import send_whatsapp_notification
from notifier_windows import send_windows_toast
from notifier_mobile import send_discord_notification, send_telegram_notification
from remote_controller import RemoteController
from telegram_bot import TelegramBotService

ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

controller = RemoteController()
telegram_bot = TelegramBotService()

# Background Sentinel Task
async def sentinel_background_loop():
    """Runs periodic streak check in the background."""
    notified_today = False
    last_notified_date = None

    while True:
        try:
            now = datetime.now()
            today_str = now.strftime("%Y-%m-%d")

            # Reset daily notification state on new day
            if last_notified_date != today_str:
                notified_today = False
                last_notified_date = today_str

            target_hour = int(os.getenv("REMINDER_HOUR", "18"))
            min_commits = int(os.getenv("MIN_COMMITS", "9"))

            # Trigger at target hour (e.g. 18:00)
            if now.hour == target_hour and not notified_today:
                username = os.getenv("GITHUB_USERNAME", "Tryton47")
                checker = GitHubStreakChecker(username)
                committed, count, repos = checker.has_committed_today()

                if count < min_commits:
                    notified_today = True
                    remaining = min_commits - count
                    project_path = os.getenv("PROJECT_PATH", r"D:\scrapton-3platform")

                    # 1. Windows Toast
                    send_windows_toast(
                        title=f"🚨 Sentinel: Belum Ada {min_commits} Commit!",
                        message=f"Halo @{username}, jam 18:00 WIB baru {count}/{min_commits} commit. Kurang {remaining} lagi!",
                        project_path=project_path
                    )

                    alert_msg = (
                        f"🚨 *PERINGATAN GITHUB SENTINEL (JAM 18:00 WIB)*\n\n"
                        f"Halo *@{username}*, hari ini baru tercatat *{count}/{min_commits} commit* (bebas di project mana saja).\n"
                        f"⚠️ Masih kurang *{remaining} commit* lagi untuk mencapai target harian!\n\n"
                        f"💡 Perintah cepat dari HP:\n"
                        f"• `/open` (buka VS Code di PC)\n"
                        f"• `/commit update progress` (auto-push commit)\n"
                        f"• `/status` (cek ulang)"
                    )

                    # 2. Telegram Alert
                    await telegram_bot.send_message(alert_msg)

                    # 3. WhatsApp Alert (if configured)
                    phone = os.getenv("WHATSAPP_PHONE")
                    fonnte = os.getenv("FONNTE_TOKEN")
                    if phone and fonnte:
                        send_whatsapp_notification(message=alert_msg, target_phone=phone)

            await asyncio.sleep(60)
        except Exception:
            await asyncio.sleep(60)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[System] Lifespan startup: Starting background tasks & Telegram bot poller...", flush=True)
    t1 = asyncio.create_task(sentinel_background_loop())
    t2 = asyncio.create_task(telegram_bot.poll_updates())
    yield
    t1.cancel()
    t2.cancel()

app = FastAPI(title="GitHub Streak Sentinel — Apple Glass Edition", lifespan=lifespan)
INDEX_HTML_PATH = Path(__file__).resolve().parent / "templates" / "index.html"

@app.get("/", response_class=FileResponse)
async def serve_dashboard():
    """Serves the Apple Glass UI Dashboard."""
    return FileResponse(INDEX_HTML_PATH)

@app.get("/api/status")
async def get_streak_status():
    """Returns today's commit status, target threshold, and progress."""
    username = os.getenv("GITHUB_USERNAME", "Tryton47")
    min_commits = int(os.getenv("MIN_COMMITS", "9"))
    checker = GitHubStreakChecker(username)
    committed, count, repos = checker.has_committed_today()
    
    target_met = count >= min_commits
    percentage = min(100, int((count / min_commits) * 100)) if min_commits > 0 else 100

    return {
        "username": username,
        "committed": target_met,
        "commit_count": count,
        "target_commits": min_commits,
        "remaining": max(0, min_commits - count),
        "percentage": percentage,
        "repos": repos,
        "reminder_hour": int(os.getenv("REMINDER_HOUR", "18")),
        "telegram_active": bool(os.getenv("TELEGRAM_BOT_TOKEN")),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

class CommandRequest(BaseModel):
    command: str

class SettingsPayload(BaseModel):
    github_username: Optional[str] = None
    github_token: Optional[str] = None
    project_path: Optional[str] = None
    whatsapp_phone: Optional[str] = None
    fonnte_token: Optional[str] = None
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    min_commits: Optional[int] = None
    reminder_hour: Optional[int] = None

@app.post("/api/command")
async def execute_remote_command(payload: CommandRequest):
    """Executes a command originating from Web UI or local client."""
    output = controller.execute_command(payload.command, sender="web-ui")
    return {"output": output}

@app.get("/api/settings")
async def get_settings():
    return {
        "github_username": os.getenv("GITHUB_USERNAME", "Tryton47"),
        "github_token": "***" if os.getenv("GITHUB_TOKEN") else "",
        "project_path": os.getenv("PROJECT_PATH", r"D:\scrapton-3platform"),
        "whatsapp_phone": os.getenv("WHATSAPP_PHONE", "082141635002"),
        "fonnte_token": os.getenv("FONNTE_TOKEN", ""),
        "telegram_bot_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
        "telegram_chat_id": os.getenv("TELEGRAM_CHAT_ID", ""),
        "min_commits": int(os.getenv("MIN_COMMITS", "9")),
        "reminder_hour": int(os.getenv("REMINDER_HOUR", "18")),
    }

@app.post("/api/settings")
async def save_settings(payload: SettingsPayload):
    if not ENV_PATH.exists():
        ENV_PATH.touch()

    if payload.github_username is not None:
        set_key(str(ENV_PATH), "GITHUB_USERNAME", payload.github_username)
        os.environ["GITHUB_USERNAME"] = payload.github_username
        controller.username = payload.github_username

    if payload.github_token is not None and payload.github_token != "***":
        set_key(str(ENV_PATH), "GITHUB_TOKEN", payload.github_token)
        os.environ["GITHUB_TOKEN"] = payload.github_token

    if payload.project_path is not None:
        set_key(str(ENV_PATH), "PROJECT_PATH", payload.project_path)
        os.environ["PROJECT_PATH"] = payload.project_path
        controller.project_path = payload.project_path

    if payload.whatsapp_phone is not None:
        set_key(str(ENV_PATH), "WHATSAPP_PHONE", payload.whatsapp_phone)
        os.environ["WHATSAPP_PHONE"] = payload.whatsapp_phone

    if payload.fonnte_token is not None:
        set_key(str(ENV_PATH), "FONNTE_TOKEN", payload.fonnte_token)
        os.environ["FONNTE_TOKEN"] = payload.fonnte_token

    if payload.telegram_bot_token is not None:
        set_key(str(ENV_PATH), "TELEGRAM_BOT_TOKEN", payload.telegram_bot_token.strip())
        os.environ["TELEGRAM_BOT_TOKEN"] = payload.telegram_bot_token.strip()

    if payload.telegram_chat_id is not None:
        set_key(str(ENV_PATH), "TELEGRAM_CHAT_ID", payload.telegram_chat_id.strip())
        os.environ["TELEGRAM_CHAT_ID"] = payload.telegram_chat_id.strip()

    if payload.min_commits is not None:
        set_key(str(ENV_PATH), "MIN_COMMITS", str(payload.min_commits))
        os.environ["MIN_COMMITS"] = str(payload.min_commits)
        controller.min_commits = payload.min_commits

    if payload.reminder_hour is not None:
        set_key(str(ENV_PATH), "REMINDER_HOUR", str(payload.reminder_hour))
        os.environ["REMINDER_HOUR"] = str(payload.reminder_hour)

    return {"status": "success", "message": "Konfigurasi berhasil disimpan ke .env"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
