"""
WhatsApp Notification Provider.
Supports Fonnte API (Indonesia standard), Green-API, Wablas, or Generic Webhook.
"""
import os
import httpx
from typing import Optional

def send_whatsapp_notification(
    message: str,
    target_phone: Optional[str] = None,
    fonnte_token: Optional[str] = None,
    green_api_instance: Optional[str] = None,
    green_api_token: Optional[str] = None,
    custom_webhook_url: Optional[str] = None
) -> dict:
    """
    Sends WhatsApp message via the configured provider in .env.
    Prioritizes:
    1. Fonnte (if FONNTE_TOKEN is set)
    2. Green-API (if GREEN_API_INSTANCE and GREEN_API_TOKEN are set)
    3. Custom Webhook (if WHATSAPP_WEBHOOK_URL is set)
    """
    target_phone = target_phone or os.getenv("WHATSAPP_PHONE", "")
    fonnte_token = fonnte_token or os.getenv("FONNTE_TOKEN", "")
    green_api_instance = green_api_instance or os.getenv("GREEN_API_INSTANCE", "")
    green_api_token = green_api_token or os.getenv("GREEN_API_TOKEN", "")
    custom_webhook_url = custom_webhook_url or os.getenv("WHATSAPP_WEBHOOK_URL", "")

    result = {"success": False, "provider": None, "detail": ""}

    # 1. Fonnte API (Very popular, quick free setup at fonnte.com)
    if fonnte_token and target_phone:
        try:
            url = "https://api.fonnte.com/send"
            headers = {"Authorization": fonnte_token}
            payload = {
                "target": target_phone,
                "message": message,
                "countryCode": "62", # Default to Indonesia country code
            }
            with httpx.Client(timeout=12.0) as client:
                res = client.post(url, headers=headers, data=payload)
                data = res.json()
                if res.status_code == 200 and data.get("status"):
                    return {"success": True, "provider": "fonnte", "detail": "Pesan WA terkirim via Fonnte"}
                return {"success": False, "provider": "fonnte", "detail": str(data)}
        except Exception as e:
            return {"success": False, "provider": "fonnte", "detail": str(e)}

    # 2. Green API
    if green_api_instance and green_api_token and target_phone:
        try:
            # Format phone to 628xxx@c.us
            cleaned_phone = "".join(filter(str.isdigit, target_phone))
            if cleaned_phone.startswith("0"):
                cleaned_phone = "62" + cleaned_phone[1:]
            chat_id = f"{cleaned_phone}@c.us"

            url = f"https://api.green-api.com/waInstance{green_api_instance}/sendMessage/{green_api_token}"
            payload = {
                "chatId": chat_id,
                "message": message
            }
            with httpx.Client(timeout=12.0) as client:
                res = client.post(url, json=payload)
                if res.status_code == 200:
                    return {"success": True, "provider": "green-api", "detail": "Pesan WA terkirim via Green-API"}
                return {"success": False, "provider": "green-api", "detail": res.text}
        except Exception as e:
            return {"success": False, "provider": "green-api", "detail": str(e)}

    # 3. Custom / Local WA Gateway Webhook
    if custom_webhook_url:
        try:
            payload = {
                "phone": target_phone,
                "message": message
            }
            with httpx.Client(timeout=12.0) as client:
                res = client.post(custom_webhook_url, json=payload)
                if res.status_code in (200, 201, 204):
                    return {"success": True, "provider": "webhook", "detail": "Pesan WA terkirim via Custom Webhook"}
                return {"success": False, "provider": "webhook", "detail": res.text}
        except Exception as e:
            return {"success": False, "provider": "webhook", "detail": str(e)}

    return {
        "success": False,
        "provider": "none",
        "detail": "Belum ada konfigurasi WhatsApp di .env (FONNTE_TOKEN / GREEN_API / WHATSAPP_WEBHOOK_URL)"
    }
