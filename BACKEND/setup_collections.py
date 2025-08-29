#!/usr/bin/env python3
"""
Setup script to create PocketBase collections and sample data
Run this after starting PocketBase for the first time
"""

import requests
import json
import time
import sys
from datetime import datetime

POCKETBASE_URL = "http://localhost:8090"

def wait_for_pocketbase():
    """Wait for PocketBase to be ready"""
    print("Waiting for PocketBase to be ready...")
    for i in range(30):
        try:
            response = requests.get(f"{POCKETBASE_URL}/api/health", timeout=5)
            if response.status_code == 200:
                print("PocketBase is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        time.sleep(2)
        print(f"   Attempt {i+1}/30...")
    
    print("PocketBase not responding after 60 seconds")
    return False

def setup_admin():
    """Setup admin user"""
    print("Setting up admin user...")
    
    try:
        # Check if admin exists
        response = requests.get(f"{POCKETBASE_URL}/api/admins", timeout=5)
        if response.status_code == 200 and response.json().get("items"):
            print("Admin user already exists")
            return True
    except:
        pass
    
    # Create admin user
    admin_data = {
        "email": "admin@playright.ai",
        "password": "admin123",
        "passwordConfirm": "admin123"
    }
    
    try:
        response = requests.post(f"{POCKETBASE_URL}/api/admins", json=admin_data, timeout=10)
        if response.status_code in [200, 201]:
            print("Admin user created: admin@playright.ai / admin123")
            print("IMPORTANT: Change the admin password in production!")
            return True
        else:
            print(f"Failed to create admin: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error creating admin: {str(e)}")
        return False

def check_collections():
    """Check if collections exist"""
    print("Checking collections...")
    
    try:
        response = requests.get(f"{POCKETBASE_URL}/api/collections", timeout=10)
        if response.status_code == 200:
            collections = response.json().get("items", [])
            collection_names = [c["name"] for c in collections]
            
            expected = ["users", "athletes", "brands", "deals", "campaigns", "athlete_metrics"]
            existing = [name for name in expected if name in collection_names]
            missing = [name for name in expected if name not in collection_names]
            
            print(f"Found collections: {existing}")
            if missing:
                print(f"Missing collections: {missing}")
                print("   Collections will be created by migrations when PocketBase restarts")
            
            return True
    except Exception as e:
        print(f"Error checking collections: {str(e)}")
        return False

def create_sample_data():
    """Create sample users and data"""
    print("Creating sample data...")
    
    # Sample athlete user
    athlete_user = {
        "email": "marcus.johnson@university.edu",
        "password": "athlete123",
        "passwordConfirm": "athlete123",
        "role": "athlete",
        "verified": True,
        "profile_completed": True
    }
    
    # Sample brand user  
    brand_user = {
        "email": "nike.local@nike.com",
        "password": "brand123",
        "passwordConfirm": "brand123", 
        "role": "brand",
        "verified": True,
        "profile_completed": True
    }
    
    try:
        # Try to create sample users (may fail if collections not ready)
        for user_data in [athlete_user, brand_user]:
            try:
                response = requests.post(f"{POCKETBASE_URL}/api/collections/users/records", json=user_data, timeout=10)
                if response.status_code in [200, 201]:
                    print(f"Created user: {user_data['email']}")
                else:
                    print(f"Could not create user {user_data['email']}: {response.status_code}")
            except Exception as e:
                print(f"Error creating user {user_data['email']}: {str(e)}")
        
        print("Sample data creation attempted")
        print("   Complete setup by visiting the admin panel and creating collections manually if needed")
        
    except Exception as e:
        print(f"Sample data creation failed: {str(e)}")

def main():
    print("PlayRight Backend Setup")
    print("=" * 50)
    
    # Wait for PocketBase
    if not wait_for_pocketbase():
        sys.exit(1)
    
    # Setup admin  
    setup_admin()
    
    # Check collections
    check_collections()
    
    # Create sample data
    create_sample_data()
    
    print("\n" + "=" * 50)
    print("Setup complete!")
    print(f"PocketBase Admin: {POCKETBASE_URL}/_/")
    print(f"API Docs: http://localhost:3001/docs (start API server)")
    print(f"AI Engine: http://localhost:8000/docs (start AI engine)")
    print("\nNext steps:")
    print("   1. Visit PocketBase admin panel to verify collections")
    print("   2. Start the API server: cd api-server && python -m uvicorn app.main:app --reload --port 3001")
    print("   3. Test the endpoints!")

if __name__ == "__main__":
    main()