#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-deployment script for VideoMusic Generator
Automatically commits, pushes and deploys without user interaction
"""

import subprocess
import sys
import os

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Configuration
SERVER = "root@158.220.94.179"
PASSWORD = "MasKil0s"
REMOTE_PATH = "~/videomusic/videomusic-generator/road_to_production"

def run_command(cmd, shell=True, capture=False):
    """Run a command and return result"""
    try:
        if capture:
            result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, encoding='utf-8')
            return result.returncode, result.stdout, result.stderr
        else:
            result = subprocess.run(cmd, shell=shell)
            return result.returncode, "", ""
    except Exception as e:
        print(f"[ERROR] Error running command: {e}")
        return 1, "", str(e)

def main():
    print("=" * 50)
    print("  VideoMusic Generator - Auto Deploy")
    print("=" * 50)

    # Get current directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_dir = os.path.dirname(script_dir)

    os.chdir(repo_dir)

    # Check if there are changes to commit
    print("\n[*] Checking for changes...")
    code, stdout, _ = run_command("git status --porcelain", capture=True)

    if stdout.strip():
        print("[+] Changes detected, committing...")
        run_command('git add -A')
        run_command('git commit -m "Auto-deploy: Latest changes"')
        print("[OK] Changes committed")
    else:
        print("[INFO] No local changes to commit")

    # Push to GitHub
    print("\n[*] Pushing to GitHub...")
    code, _, _ = run_command("git push")
    if code == 0:
        print("[OK] Pushed to GitHub")
    else:
        print("[WARN] Push may have failed, continuing...")

    # Deploy to server using SSH with password
    print(f"\n[*] Deploying to {SERVER}...")
    print("[*] This may take a few minutes...")

    # Try using sshpass if available
    code, stdout, stderr = run_command("sshpass -V", capture=True)

    if code == 0:
        # Use sshpass
        print("[OK] Using sshpass for automatic login")
        deploy_cmd = f'sshpass -p "{PASSWORD}" ssh -o StrictHostKeyChecking=no {SERVER} "cd {REMOTE_PATH} && bash update.sh"'
        code, stdout, stderr = run_command(deploy_cmd, capture=True)
    else:
        # Manual SSH - user needs to enter password
        print("[WARN] sshpass not available")
        print(f"[KEY] Please enter password when prompted: {PASSWORD}")
        deploy_cmd = f'ssh -o StrictHostKeyChecking=no {SERVER} "cd {REMOTE_PATH} && bash update.sh"'
        code, stdout, stderr = run_command(deploy_cmd, capture=False)

    if code == 0:
        print("\n" + "=" * 50)
        print("[SUCCESS] DEPLOYMENT SUCCESSFUL!")
        print("=" * 50)
        print(f"\n[WEB] Access your app at: http://158.220.94.179:8000")
        return 0
    else:
        print("\n" + "=" * 50)
        print("[FAILED] DEPLOYMENT FAILED")
        print("=" * 50)
        if stderr:
            print(f"Error: {stderr}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
