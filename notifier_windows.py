"""
Windows Toast Notification Provider using PowerShell BurntToast or Windows WinRT fallback.
"""
import subprocess
from pathlib import Path

def send_windows_toast(title: str, message: str, project_path: str = r"D:\scrapton-3platform"):
    """
    Sends native Windows toast notification via PowerShell script.
    """
    ps_script = f"""
    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
    [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

    $template = @"
    <toast duration="long">
        <visual>
            <binding template="ToastGeneric">
                <text>{title}</text>
                <text>{message}</text>
                <text placement="attribution">GitHub Streak Sentinel</text>
            </binding>
        </visual>
        <actions>
            <action content="Buka Workspace" arguments="{project_path}" activationType="protocol"/>
        </actions>
    </toast>
"@

    $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
    $xml.LoadXml($template)
    $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
    [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("GitHub Sentinel").Show($toast)
    """

    try:
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, text=True, check=False)
    except Exception as e:
        print(f"Failed to show toast: {e}")
