#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple server starter
"""
import sys
import os

if __name__ == "__main__":
    # Set UTF-8 encoding for Windows console
    if sys.platform == 'win32':
        os.system('chcp 65001 >nul 2>&1')

    print("\n" + "="*60)
    print("  VideoMusic Generator - Secure Web Application")
    print("="*60)
    print("\nStarting server...")
    print("URL: http://localhost:8000")
    print("\nDefault credentials:")
    print("  Username: admin")
    print("  Password: admin123")
    print("\n**CHANGE THE PASSWORD AFTER FIRST LOGIN!**\n")
    print("Press CTRL+C to stop the server\n")
    print("="*60 + "\n")

    # Run uvicorn directly
    import uvicorn

    try:
        uvicorn.run(
            "web_app_secure:app",
            host="127.0.0.1",
            port=8000,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        print("\nIf port 8000 is in use, try:")
        print("  netstat -ano | findstr :8000")
        print("  taskkill /F /PID <PID>")
