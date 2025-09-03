#!/usr/bin/env python3
"""
Startup script for the AIDE backend server
"""

import os
import sys
import subprocess
import time

def main():
    """Main startup function"""
    print("🚀 Starting AIDE Backend Server...")
    print("=" * 50)
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Virtual environment not detected!")
        print("Please activate the virtual environment first:")
        print("   source env/bin/activate")
        print()
        return False
    
    print("✅ Virtual environment detected")
    
    # Check if required files exist
    required_files = [
        "app.py",
        "requirements.txt",
        "data/knowledge/academic_rules.json",
        "data/knowledge/procedures.csv",
        "data/knowledge/tools_and_instructions.txt"
    ]
    
    print("\n📁 Checking required files...")
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - MISSING!")
            return False
    
    # Check if .env file exists
    if not os.path.exists(".env"):
        print("\n⚠️  .env file not found!")
        print("Creating basic .env file...")
        env_content = """# Flask Configuration
FLASK_ENV=development
PORT=5001

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=aide_db
MONGODB_COLLECTIONS=users,documents,conversations,analytics

# RAG Configuration
RAG_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
RAG_EMBEDDING_DIMENSION=384
RAG_SIMILARITY_THRESHOLD=0.7
RAG_MAX_RESULTS=5

# Agent Configuration
AGENT_TIMEOUT=30
AGENT_MAX_RETRIES=3

# Groq API Key (optional - will use fallback if not provided)
GROQ_API_KEY=your_groq_api_key_here
"""
        try:
            with open(".env", "w") as f:
                f.write(env_content)
            print("   ✅ .env file created")
        except Exception as e:
            print(f"   ❌ Failed to create .env file: {e}")
            return False
    else:
        print("   ✅ .env file exists")
    
    # Install dependencies if needed
    print("\n📦 Checking dependencies...")
    try:
        import chromadb
        print("   ✅ ChromaDB available")
    except ImportError:
        print("   ⚠️  ChromaDB not available, installing dependencies...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
            print("   ✅ Dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to install dependencies: {e}")
            return False
    
    # Check MongoDB connection (optional)
    print("\n🗄️  Checking MongoDB connection...")
    try:
        import pymongo
        client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("   ✅ MongoDB connection successful")
        client.close()
    except Exception as e:
        print(f"   ⚠️  MongoDB connection failed: {e}")
        print("   Note: The app will still run but MongoDB features will be limited")
    
    print("\n🎯 All checks completed!")
    print("\nStarting Flask server...")
    print("=" * 50)
    
    # Start the Flask server
    try:
        subprocess.run([sys.executable, "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Server failed to start: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
