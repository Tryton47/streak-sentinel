"""
Remote Controller for GitHub Streak Sentinel.
Processes commands sent remotely from Mobile (WhatsApp, Telegram, or Web UI).
"""
import os
import subprocess
from datetime import datetime
from github_checker import GitHubStreakChecker
from notifier_whatsapp import send_whatsapp_notification
from notifier_windows import send_windows_toast

class RemoteController:
    def __init__(self):
        self.username = os.getenv("GITHUB_USERNAME", "Tryton47")
        self.project_path = os.getenv("PROJECT_PATH", r"D:\scrapton-3platform")
        self.min_commits = int(os.getenv("MIN_COMMITS", "9"))

    def execute_command(self, raw_cmd: str, sender: str = "mobile") -> str:
        """
        Parses and runs command from smartphone.
        Supports commands starting with '!' or '/' or plain words.
        """
        cmd_clean = raw_cmd.strip()
        parts = cmd_clean.split(maxsplit=1)
        if not parts:
            return "Ketik '!help' untuk melihat daftar perintah yang tersedia."

        action = parts[0].lower().lstrip("!/").strip()
        arg = parts[1].strip() if len(parts) > 1 else ""

        if action in ("status", "stat", "cek"):
            return self._handle_status()
        elif action in ("check", "forcecheck", "scan"):
            return self._handle_force_check()
        elif action in ("open", "vscode", "code"):
            return self._handle_open_workspace()
        elif action in ("commit", "push", "save", "emergency"):
            return self._handle_emergency_commit(arg)
        elif action in ("web", "dashboard", "link", "url"):
            return self._handle_web_link()
        elif action in ("ping", "p"):
            return self._handle_ping()
        elif action in ("cmd", "run", "exec", "sh"):
            return self._handle_run_command(arg)
        elif action in ("notif", "alert", "test"):
            return self._handle_test_notif()
        elif action in ("help", "bantuan", "menu"):
            return self._handle_help()
        else:
            return (
                f"Perintah '{action}' tidak dikenali.\n\n"
                "Ketik *!help* untuk melihat daftar remote command dari HP."
            )

    def _handle_status(self) -> str:
        checker = GitHubStreakChecker(self.username)
        committed, count, repos = checker.has_committed_today()
        target = int(os.getenv("MIN_COMMITS", str(self.min_commits)))
        now_str = datetime.now().strftime("%H:%M:%S WIB")
        remaining = max(0, target - count)

        repo_list = "\n- ".join(repos) if repos else "Belum ada repo tersentuh"

        if count >= target:
            return (
                f"🟢 *TARGET 9 COMMIT TERCAPAI!*\n"
                f"👤 Akun: @{self.username}\n"
                f"🔥 Total commit hari ini: *{count}/{target} commit* ✅\n"
                f"📦 Repositori aktif:\n- {repo_list}\n\n"
                f"🕒 Update: {now_str}\n"
                f"Streak & target harian aman! Kerja bagus! 🚀"
            )
        else:
            return (
                f"⚠️ *PERINGATAN TARGET COMMIT!*\n"
                f"👤 Akun: @{self.username}\n"
                f"📊 Progress: *{count}/{target} commit* (Kurang *{remaining}* commit lagi)\n"
                f"⏰ Deadline pengingat: Jam 18:00 WIB\n"
                f"🕒 Update: {now_str}\n\n"
                f"💡 Mau auto commit dari HP? Balas:\n"
                f"`!commit update progress harian`"
            )

    def _handle_force_check(self) -> str:
        status_msg = self._handle_status()
        checker = GitHubStreakChecker(self.username)
        committed, count, _ = checker.has_committed_today()
        target = int(os.getenv("MIN_COMMITS", str(self.min_commits)))

        if count < target:
            send_windows_toast(
                title=f"🚨 Target {target} Commit Belum Terpenuhi!",
                message=f"Hari ini baru {count}/{target} commit. Kurang {target - count} lagi sebelum jam 18:00 WIB!",
                project_path=self.project_path
            )
        return status_msg

    def _handle_open_workspace(self) -> str:
        """Opens project in VS Code or Windows Explorer on host machine."""
        if not os.path.exists(self.project_path):
            return f"❌ Folder project `{self.project_path}` tidak ditemukan di komputer."

        try:
            subprocess.Popen(["code", self.project_path], shell=True)
            return f"💻 *Berhasil Membuka Workspace!*\nVS Code telah dibuka di PC untuk project: `{self.project_path}`"
        except Exception:
            try:
                os.startfile(self.project_path)
                return f"📁 Explorer PC telah dibuka pada `{self.project_path}`"
            except Exception as e:
                return f"❌ Gagal membuka workspace di PC: {e}"

    def _handle_emergency_commit(self, custom_msg: str) -> str:
        """
        Emergency commit from mobile to prevent streak loss.
        Appends entry to streak_log.txt and executes git add, commit, push.
        """
        target_dir = self.project_path
        if not os.path.exists(target_dir):
            target_dir = os.path.dirname(os.path.abspath(__file__))

        commit_message = custom_msg or f"chore(streak): sentinel mobile update [{datetime.now().strftime('%Y-%m-%d %H:%M')}]"
        log_file = os.path.join(target_dir, "STREAK_LOG.md")

        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"- 🚀 Sentinel Mobile Commit at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} WIB: {commit_message}\n")

            # Git add
            subprocess.run(["git", "add", "STREAK_LOG.md"], cwd=target_dir, check=True, capture_output=True)
            # Git commit
            subprocess.run(["git", "commit", "-m", commit_message], cwd=target_dir, check=True, capture_output=True)
            # Git push
            push_res = subprocess.run(["git", "push"], cwd=target_dir, check=True, capture_output=True, text=True)

            checker = GitHubStreakChecker(self.username)
            _, count, _ = checker.has_committed_today()
            target = int(os.getenv("MIN_COMMITS", "9"))

            return (
                f"✅ *COMMIT BERHASIL DARI HP!*\n"
                f"📝 Pesan: `{commit_message}`\n"
                f"📊 Progress sekarang: *{count}/{target} commit*\n"
                f"🔥 Streak GitHub kamu tetap aman!"
            )
        except subprocess.CalledProcessError as e:
            err = e.stderr.decode() if isinstance(e.stderr, bytes) else str(e)
            return f"⚠️ Git error saat commit/push: {err[:200]}"
        except Exception as e:
            return f"❌ Gagal melakukan emergency commit: {str(e)}"

    def _handle_web_link(self) -> str:
        return (
            "🌐 *Link Dashboard Apple Glass Sentinel*\n\n"
            "• *Dari HP (Wi-Fi):* http://192.168.0.102:8000\n"
            "• *Dari PC:* http://localhost:8000\n\n"
            "💡 _Buka link HP di Safari/Chrome, lalu tap 'Add to Home Screen' agar jadi seperti aplikasi iPhone/Android!_"
        )

    def _handle_ping(self) -> str:
        now_str = datetime.now().strftime("%H:%M:%S WIB")
        return (
            f"🏓 *Pong!*\n"
            f"⚡ Koneksi Bot: *Online & Responsif*\n"
            f"👤 Akun GitHub: @{self.username}\n"
            f"💻 Host: Windows PC\n"
            f"🕒 Server Time: {now_str}"
        )

    def _handle_run_command(self, cmd: str) -> str:
        if not cmd:
            return "⚠️ Mohon sertakan perintah yang ingin dijalankan.\nContoh: `/cmd git status` atau `/cmd python main.py`"

        target_dir = self.project_path if os.path.exists(self.project_path) else os.path.dirname(os.path.abspath(__file__))

        try:
            res = subprocess.run(cmd, shell=True, cwd=target_dir, capture_output=True, text=True, timeout=15)
            output = (res.stdout or res.stderr or "Perintah dieksekusi tanpa output.").strip()
            # Trim if too long
            if len(output) > 800:
                output = output[:800] + "\n...(output dipotong)"
            return f"💻 *Output Terminal ({target_dir}):*\n```\n{output}\n```"
        except subprocess.TimeoutExpired:
            return "⏳ Perintah timeout (melebihi batas waktu 15 detik)."
        except Exception as e:
            return f"❌ Gagal menjalankan perintah: {str(e)}"

    def _handle_test_notif(self) -> str:
        target = int(os.getenv("MIN_COMMITS", "9"))
        phone = os.getenv("WHATSAPP_PHONE", "")
        fonnte = os.getenv("FONNTE_TOKEN", "")

        send_windows_toast(
            title=f"🔔 Test Sentinel (Target {target} Commit)",
            message="Sistem aktif! Peringatan dikirim jam 18:00 WIB jika < 9 commit.",
            project_path=self.project_path
        )

        if phone and fonnte:
            send_whatsapp_notification(
                message=f"🔔 *Test Notifikasi WhatsApp Sentinel*\nSistem aktif! Target harian: minimal {target} commit (bebas di project mana saja).\nJika belum capai {target} commit sampai jam 18:00 WIB, notifikasi akan dikirim ke sini."
            )

        return "✅ Notifikasi uji coba telah ditembakkan ke layar PC & WhatsApp."

    def _handle_help(self) -> str:
        target = int(os.getenv("MIN_COMMITS", "9"))
        return (
            f"📱 *REMOTE SENTINEL COMMANDS (DARI HP)*\n\n"
            f"🎯 *Target Harian*: Minimal {target} Commit (bebas repo mana pun)\n"
            f"⏰ *Deadline Notif*: Jam 18:00 WIB jika belum {target} commit\n\n"
            "• `/status` - Cek progress commit hari ini (misal: 4/9)\n"
            "• `/check` - Scan langsung ke GitHub API & cek status\n"
            "• `/open` - Buka workspace di komputer PC dari jarak jauh\n"
            "• `/commit <pesan>` - Auto-commit & push langsung dari chat HP\n"
            "• `/ping` - Cek koneksi & latensi bot ke PC\n"
            "• `/web` - Tampilkan link dashboard Apple Glass\n"
            "• `/cmd <perintah>` - Jalankan command terminal di project PC\n"
            "• `/notif` - Tes kirim notifikasi ke PC & Telegram\n"
            "• `/help` - Tampilkan panduan ini\n\n"
            "💡 _Bisa diawali tanda seru (!) atau slash (/), contoh: /status_"
        )
