# 🛡️ GitHub Streak Sentinel — Apple Glass Edition 🍏

Sistem penjaga streak GitHub otomatis dengan tampilan **Liquid Frosted Glass ala Apple macOS / iOS**, notifikasi real-time ke **WhatsApp**, dan fitur **Remote Control dari Smartphone**!

---

## ✨ Fitur Unggulan

### 1. 🍏 Apple Liquid Glassmorphism Dashboard
- Desain antarmuka transparan frosted glass mewah berbasis **macOS Sequoia / iOS 18**.
- Background ambient mesh dinamis dengan aksen glow & SF Pro typography.
- Status streak real-time: indikator cincin api animasi (Safe vs At Risk), commit counter hari ini, dan daftar repositori aktif.
- **Konsol Terminal Glass**: Eksekusi perintah langsung di web UI.

### 2. 📱 Akses & Kontrol Penuh dari HP (Smartphone)
- Cukup buka browser HP di `http://192.168.0.102:8000` (atau IP lokal Wi-Fi PC kamu).
- Responsive: Terasa seperti aplikasi widget native iOS di smartphone.
- Tombol aksi sekali sentuh dari HP:
  - ⚡ **Periksa Sekarang**: Scan live API GitHub detik ini.
  - 💬 **Kirim Notifikasi WA**: Tes tembak alert ke WhatsApp & layar PC.
  - 💻 **Buka di VS Code**: Luncurkan editor workspace di komputer dari jarak jauh!
  - 🚀 **Emergency Commit**: Auto-commit & git push instan dari HP untuk menyelamatkan grafik commit hijau.

### 3. 💬 Integrasi WhatsApp 2-Way Bot
- Notifikasi pengingat otomatis jika belum ada commit hingga jam target (misal jam 19.00 malam).
- **Remote Commands**: Kamu bisa balas chat WhatsApp dari HP dengan perintah:
  - `!status` : Cek apakah streak hari ini sudah aman
  - `!check`  : Scan GitHub & picu notifikasi
  - `!open`   : Buka project di VS Code PC kamu
  - `!commit <pesan>` : Auto-commit darurat dari WhatsApp!

---

## 🚀 Cara Menjalankan

### A. Melalui Double-Click (Paling Mudah di Windows)
Klik dua kali file:
```
run_dashboard.bat
```

### B. Melalui Terminal / Command Prompt
```bash
# Jalankan Apple Glass Dashboard & Remote Server
python main.py --server

# Atau jalankan scan CLI biasa
python main.py
```

Buka URL berikut:
- **Di Komputer (PC)**: [http://localhost:8000](http://localhost:8000)
- **Di Smartphone (HP)**: `http://192.168.0.102:8000` *(pastikan HP & PC di Wi-Fi yang sama)*

---

## ⚙️ Pengaturan WhatsApp di `.env`

Edit file `.env` (atau ubah langsung melalui menu Pengaturan ⚙️ di Glass UI Dashboard):
```env
GITHUB_USERNAME=Tryton47
PROJECT_PATH=D:\scrapton-3platform
WHATSAPP_PHONE=08xxxxxxxxxx
FONNTE_TOKEN=your_token_from_fonnte
REMINDER_HOUR=19
```

> 💡 *Untuk WhatsApp Gateway gratis & cepat di Indonesia, kamu bisa mendaftar akun di [fonnte.com](https://fonnte.com), lalu salin Token ke `.env`.*
