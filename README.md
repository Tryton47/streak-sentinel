# 🛡️ GitHub Streak Sentinel — Apple Glass Edition 🍏

Sistem penjaga streak GitHub otomatis dengan tampilan **Liquid Frosted Glass ala Apple macOS / iOS**, notifikasi & kontrol 2 arah via **Telegram Bot (@tryton_streak_bot)** & **WhatsApp**, serta target harian **minimal 9 commit** dengan pengingat jam 18:00 WIB!

---

## ✨ Fitur Unggulan

### 1. 🍏 Apple Liquid Glassmorphism Dashboard
- Desain antarmuka transparan frosted glass mewah berbasis **macOS Sequoia / iOS 18** (SF Pro, ambient glow mesh, ultra-frosted blur).
- **Apple Fitness Circular Progress Ring**: Cincin SVG dinamis yang menampilkan target harian minimal 9 commit.
- **Beacon Status Telegram Live**: Indikator hijau real-time `🟢 Online` yang terhubung langsung ke bot Telegram dengan tombol tes latency *Ping*.
- **Floating Mobile Glass Dock**: Navigasi pil mengambang di layar smartphone untuk kontrol cepat sekali sentuh.
- **Konsol Terminal Glass**: Eksekusi perintah shell & git langsung dari dashboard web.

### 2. 🤖 Telegram 2-Way Bot Remote Control (@tryton_streak_bot)
- Bot interaktif 2 arah tanpa biaya:
  - `/status` : Cek progress commit hari ini dan jarak menuju target 9 commit.
  - `/check`  : Scan instan ke GitHub API.
  - `/open`   : Luncurkan workspace VS Code di PC langsung dari chat Telegram HP!
  - `/commit <pesan>` : Auto-commit & git push darurat dari HP untuk mengamankan streak.
  - `/ping`   : Tes latensi dan stabilitas koneksi antara Telegram dan PC.
  - `/web`    : Tampilkan link langsung ke Apple Glass Dashboard.
  - `/cmd <perintah>` : Jalankan perintah shell / script di project PC.
  - `/notif`  : Tembak notifikasi toast native ke layar PC.

### 3. 🎯 Aturan Target 9 Commit & Peringatan 18:00 WIB
- Menghitung akumulasi seluruh commit hari ini di semua repositori akun kamu.
- Jika sampai pukul **18:00 WIB** target 9 commit belum tercapai, Sentinel secara otomatis mengirimkan alert ke:
  1. Telegram Bot di HP kamu.
  2. Native Windows 10/11 Toast Notification di monitor PC.
  3. WhatsApp (opsional via Fonnte Gateway).

### 4. 🔄 24/7 Background Persistence & Auto-Start
- **Zero-Window Silent Runner (`start_sentinel_silent.vbs`)**: Menjalankan Sentinel di background tanpa ada jendela CMD yang mengganggu.
- **Windows Startup Installer (`install_autostart.ps1`)**: Sekali klik untuk mendaftarkan Sentinel ke Startup Windows agar selalu aktif otomatis setelah PC menyala.

---

## 🚀 Cara Menjalankan

### A. Background Otomatis (Rekomendasi)
Klik dua kali file:
```
start_sentinel_silent.vbs
```
Sentinel akan langsung aktif di latar belakang (background) tanpa jendela terminal.

### B. Dashboard Interaktif (Dengan Terminal)
Klik dua kali file:
```
run_dashboard.bat
```

### C. Pasang ke Startup Windows (Otomatis Aktif Saat PC Nyala)
Buka PowerShell dan jalankan:
```powershell
powershell -ExecutionPolicy Bypass -File install_autostart.ps1
```

---

## 🌐 Akses Web Dashboard

- **Di Komputer (PC)**: [http://localhost:8000](http://localhost:8000)
- **Di Smartphone (HP)**: `http://192.168.0.102:8000` *(pastikan HP & PC terhubung ke Wi-Fi yang sama)*

---

## ⚙️ Konfigurasi `.env`

File `.env` tersimpan aman di direktori lokal PC (tidak terunggah ke git public):
```env
GITHUB_USERNAME=Tryton47
PROJECT_PATH=D:\scrapton-3platform
MIN_COMMITS=9
REMINDER_HOUR=18
TELEGRAM_BOT_TOKEN=9104924567:AAHItsz9WMl6J17v5MQC7Ec0cscHtkwTBj0
TELEGRAM_CHAT_ID=9288483071
```
