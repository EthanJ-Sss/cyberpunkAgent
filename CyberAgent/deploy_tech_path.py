#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
部署 Trumen_Legos_技术结构路径.html 到服务器
使用方法: python deploy_tech_path.py
"""
import paramiko
import os
import sys
import io

# Windows 控制台编码修复
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
REMOTE_PATH = "/var/www/cyberagent-tech-path"
LOCAL_FILE = "Trumen_Legos_技术结构路径.html"
WEB_PORT = 4187  # 选择空闲端口 4187
SERVICE_NAME = "cyberagent-tech-path"
# ============================================================

def main():
    print("=" * 50)
    print("  Deploy Trumen Legos 技术结构路径")
    print("=" * 50)
    print(f"\nServer: {SERVER}")
    print(f"Target Port: {WEB_PORT}")
    print(f"Remote Path: {REMOTE_PATH}")
    print()
    
    # 检查本地文件
    if not os.path.exists(LOCAL_FILE):
        print(f"Error: {LOCAL_FILE} not found!")
        return False
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # 连接服务器
        print("Connecting to server...")
        ssh.connect(SERVER, PORT, USERNAME, PASSWORD, timeout=30)
        print("[OK] Connected!")
        
        # 准备远程目录
        print("\nPreparing remote directory...")
        ssh.exec_command(f"sudo mkdir -p {REMOTE_PATH}")
        ssh.exec_command(f"sudo chown -R {USERNAME}:{USERNAME} {REMOTE_PATH}")
        print("[OK] Directory ready!")
        
        # 上传文件
        print(f"\nUploading {LOCAL_FILE}...")
        sftp = ssh.open_sftp()
        sftp.put(LOCAL_FILE, f"{REMOTE_PATH}/index.html")
        sftp.close()
        print("[OK] Upload complete!")
        
        # 停止旧服务
        print("\nStopping old services...")
        ssh.exec_command(f"pkill -f 'serve.*{WEB_PORT}' 2>/dev/null || true")
        ssh.exec_command(f"pkill -f 'python.*http.server.*{WEB_PORT}' 2>/dev/null || true")
        import time
        time.sleep(2)
        
        # 检查 serve 是否安装
        print("\nChecking 'serve' installation...")
        stdin, stdout, stderr = ssh.exec_command("which serve")
        serve_path = stdout.read().decode().strip()
        
        if not serve_path:
            print("Installing 'serve'...")
            stdin, stdout, stderr = ssh.exec_command("sudo npm install -g serve 2>&1")
            stdout.read()
            print("[OK] Installed!")
        
        # 启动服务
        print("Starting service...")
        cmd = f"cd {REMOTE_PATH} && nohup serve -s . -l {WEB_PORT} > /tmp/{SERVICE_NAME}.log 2>&1 &"
        ssh.exec_command(cmd)
        time.sleep(3)
        
        # 开放防火墙端口
        print("\nOpening firewall port...")
        ssh.exec_command(f"sudo ufw allow {WEB_PORT}")
        time.sleep(1)
        
        # 验证服务
        print("\nVerifying service...")
        stdin, stdout, stderr = ssh.exec_command(f"ss -tlnp | grep {WEB_PORT} || netstat -tlnp | grep {WEB_PORT}")
        result = stdout.read().decode()
        
        if str(WEB_PORT) in result:
            print("[OK] Service is running!")
        else:
            print("[WARN] Service may not be running properly")
        
        print("\n" + "=" * 50)
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
