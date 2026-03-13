#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查服务器上的服务状态
"""
import paramiko
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

SERVER = "43.173.170.5"
PORT = 22
USERNAME = "ubuntu"
PASSWORD = "MTc1MjA0NDQ0MQ"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("Connecting to server...")
    ssh.connect(SERVER, PORT, USERNAME, PASSWORD, timeout=30)
    print("[OK] Connected!\n")
    
    # 检查端口 4180
    print("=" * 50)
    print("Checking port 4180...")
    print("=" * 50)
    stdin, stdout, stderr = ssh.exec_command("ss -tlnp | grep 4180 || netstat -tlnp | grep 4180")
    result = stdout.read().decode()
    print(result if result else "No service on port 4180")
    
    # 检查进程
    print("\n" + "=" * 50)
    print("Checking serve processes...")
    print("=" * 50)
    stdin, stdout, stderr = ssh.exec_command("ps aux | grep serve | grep -v grep")
    result = stdout.read().decode()
    print(result if result else "No serve processes running")
    
    # 检查日志
    print("\n" + "=" * 50)
    print("Checking log file...")
    print("=" * 50)
    stdin, stdout, stderr = ssh.exec_command("tail -20 /tmp/cyberagent-hub.log 2>&1")
    result = stdout.read().decode()
    print(result if result else "No log file found")
    
    # 检查目录
    print("\n" + "=" * 50)
    print("Checking remote directory...")
    print("=" * 50)
    stdin, stdout, stderr = ssh.exec_command("ls -la /var/www/cyberagent-hub/")
    result = stdout.read().decode()
    print(result)
    
    # 检查防火墙
    print("\n" + "=" * 50)
    print("Checking firewall...")
    print("=" * 50)
    stdin, stdout, stderr = ssh.exec_command("sudo ufw status | grep 4180")
    result = stdout.read().decode()
    print(result if result else "Port 4180 not in firewall rules")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
