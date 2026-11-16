# 🛡️ GitHub Streak Sentinel

Sistem pengingat pintar otomatis untuk memantau kontribusi harian GitHub Anda dan menjaga agar grafik commit Anda tetap hijau setiap hari!

## ✨ Fitur

- 🔍 **Live GitHub API Tracking**: Memeriksa commit hari ini tanpa perlu login manual.
- 💻 **Windows Toast Notification**: Notifikasi popup langsung di layar PC Anda lengkap dengan tombol menuju workspace.
- 📱 **Mobile Alert (Discord & Telegram)**: Notifikasi instan langsung masuk ke HP Anda jika belum ada commit hingga sore/malam hari.
- ⏰ **Windows Task Scheduler Integration**: Berjalan otomatis di latar belakang tanpa memberatkan PC.

---

## 🚀 Panduan Setup Singkat

1. **Konfigurasi Lingkungan (`.env`)**:
   Salin `.env.example` ke `.env` lalu sesuaikan:
   ```env
   GITHUB_USERNAME=Tryton47
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/... (opsional)
   TELEGRAM_BOT_TOKEN=... (opsional)
   TELEGRAM_CHAT_ID=... (opsional)
   PROJECT_PATH=D:\scrapton-3platform
   ```

2. **Jalankan Uji Coba Manual**:
   ```bash
   python main.py
   ```

3. **Pasang Jadwal Otomatis di Windows**:
   Jalankan file PowerShell ini sekali saja:
   ```powershell
   powershell -ExecutionPolicy Bypass -File install_scheduler.ps1
   ```
