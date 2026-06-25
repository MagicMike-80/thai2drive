#!/usr/bin/env python3
"""
Thai2Drive Backend Auth API Testing
Tests all auth endpoints and verifies existing functionality still works
"""

import requests
import json
import time
import sys
from typing import Dict, Any, Optional

# Backend URL from frontend .env
BASE_URL = "https://www.thai2drive.no/api"

# Test credentials from /app/memory/test_credentials.md
TEST_USER_EMAIL = "test@thai2drive.com"
TEST_USER_PASSWORD = "test123"
ADMIN_USER_EMAIL = "admin@thai2drive.com"
ADMIN_USER_PASSWORD = "admin123"

class AuthTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_token = None
        self.admin_token = None
        self.results = []
        
    def log_result(self, test_name: str, success: bool, message: str, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "details": details
        })
        print(f"{status} {test_name}: {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None, token: str = None) -> tuple:
        """Make HTTP request and return (success, response_data, status_code)"""
        url = f"{BASE_URL}{endpoint}"
        
        # Set up headers
        req_headers = {"Content-Type": "application/json"}
        if headers:
            req_headers.update(headers)
        if token:
            req_headers["Authorization"] = f"Bearer {token}"
            
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=req_headers)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=req_headers)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=req_headers)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=req_headers)
            else:
                return False, {"error": f"Unsupported method: {method}"}, 0
                
            try:
                response_data = response.json()
            except:
                response_data = {"text": response.text}
                
            return response.status_code < 400, response_data, response.status_code
            
        except Exception as e:
            return False, {"error": str(e)}, 0

    def test_signup_valid(self):
        """Test signup with valid credentials"""
        data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        success, response, status_code = self.make_request("POST", "/auth/signup", data)
        
        if success and status_code == 200:
            if "token" in response and "user" in response:
                user = response["user"]
                if all(key in user for key in ["id", "email", "is_admin", "is_premium"]):
                    self.test_token = response["token"]
                    self.log_result("Signup Valid", True, f"User created successfully: {user['email']}")
                    return True
                else:
                    self.log_result("Signup Valid", False, "Missing user fields in response", str(response))
            else:
                self.log_result("Signup Valid", False, "Missing token or user in response", str(response))
        else:
            self.log_result("Signup Valid", False, f"Signup failed (status: {status_code})", str(response))
        
        return False

    def test_signup_duplicate(self):
        """Test signup with duplicate email"""
        data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        success, response, status_code = self.make_request("POST", "/auth/signup", data)
        
        if status_code == 409:
            self.log_result("Signup Duplicate", True, "Correctly rejected duplicate email")
            return True
        else:
            self.log_result("Signup Duplicate", False, f"Expected 409, got {status_code}", str(response))
            return False

    def test_signup_invalid_email(self):
        """Test signup with invalid email format"""
        data = {
            "email": "invalid-email",
            "password": TEST_USER_PASSWORD
        }
        
        success, response, status_code = self.make_request("POST", "/auth/signup", data)
        
        if status_code == 422:  # Validation error
            self.log_result("Signup Invalid Email", True, "Correctly rejected invalid email format")
            return True
        else:
            self.log_result("Signup Invalid Email", False, f"Expected 422, got {status_code}", str(response))
            return False

    def test_signup_short_password(self):
        """Test signup with short password"""
        data = {
            "email": "short@thai2drive.com",
            "password": "123"  # Less than 6 characters
        }
        
        success, response, status_code = self.make_request("POST", "/auth/signup", data)
        
        if status_code == 422:  # Validation error
            self.log_result("Signup Short Password", True, "Correctly rejected short password")
            return True
        else:
            self.log_result("Signup Short Password", False, f"Expected 422, got {status_code}", str(response))
            return False

    def test_login_valid(self):
        """Test login with correct credentials"""
        data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        success, response, status_code = self.make_request("POST", "/auth/login", data)
        
        if success and status_code == 200:
            if "token" in response and "user" in response:
                self.test_token = response["token"]
                self.log_result("Login Valid", True, f"Login successful for {response['user']['email']}")
                return True
            else:
                self.log_result("Login Valid", False, "Missing token or user in response", str(response))
        else:
            self.log_result("Login Valid", False, f"Login failed (status: {status_code})", str(response))
        
        return False

    def test_login_wrong_password(self):
        """Test login with wrong password"""
        data = {
            "email": TEST_USER_EMAIL,
            "password": "wrongpassword"
        }
        
        success, response, status_code = self.make_request("POST", "/auth/login", data)
        
        if status_code == 401:
            self.log_result("Login Wrong Password", True, "Correctly rejected wrong password")
            return True
        else:
            self.log_result("Login Wrong Password", False, f"Expected 401, got {status_code}", str(response))
            return False

    def test_login_nonexistent_email(self):
        """Test login with non-existent email"""
        data = {
            "email": "nonexistent@thai2drive.com",
            "password": TEST_USER_PASSWORD
        }
        
        success, response, status_code = self.make_request("POST", "/auth/login", data)
        
        if status_code == 401:
            self.log_result("Login Nonexistent Email", True, "Correctly rejected non-existent email")
            return True
        else:
            self.log_result("Login Nonexistent Email", False, f"Expected 401, got {status_code}", str(response))
            return False

    def test_get_me_with_token(self):
        """Test GET /auth/me with valid token"""
        if not self.test_token:
            self.log_result("Get Me With Token", False, "No test token available")
            return False
            
        success, response, status_code = self.make_request("GET", "/auth/me", token=self.test_token)
        
        if success and status_code == 200:
            if all(key in response for key in ["id", "email", "is_admin", "is_premium"]):
                self.log_result("Get Me With Token", True, f"User info retrieved: {response['email']}")
                return True
            else:
                self.log_result("Get Me With Token", False, "Missing user fields in response", str(response))
        else:
            self.log_result("Get Me With Token", False, f"Failed to get user info (status: {status_code})", str(response))
        
        return False

    def test_get_me_without_token(self):
        """Test GET /auth/me without token"""
        success, response, status_code = self.make_request("GET", "/auth/me")
        
        if status_code == 401:
            self.log_result("Get Me Without Token", True, "Correctly rejected request without token")
            return True
        else:
            self.log_result("Get Me Without Token", False, f"Expected 401, got {status_code}", str(response))
            return False

    def test_get_me_invalid_token(self):
        """Test GET /auth/me with invalid token"""
        success, response, status_code = self.make_request("GET", "/auth/me", token="invalid-token")
        
        if status_code == 401:
            self.log_result("Get Me Invalid Token", True, "Correctly rejected invalid token")
            return True
        else:
            self.log_result("Get Me Invalid Token", False, f"Expected 401, got {status_code}", str(response))
            return False

    def test_forgot_password(self):
        """Test forgot password request"""
        data = {
            "email": TEST_USER_EMAIL
        }
        
        success, response, status_code = self.make_request("POST", "/auth/forgot-password", data)
        
        if success and status_code == 200:
            if "message" in response:
                self.log_result("Forgot Password", True, "Password reset request sent (MOCKED)")
                return True
            else:
                self.log_result("Forgot Password", False, "Missing message in response", str(response))
        else:
            self.log_result("Forgot Password", False, f"Failed to request password reset (status: {status_code})", str(response))
        
        return False

    def test_reset_password(self):
        """Test password reset with code from logs"""
        # First request a password reset
        data = {
            "email": TEST_USER_EMAIL
        }
        
        success, response, status_code = self.make_request("POST", "/auth/forgot-password", data)
        
        if not success:
            self.log_result("Reset Password", False, "Could not request password reset")
            return False
        
        # Try to get the reset code from backend logs
        try:
            import subprocess
            result = subprocess.run(
                ["tail", "-n", "50", "/var/log/supervisor/backend.err.log"],
                capture_output=True, text=True
            )
            
            reset_code = None
            for line in result.stdout.split('\n'):
                if "[MOCKED EMAIL]" in line and TEST_USER_EMAIL in line:
                    # Extract code from log line
                    parts = line.split(":")
                    if len(parts) > 0:
                        reset_code = parts[-1].strip()
                        break
            
            if reset_code:
                # Test password reset with the code
                reset_data = {
                    "email": TEST_USER_EMAIL,
                    "code": reset_code,
                    "new_password": "newpassword123"
                }
                
                success, response, status_code = self.make_request("POST", "/auth/reset-password", reset_data)
                
                if success and status_code == 200:
                    self.log_result("Reset Password", True, f"Password reset successful with code: {reset_code}")
                    return True
                else:
                    self.log_result("Reset Password", False, f"Password reset failed (status: {status_code})", str(response))
            else:
                self.log_result("Reset Password", False, "Could not find reset code in logs")
                
        except Exception as e:
            self.log_result("Reset Password", False, f"Error reading logs: {str(e)}")
        
        return False

    def test_admin_check_non_admin(self):
        """Test admin check for non-admin email"""
        data = {
            "email": TEST_USER_EMAIL
        }
        
        success, response, status_code = self.make_request("POST", "/admin/check", data)
        
        if success and status_code == 200:
            if "is_admin" in response and response["is_admin"] == False:
                self.log_result("Admin Check Non-Admin", True, f"Correctly identified non-admin: {TEST_USER_EMAIL}")
                return True
            else:
                self.log_result("Admin Check Non-Admin", False, "Unexpected admin check response", str(response))
        else:
            self.log_result("Admin Check Non-Admin", False, f"Admin check failed (status: {status_code})", str(response))
        
        return False

    def test_admin_add_and_check(self):
        """Test adding admin and checking admin status"""
        # First add admin
        add_data = {
            "email": ADMIN_USER_EMAIL
        }
        
        success, response, status_code = self.make_request("POST", "/admin/add", add_data)
        
        if not (success and status_code == 200):
            self.log_result("Admin Add", False, f"Failed to add admin (status: {status_code})", str(response))
            return False
        
        self.log_result("Admin Add", True, f"Admin added: {ADMIN_USER_EMAIL}")
        
        # Now check admin status
        check_data = {
            "email": ADMIN_USER_EMAIL
        }
        
        success, response, status_code = self.make_request("POST", "/admin/check", check_data)
        
        if success and status_code == 200:
            if "is_admin" in response and response["is_admin"] == True:
                self.log_result("Admin Check Admin", True, f"Correctly identified admin: {ADMIN_USER_EMAIL}")
                return True
            else:
                self.log_result("Admin Check Admin", False, "Admin not recognized after adding", str(response))
        else:
            self.log_result("Admin Check Admin", False, f"Admin check failed (status: {status_code})", str(response))
        
        return False

    def test_existing_endpoints(self):
        """Test that existing endpoints still work"""
        endpoints_to_test = [
            ("GET", "/questions", "Questions endpoint"),
            ("POST", "/seed", "Seed endpoint"),
            ("GET", "/categories", "Categories endpoint")
        ]
        
        all_passed = True
        
        for method, endpoint, name in endpoints_to_test:
            success, response, status_code = self.make_request(method, endpoint)
            
            if success and status_code == 200:
                self.log_result(f"Existing - {name}", True, f"{name} working correctly")
            else:
                self.log_result(f"Existing - {name}", False, f"{name} failed (status: {status_code})", str(response))
                all_passed = False
        
        return all_passed

    def run_all_tests(self):
        """Run all auth tests"""
        print(f"🚀 Starting Thai2Drive Auth API Tests")
        print(f"📍 Testing against: {BASE_URL}")
        print("=" * 60)
        
        # Test signup flow
        self.test_signup_valid()
        self.test_signup_duplicate()
        self.test_signup_invalid_email()
        self.test_signup_short_password()
        
        # Test login flow
        self.test_login_valid()
        self.test_login_wrong_password()
        self.test_login_nonexistent_email()
        
        # Test /auth/me endpoint
        self.test_get_me_with_token()
        self.test_get_me_without_token()
        self.test_get_me_invalid_token()
        
        # Test password reset flow
        self.test_forgot_password()
        self.test_reset_password()
        
        # Test admin functionality
        self.test_admin_check_non_admin()
        self.test_admin_add_and_check()
        
        # Test existing endpoints
        self.test_existing_endpoints()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for r in self.results if r["success"])
        total = len(self.results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if total - passed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['message']}")
                    if result["details"]:
                        print(f"    Details: {result['details']}")
        
        return passed == total

if __name__ == "__main__":
    tester = AuthTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)