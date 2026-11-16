"""
Main sentinel orchestrator.
Reads environment, queries GitHub, triggers desktop and mobile alerts if streak is at risk.
"""
import os
import sys
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

from github_checker import GitHubStreakChecker
from notifier_windows import send_windows_toast
from notifier_mobile import send_discord_notification, send_telegram_notification

console = Console()
load_dotenv()

def main():
    username = os.getenv("GITHUB_USERNAME", "Tryton47")
    discord_webhook = os.getenv("DISCORD_WEBHOOK_URL")
    tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
    tg_chat = os.getenv("TELEGRAM_CHAT_ID")
    project_path = os.getenv("PROJECT_PATH", r"D:\scrapton-3platform")

    console.print(f"[bold cyan]Scanning GitHub streak for user:[/bold cyan] {username}")
    checker = GitHubStreakChecker(username)
    committed, count, repos = checker.has_committed_today()

    if committed:
        console.print(Panel(
            f"[bold green]Streak Aman! Hari ini sudah ada {count} commit.[/bold green]\n"
            f"Repositories: {', '.join(repos)}",
            title="GitHub Streak Status",
            border_style="green"
        ))
        return

    # Jika belum ada commit hari ini
    console.print(Panel(
        f"[bold red]PERINGATAN: Belum ada commit terdeteksi untuk @{username} hari ini![/bold red]\n"
        "Mengirimkan notifikasi ke Desktop dan HP...",
        title="Streak Alert",
        border_style="red"
    ))

    # 1. Windows Toast
    send_windows_toast(
        title="🚨 GitHub Streak Reminder!",
        message=f"Woi @{username}, belum ada commit hari ini! Yuk ngoding sebentar.",
        project_path=project_path,
    )

    # 2. Discord Alert
    if discord_webhook:
        send_discord_notification(
            discord_webhook,
            title="🚨 GitHub Streak Alert!",
            description=f"Halo **{username}**, hari ini Anda belum melakukan push ke GitHub. Yuk luangkan waktu 5 menit untuk update repo!",
        )

    # 3. Telegram Alert
    if tg_token and tg_chat:
        send_telegram_notification(
            tg_token,
            tg_chat,
            f"🚨 *GitHub Streak Alert!*\nHalo *{username}*, hari ini belum ada commit di GitHub. Buka workspace sekarang: `{project_path}`"
        )

if __name__ == "__main__":
    main()
