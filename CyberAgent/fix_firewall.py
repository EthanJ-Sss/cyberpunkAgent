#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
开放防火墙端口
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
    
    # 开放端口 4180 和 4185
    ports = [4180, 4185]
    
    for port in ports:
        print(f"Opening port {port}...")
        stdin, stdout, stderr = ssh.exec_command(f"sudo ufw allow {port}")
        result = stdout.read().decode()
        error = stderr.read().decode()
        print(result if result else error)
    
    # 重新加载防火墙
    print("\nReloading firewall...")
    stdin, stdout, stderr = ssh.exec_command("sudo ufw reload")
    result = stdout.read().decode()
    print(result)
    
    # 检查状态
    print("\nChecking firewall status...")
    stdin, stdout, stderr = ssh.exec_command("sudo ufw status | grep -E '4180|4185'")
    result = stdout.read().decode()
    print(result if result else "Ports not found in firewall rules")
    
    print("\n" + "=" * 50)
    print("  FIREWALL CONFIGURED!")
    print("=" * 50)
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
