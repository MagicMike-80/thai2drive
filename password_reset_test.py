#!/usr/bin/env python3
"""
Simple test for password reset functionality
"""

import requests
import subprocess
import re
import time

BASE_URL = "https://www.thai2drive.no/api"
TEST_EMAIL = "resettest@thai2drive.com"

def test_password_reset():
    print("🔄 Testing password reset flow...")
    
    # 1. First create a user
    signup_data = {
        "email": TEST_EMAIL,
        "password": "originalpass123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
    if response.status_code != 200:
        print(f"❌ Failed to create test user: {response.status_code}")
        return False
    
    print(f"✅ Created test user: {TEST_EMAIL}")
    
    # 2. Request password reset
    forgot_data = {
        "email": TEST_EMAIL
    }
    
    response = requests.post(f"{BASE_URL}/auth/forgot-password", json=forgot_data)
    if response.status_code != 200:
        print(f"❌ Failed to request password reset: {response.status_code}")
        return False
    
    print("✅ Password reset requested")
    
    # 3. Get the reset code from logs
    time.sleep(1)  # Wait a moment for log to be written
    
    try:
        result = subprocess.run(
            ["tail", "-n", "20", "/var/log/supervisor/backend.err.log"],
            capture_output=True, text=True
        )
        
        reset_code = None
        for line in result.stdout.split('\n'):
            if "[MOCKED EMAIL]" in line and TEST_EMAIL in line:
                # Extract 6-digit code from the line
                match = re.search(r': (\d{6})$', line)
                if match:
                    reset_code = match.group(1)
                    break
        
        if not reset_code:
            print("❌ Could not find reset code in logs")
            return False
        
        print(f"✅ Found reset code: {reset_code}")
        
        # 4. Reset password with the code
        reset_data = {
            "email": TEST_EMAIL,
            "code": reset_code,
            "new_password": "newpassword123"
        }
        
        response = requests.post(f"{BASE_URL}/auth/reset-password", json=reset_data)
        if response.status_code != 200:
            print(f"❌ Failed to reset password: {response.status_code} - {response.text}")
            return False
        
        print("✅ Password reset successful")
        
        # 5. Test login with new password
        login_data = {
            "email": TEST_EMAIL,
            "password": "newpassword123"
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code != 200:
            print(f"❌ Failed to login with new password: {response.status_code}")
            return False
        
        print("✅ Login successful with new password")
        return True
        
    except Exception as e:
        print(f"❌ Error during password reset test: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_password_reset()
    print(f"\n🎯 Password reset test: {'PASSED' if success else 'FAILED'}")