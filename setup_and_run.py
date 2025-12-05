#!/usr/bin/env python3
"""
Setup and run script for Version Tracker Application
"""

import subprocess
import sys
import os

def main():
    print("=" * 60)
    print("Version Tracker - Setup and Run")
    print("=" * 60)
    
    # Change to project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("\n[1/3] Upgrading SQLAlchemy...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "SQLAlchemy"])
        print("✓ SQLAlchemy upgraded successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to upgrade SQLAlchemy: {e}")
        return 1
    
    print("\n[2/3] Creating .env file if not exists...")
    if not os.path.exists(".env"):
        with open(".env", "w", encoding="utf-8") as f:
            f.write("""FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production
DEBUG=True
DATABASE_URL=sqlite:///version_tracker.db
GITHUB_TOKEN=
""")
        print("✓ Created .env file")
    else:
        print("✓ .env file already exists")
    
    print("\n[3/3] Starting application...")
    print("=" * 60)
    print("Opening http://localhost:5000 in your browser...")
    print("=" * 60)
    
    try:
        subprocess.call([sys.executable, "run.py"])
    except KeyboardInterrupt:
        print("\n\nApplication stopped.")
        return 0
    except Exception as e:
        print(f"\n✗ Error running application: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
