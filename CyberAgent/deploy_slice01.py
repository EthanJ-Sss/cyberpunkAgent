#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
部署脚本 - 将 AI 画家交易市场切片网页部署到服务器
"""
import paramiko
import os
import sys
import io
import time

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ============================================================
# 配置区域
# ============================================================
SERVER = "43.173.170.5"
PORT = 22
USERNAME = "ubuntu"
PASSWORD = "MTc1MjA0NDQ0MQ"
REMOTE_PATH = "/var/www/slice01-painter-market"
LOCAL_FILES = ["slice_01.html"]
WEB_PORT = 4186
SERVICE_NAME = "slice01-painter-market"
# ============================================================

def main():
    print("=" * 50)
    print("  Slice 01: AI Painter Market - Deploy")
    print("=" * 50)
    print(f"\n  Server:  {SERVER}")
    print(f"  Port:    {WEB_PORT}")
    print(f"  Path:    {REMOTE_PATH}")
    print()

    for f in LOCAL_FILES:
        if not os.path.exists(f):
            print(f"Error: {f} not found!")
            return False

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # 1. 连接服务器
        print("[1/6] Connecting to server...")
        ssh.connect(SERVER, PORT, USERNAME, PASSWORD, timeout=30)
        print("  OK - Connected!")

        # 2. 准备远程目录
        print("[2/6] Preparing remote directory...")
        commands = [
            f"sudo mkdir -p {REMOTE_PATH}",
            f"sudo chown -R {USERNAME}:{USERNAME} {REMOTE_PATH}",
        ]
        for cmd in commands:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            stdout.read()
        print("  OK - Directory ready!")

        # 3. 上传文件（将 slice_01.html 重命名为 index.html 以便 serve 默认访问）
        print("[3/6] Uploading files...")
        sftp = ssh.open_sftp()
        total_size = 0
        for local_file in LOCAL_FILES:
            # slice_01.html -> index.html (serve 默认入口)
            remote_name = "index.html" if local_file == "slice_01.html" else os.path.basename(local_file)
            remote_file = f"{REMOTE_PATH}/{remote_name}"
            sftp.put(local_file, remote_file)
            fsize = os.path.getsize(local_file)
            total_size += fsize
            print(f"  -> {local_file} => {remote_name} ({fsize:,} bytes)")
        sftp.close()
        print(f"  OK - Uploaded {len(LOCAL_FILES)} files ({total_size:,} bytes total)")

        # 4. 确保 serve 已安装
        print("[4/6] Checking serve...")
        stdin, stdout, stderr = ssh.exec_command("which serve")
        serve_path = stdout.read().decode().strip()
        if not serve_path:
            print("  Installing serve...")
            stdin, stdout, stderr = ssh.exec_command("sudo npm install -g serve 2>&1")
            output = stdout.read().decode()
            print(f"  {output.strip()[-80:]}")
            stdin, stdout, stderr = ssh.exec_command("which serve")
            serve_path = stdout.read().decode().strip()
        print(f"  OK - serve at {serve_path}")

        # 5. 配置 systemd 服务
        print("[5/6] Configuring systemd service...")
        service_content = f"""[Unit]
Description=Slice01 AI Painter Market Web Service
After=network.target

[Service]
Type=simple
User={USERNAME}
WorkingDirectory={REMOTE_PATH}
ExecStart={serve_path} -s . -l {WEB_PORT}
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
"""
        sftp = ssh.open_sftp()
        with sftp.file(f"/tmp/{SERVICE_NAME}.service", "w") as f:
            f.write(service_content)
        sftp.close()

        service_commands = [
            f"sudo mv /tmp/{SERVICE_NAME}.service /etc/systemd/system/{SERVICE_NAME}.service",
            "sudo systemctl daemon-reload",
            f"pkill -f 'serve.*{WEB_PORT}' 2>/dev/null || true",
            f"sudo systemctl enable {SERVICE_NAME} 2>/dev/null",
            f"sudo systemctl restart {SERVICE_NAME}",
        ]
        for cmd in service_commands:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            stdout.read()
        time.sleep(3)
        print("  OK - Service configured!")

        # 6. 验证服务
        print("[6/6] Verifying service...")
        stdin, stdout, stderr = ssh.exec_command(f"sudo systemctl is-active {SERVICE_NAME}")
        status = stdout.read().decode().strip()
        print(f"  Service status: {status}")

        stdin, stdout, stderr = ssh.exec_command(f"ss -tlnp | grep {WEB_PORT}")
        port_check = stdout.read().decode().strip()

        if str(WEB_PORT) in port_check:
            print(f"  OK - Port {WEB_PORT} is listening!")
        else:
            print(f"  WARN - Port {WEB_PORT} not detected yet, checking logs...")
            stdin, stdout, stderr = ssh.exec_command(f"sudo journalctl -u {SERVICE_NAME} --no-pager -n 10")
            logs = stdout.read().decode()
            print(f"  Logs:\n{logs}")

        # 开放防火墙端口
        stdin, stdout, stderr = ssh.exec_command(f"sudo ufw allow {WEB_PORT} 2>/dev/null; echo done")
        stdout.read()

        print()
        print("=" * 50)
        print("  DEPLOYMENT COMPLETE!")
        print(f"  URL: http://{SERVER}:{WEB_PORT}")
        print("=" * 50)
        return True

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        ssh.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
