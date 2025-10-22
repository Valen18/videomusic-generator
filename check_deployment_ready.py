#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pre-deployment checker for VideoMusic Generator
Verifies all necessary files are present before deployment
"""

import os
import sys
from pathlib import Path

# Fix encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"[OK] {description}: {filepath}")
        return True
    else:
        print(f"[MISSING] {description}: {filepath}")
        return False

def check_deployment_readiness():
    """Check if all deployment files are ready"""
    print("Checking deployment readiness...\n")

    required_files = [
        ("Dockerfile", "Dockerfile"),
        ("Docker Compose", "docker-compose.yml"),
        (".dockerignore", ".dockerignore"),
        ("Production Requirements", "requirements-prod.txt"),
        ("Environment Template", ".env.example"),
        (".gitignore", ".gitignore"),
        ("Main Application", "web_app_secure.py"),
    ]

    documentation_files = [
        ("Quick Start Guide", "QUICK_START_DOKPLOY.md"),
        ("Deployment Guide", "DEPLOYMENT_DOKPLOY.md"),
        ("Deployment Summary", "DEPLOYMENT_SUMMARY.md"),
    ]

    all_good = True

    print("Required Files:")
    for desc, filepath in required_files:
        if not check_file_exists(filepath, desc):
            all_good = False

    print("\nDocumentation:")
    for desc, filepath in documentation_files:
        check_file_exists(filepath, desc)

    print("\nAdditional Checks:")

    # Check if web directory exists
    if os.path.exists("web"):
        print("[OK] Web directory exists")

        # Check key web files
        web_files = ["index.html", "app_secure.js", "styles.css"]
        for wf in web_files:
            web_path = f"web/{wf}"
            if os.path.exists(web_path):
                print(f"  [OK] {wf}")
            else:
                print(f"  [MISSING] {wf}")
                all_good = False
    else:
        print("[ERROR] Web directory not found!")
        all_good = False

    # Check if src directory structure exists
    if os.path.exists("src"):
        print("[OK] Source directory exists")
    else:
        print("[ERROR] Source directory not found!")
        all_good = False

    print("\n" + "="*50)

    if all_good:
        print("SUCCESS - ALL CHECKS PASSED!")
        print("\nYour application is ready for deployment!")
        print("\nNext steps:")
        print("   1. Initialize git: git init")
        print("   2. Add files: git add .")
        print("   3. Commit: git commit -m 'Ready for deployment'")
        print("   4. Push to GitHub/GitLab")
        print("   5. Configure in Dokploy")
        print("\nSee QUICK_START_DOKPLOY.md for details")
        return True
    else:
        print("ERROR - SOME CHECKS FAILED!")
        print("\nPlease fix the missing files before deployment")
        return False

if __name__ == "__main__":
    success = check_deployment_readiness()
    sys.exit(0 if success else 1)
