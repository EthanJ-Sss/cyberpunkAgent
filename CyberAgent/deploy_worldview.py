#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
部署世界观设定页面到服务器
"""
import paramiko
import os
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

SERVER = "43.173.170.5"
PORT = 22
USERNAME = "ubuntu"
PASSWORD = "MTc1MjA0NDQ0MQ"
REMOTE_PATH = "/var/www/cyberagent-worldview"
LOCAL_FILE = "Agent_赛博朋克2077_世界观设定.html"
WEB_PORT = 4188
SERVICE_NAME = "cyberagent-worldview"

def main():
    print("=" * 50)
    print("  Deploy 世界观设定")
    print("=" * 50)
    print(f"\nServer: {SERVER}")
    print(f"Target Port: {WEB_PORT}")
    print(f"Remote Path: {REMOTE_PATH}")
    print()
    
    if not os.path.exists(LOCAL_FILE):
        print(f"Error: {LOCAL_FILE} not found!")
        return False
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print("Connecting to server...")
        ssh.connect(SERVER, PORT, USERNAME, PASSWORD, timeout=30)
        print("[OK] Connected!")
        
        print("\nPreparing remote directory...")
        ssh.exec_command(f"sudo mkdir -p {REMOTE_PATH}")
        ssh.exec_command(f"sudo chown -R {USERNAME}:{USERNAME} {REMOTE_PATH}")
        print("[OK] Directory ready!")
        
        print(f"\nUploading {LOCAL_FILE}...")
        sftp = ssh.open_sftp()
        sftp.put(LOCAL_FILE, f"{REMOTE_PATH}/index.html")
        sftp.close()
        print("[OK] Upload complete!")
        
        print("\nStopping old services...")
        ssh.exec_command(f"pkill -f 'serve.*{WEB_PORT}' 2>/dev/null || true")
        import time
        time.sleep(2)
        
        print("\nStarting service...")
        cmd = f"cd {REMOTE_PATH} && nohup serve -s . -l {WEB_PORT} > /tmp/{SERVICE_NAME}.log 2>&1 &"
        ssh.exec_command(cmd)
        time.sleep(3)
        
        print("\nOpening firewall port...")
        ssh.exec_command(f"sudo ufw allow {WEB_PORT}")
        time.sleep(1)
        
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
