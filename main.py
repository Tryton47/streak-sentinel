"""
Main sentinel orchestrator.
Reads environment, queries GitHub, triggers desktop, WhatsApp, and mobile alerts if streak is at risk.
Can also launch the Apple Glass Dashboard server.
"""
import os
import sys
import argparse
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

from github_checker import GitHubStreakChecker
from notifier_windows import send_windows_toast
from notifier_mobile import send_discord_notification, send_telegram_notification
from notifier_whatsapp import send_whatsapp_notification

console = Console()
load_dotenv()

def run_cli_check():
    username = os.getenv("GITHUB_USERNAME", "Tryton47")
    discord_webhook = os.getenv("DISCORD_WEBHOOK_URL")
    tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
    tg_chat = os.getenv("TELEGRAM_CHAT_ID")
    wa_phone = os.getenv("WHATSAPP_PHONE")
    fonnte_token = os.getenv("FONNTE_TOKEN")
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
        "Mengirimkan notifikasi ke Desktop, WhatsApp, dan Mobile...",
        title="Streak Alert",
        border_style="red"
    ))

    # 1. Windows Toast
    send_windows_toast(
        title="🚨 GitHub Streak Reminder!",
        message=f"Woi @{username}, belum ada commit hari ini! Yuk ngoding sebentar.",
        project_path=project_path,
    )

    # 2. WhatsApp Notification
    if wa_phone and fonnte_token:
        res = send_whatsapp_notification(
            message=(
                f"🚨 *GitHub Streak Alert!*\n"
                f"Halo @{username}, belum ada commit hari ini di GitHub.\n"
                f"Balas *!open* untuk buka workspace di PC atau *!commit* untuk auto-commit sekarang!"
            )
        )
        if res.get("success"):
            console.print("[green]✔ Notifikasi WhatsApp berhasil dikirim![/green]")
        else:
            console.print(f"[yellow]⚠ WhatsApp notifikasi: {res.get('detail')}[/yellow]")

    # 3. Discord Alert
    if discord_webhook:
        send_discord_notification(
            discord_webhook,
            title="🚨 GitHub Streak Alert!",
            description=f"Halo **{username}**, hari ini Anda belum melakukan push ke GitHub. Yuk luangkan waktu 5 menit untuk update repo!",
        )

    # 4. Telegram Alert
    if tg_token and tg_chat:
        send_telegram_notification(
            tg_token,
            tg_chat,
            f"🚨 *GitHub Streak Alert!*\nHalo *{username}*, hari ini belum ada commit di GitHub. Buka workspace sekarang: `{project_path}`"
        )

def main():
    parser = argparse.ArgumentParser(description="GitHub Streak Sentinel")
    parser.add_argument("--server", action="store_true", help="Jalankan Apple Glass Web Dashboard & Remote Server")
    parser.add_argument("--port", type=int, default=8000, help="Port untuk Web Dashboard (default: 8000)")
    args = parser.parse_args()

    if args.server:
        import uvicorn
        console.print("[bold green]Meluncurkan Apple Glass Dashboard & Remote Server...[/bold green]")
        console.print(f"[cyan]Akses di PC : http://localhost:{args.port}[/cyan]")
        console.print(f"[cyan]Akses di HP : http://192.168.0.102:{args.port}[/cyan]")
        uvicorn.run("server:app", host="0.0.0.0", port=args.port, reload=True)
    else:
        run_cli_check()

if __name__ == "__main__":
    main()
