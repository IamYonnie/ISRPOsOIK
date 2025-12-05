# MIT License
# Simple runner script for development

import os
import sys

# Set environment variables before importing Flask
os.environ.setdefault('FLASK_ENV', 'development')
os.environ.setdefault('GITHUB_TOKEN', 'dev-token')
os.environ.setdefault('DEBUG', 'True')

try:
    from app import create_app
    
    if __name__ == '__main__':
        app = create_app()
        print("=" * 60)
        print("Version Tracker Application")
        print("=" * 60)
        print("Starting development server...")
        print("Open http://localhost:5000 in your browser")
        print("Press Ctrl+C to stop")
        print("=" * 60)
        app.run(debug=True, host='0.0.0.0', port=5000)
        
except ImportError as e:
    print(f"Error: {e}")
    print("\nPlease install dependencies:")
    print("pip install -r requirements.txt")
    sys.exit(1)
