"""
Mobile Notification Providers: Discord Webhook and Telegram Bot.
"""
import httpx

def send_discord_notification(webhook_url: str, title: str, description: str) -> bool:
    """Send reminder embed to Discord channel."""
    if not webhook_url:
        return False

    payload = {
        "username": "Streak Sentinel",
        "avatar_url": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
        "embeds": [
            {
                "title": title,
                "description": description,
                "color": 15158332,  # Red alert
                "footer": {"text": "GitHub Streak Sentinel Alert"},
            }
        ]
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            res = client.post(webhook_url, json=payload)
            return res.status_code in (200, 204)
    except Exception:
        return False

def send_telegram_notification(bot_token: str, chat_id: str, message: str) -> bool:
    """Send alert message via Telegram Bot API."""
    if not bot_token or not chat_id:
        return False

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            res = client.post(url, json=payload)
            return res.status_code == 200
    except Exception:
        return False
