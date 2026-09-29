#!/usr/bin/env python3
"""
Thai2Drive Backend Auth API Testing
Tests all auth endpoints and verifies existing functionality still works.

Låste ruter (/seed, /admin/check, /admin/add, AI-rutene og /tts) testes med gyldig JWT-token
hentet via innlogging, og uten token for å bekrefte at de avvises.

Konfigurasjon via miljøvariabler (ingen hemmeligheter i filen):
  T2D_BASE_URL          standard http://127.0.0.1:8000/api  (lokal server)
  T2D_ALLOW_PROD=1      kreves for å kjøre mot en ikke-lokal URL (skriptet oppretter brukere,
                        sender tilbakestillingskoder og kaller /seed, så det skal normalt
                        aldri kjøres mot produksjon)
  T2D_ADMIN_EMAIL / T2D_ADMIN_PASSWORD   admin-innlogging (JWT for admin-låste ruter)
  T2D_ADMIN_SECRET      ADMIN_BOOTSTRAP_SECRET (alternativ til admin-JWT, og for /admin/add)
  T2D_PREMIUM_EMAIL / T2D_PREMIUM_PASSWORD   bruker med aktiv tilgang (valgfri, for positive tester)

  python backend_test.py --locked-only   kjører bare sikkerhetstestene (låste ruter, AI, TTS)
"""

import os
import requests
import json
import time
import sys
from typing import Dict, Any, Optional

BASE_URL = os.environ.get("T2D_BASE_URL", "http://127.0.0.1:8000/api").rstrip("/")

# Vanlig testbruker (registreres av signup-testene)
TEST_USER_EMAIL = "test@thai2drive.com"
TEST_USER_PASSWORD = "test123"
# Admin: ingen standardpassord. Uten disse hoppes admin-testene over.
ADMIN_USER_EMAIL = os.environ.get("T2D_ADMIN_EMAIL", "admin@thai2drive.com")
ADMIN_USER_PASSWORD = os.environ.get("T2D_ADMIN_PASSWORD", "")
ADMIN_SECRET = os.environ.get("T2D_ADMIN_SECRET", "")
PREMIUM_USER_EMAIL = os.environ.get("T2D_PREMIUM_EMAIL", "")
PREMIUM_USER_PASSWORD = os.environ.get("T2D_PREMIUM_PASSWORD", "")

# Ruter som krever aktiv tilgang (HTTP 402 uten)
AI_ROUTES = [
    ("GET", "/ai/explanation/q-test"),
    ("GET", "/ai/smart-practice/dev-test"),
    ("GET", "/ai/dashboard/dev-test"),
    ("POST", "/teacher/chat"),
]


def is_local_url(url: str) -> bool:
    from urllib.parse import urlparse
    return (urlparse(url).hostname or "") in ("localhost", "127.0.0.1", "::1")

class AuthTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_token = None
        self.admin_token = None
        self.premium_token = None
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
    
    def log_skip(self, test_name: str, reason: str):
        """Hoppet over (mangler legitimasjon): telles ikke som bestått eller feilet."""
        self.results.append({"test": test_name, "success": True, "skipped": True, "message": reason, "details": ""})
        print(f"⏭️  SKIP {test_name}: {reason}")

    def login_token(self, email: str, password: str) -> Optional[str]:
        success, response, status_code = self.make_request("POST", "/auth/login", {"email": email, "password": password})
        if success and status_code == 200 and isinstance(response, dict):
            return response.get("token")
        return None

    def acquire_tokens(self):
        """Hent gyldige JWT-tokens for de låste rutene (via innlogging, aldri hardkodet)."""
        if not self.test_token:
            self.test_token = self.login_token(TEST_USER_EMAIL, TEST_USER_PASSWORD)
        if ADMIN_USER_PASSWORD and not self.admin_token:
            self.admin_token = self.login_token(ADMIN_USER_EMAIL, ADMIN_USER_PASSWORD)
        if PREMIUM_USER_EMAIL and PREMIUM_USER_PASSWORD and not self.premium_token:
            self.premium_token = self.login_token(PREMIUM_USER_EMAIL, PREMIUM_USER_PASSWORD)

    def admin_auth(self) -> Dict[str, Any]:
        """Argumenter for admin-låste ruter: admin-JWT og/eller X-Admin-Secret."""
        return {"token": self.admin_token, "headers": {"X-Admin-Secret": ADMIN_SECRET} if ADMIN_SECRET else None}

    def has_admin_auth(self) -> bool:
        return bool(self.admin_token or ADMIN_SECRET)

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
        if not self.has_admin_auth():
            self.log_skip("Admin Check Non-Admin", "ingen T2D_ADMIN_PASSWORD/T2D_ADMIN_SECRET satt")
            return True
        data = {
            "email": TEST_USER_EMAIL
        }

        success, response, status_code = self.make_request("POST", "/admin/check", data, **self.admin_auth())

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
        if not ADMIN_SECRET:
            self.log_skip("Admin Add", "ingen T2D_ADMIN_SECRET satt (/admin/add krever X-Admin-Secret)")
            return True
        # First add admin
        add_data = {
            "email": ADMIN_USER_EMAIL
        }

        success, response, status_code = self.make_request("POST", "/admin/add", add_data, headers={"X-Admin-Secret": ADMIN_SECRET})
        
        if not (success and status_code == 200):
            self.log_result("Admin Add", False, f"Failed to add admin (status: {status_code})", str(response))
            return False
        
        self.log_result("Admin Add", True, f"Admin added: {ADMIN_USER_EMAIL}")
        
        # Now check admin status
        check_data = {
            "email": ADMIN_USER_EMAIL
        }
        
        success, response, status_code = self.make_request("POST", "/admin/check", check_data, **self.admin_auth())

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

    # ── Låste ruter, betalingsmur og TTS ─────────────────────────────────────────

    def _expect(self, name: str, status: int, allowed, what: str) -> bool:
        ok = status in allowed
        self.log_result(name, ok, f"{what}: HTTP {status}" + ("" if ok else f" (forventet {sorted(allowed)})"))
        return ok

    def test_locked_routes_reject_unauthenticated(self):
        """Uautentiserte kall mot admin-låste ruter skal avvises (401/403)."""
        ok = True
        for method, path, body in (("POST", "/seed", None), ("POST", "/admin/check", {"email": ADMIN_USER_EMAIL}),
                                   ("POST", "/admin/add", {"email": "x@example.com"}), ("GET", "/admin-setup-t2d", None)):
            _, _, status = self.make_request(method, path, body)
            ok &= self._expect(f"Locked {path} (uten token)", status, (401, 403), f"{method} {path}")
        return ok

    def test_locked_routes_with_valid_token(self):
        """Med gyldig admin-JWT eller X-Admin-Secret slipper man inn."""
        if not self.has_admin_auth():
            self.log_skip("Locked routes med gyldig admin-token", "ingen T2D_ADMIN_PASSWORD/T2D_ADMIN_SECRET satt")
            return True
        ok = True
        _, _, status = self.make_request("POST", "/admin/check", {"email": ADMIN_USER_EMAIL}, **self.admin_auth())
        ok &= self._expect("Locked /admin/check (med admin-token)", status, (200,), "POST /admin/check")
        _, _, status = self.make_request("POST", "/seed", None, **self.admin_auth())
        ok &= self._expect("Locked /seed (med admin-token)", status, (200,), "POST /seed")
        if self.test_token:
            _, _, status = self.make_request("POST", "/seed", None, token=self.test_token)
            ok &= self._expect("Locked /seed (vanlig bruker)", status, (403,), "POST /seed med vanlig brukertoken")
        return ok

    def _has_access(self, token: str) -> Optional[bool]:
        success, response, status = self.make_request("GET", "/auth/me", token=token)
        return bool(response.get("is_premium")) if success and isinstance(response, dict) else None

    def test_ai_routes_paywall(self):
        """AI-rutene: 402 uten aktiv tilgang, slipper gjennom med."""
        ok = True
        for method, path in AI_ROUTES:
            _, _, status = self.make_request(method, path, {} if method == "POST" else None)
            ok &= self._expect(f"AI {path} (uten token)", status, (402,), f"{method} {path}")
        for label, token in (("vanlig bruker", self.test_token), ("bruker med tilgang", self.premium_token)):
            if not token:
                self.log_skip(f"AI-ruter ({label})", "ingen token (innlogging feilet eller ikke konfigurert)")
                continue
            has_access = self._has_access(token)
            for method, path in AI_ROUTES:
                _, _, status = self.make_request(method, path, {} if method == "POST" else None, token=token)
                if has_access:
                    passed = status not in (401, 402, 403)
                    self.log_result(f"AI {path} ({label}, aktiv tilgang)", passed,
                                    f"{method} {path}: HTTP {status}" + ("" if passed else " (skal ikke avvises)"))
                    ok &= passed
                else:
                    ok &= self._expect(f"AI {path} ({label}, uten tilgang)", status, (402,), f"{method} {path}")
        return ok

    def test_tts_paywall(self):
        """TTS: 401 uten innlogging, 402 uten aktiv tilgang, og token-flyt for de som har tilgang."""
        ok = True
        _, _, status = self.make_request("GET", "/tts?lang=th-TH&text=hei")
        ok &= self._expect("TTS uten token", status, (401,), "GET /tts")
        _, _, status = self.make_request("GET", "/tts/stream?lang=th-TH&text=hei", token="ugyldig.token.verdi")
        ok &= self._expect("TTS med ugyldig token", status, (401,), "GET /tts/stream")
        _, _, status = self.make_request("GET", "/tts?lang=th-TH&text=hei&tt=ugyldig")
        ok &= self._expect("TTS med ugyldig ?tt=", status, (401,), "GET /tts?tt=")
        _, _, status = self.make_request("GET", "/tts/token")
        ok &= self._expect("TTS-token uten innlogging", status, (402,), "GET /tts/token")
        for label, token in (("vanlig bruker", self.test_token), ("bruker med tilgang", self.premium_token)):
            if not token:
                self.log_skip(f"TTS ({label})", "ingen token (innlogging feilet eller ikke konfigurert)")
                continue
            has_access = self._has_access(token)
            # Uten tekst svarer serveren 400 ETTER porten, så ingen betalt TTS-leverandør kalles.
            _, _, status = self.make_request("GET", "/tts?lang=th-TH", token=token)
            expected = (400,) if has_access else (402,)
            ok &= self._expect(f"TTS Bearer ({label})", status, expected, "GET /tts uten tekst")
            success, response, status = self.make_request("GET", "/tts/token", token=token)
            if has_access:
                ok &= self._expect(f"TTS-token utstedt ({label})", status, (200,), "GET /tts/token")
                tt = response.get("token") if isinstance(response, dict) else None
                if tt:
                    _, _, status = self.make_request("GET", f"/tts?lang=th-TH&tt={tt}")
                    ok &= self._expect(f"TTS ?tt= ({label})", status, (400,), "GET /tts?tt= uten tekst")
                    _, _, status = self.make_request("GET", "/auth/me", token=tt)
                    ok &= self._expect("TTS-token er ikke en innlogging", status, (401,), "GET /auth/me med TTS-token")
            else:
                ok &= self._expect(f"TTS-token nektet ({label})", status, (402,), "GET /tts/token")
        return ok

    def run_all_tests(self, locked_only: bool = False):
        """Run all auth tests"""
        print(f"🚀 Starting Thai2Drive Auth API Tests")
        print(f"📍 Testing against: {BASE_URL}")
        print("=" * 60)

        if not locked_only:
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

        # Gyldige JWT-tokens for de låste rutene (innlogging, ikke hardkodet)
        self.acquire_tokens()

        # Test admin functionality (låst: krever admin-JWT eller X-Admin-Secret)
        self.test_admin_check_non_admin()
        self.test_admin_add_and_check()

        # Låste ruter, betalingsmur for AI og TTS
        self.test_locked_routes_reject_unauthenticated()
        self.test_locked_routes_with_valid_token()
        self.test_ai_routes_paywall()
        self.test_tts_paywall()

        # Test existing endpoints
        if not locked_only:
            self.test_existing_endpoints()

        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        counted = [r for r in self.results if not r.get("skipped")]
        skipped = len(self.results) - len(counted)
        passed = sum(1 for r in counted if r["success"])
        total = len(counted)

        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Skipped: {skipped}")
        print(f"Success Rate: {(passed/total)*100:.1f}%" if total else "Success Rate: n/a")

        if total - passed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['message']}")
                    if result["details"]:
                        print(f"    Details: {result['details']}")
        
        return passed == total

if __name__ == "__main__":
    # Skriptet oppretter brukere, sender tilbakestillingskoder og kaller /seed: aldri mot produksjon ved uhell.
    if not is_local_url(BASE_URL) and os.environ.get("T2D_ALLOW_PROD") != "1":
        print(f"❌ Nekter å kjøre mot {BASE_URL}: ikke en lokal URL. Sett T2D_ALLOW_PROD=1 hvis det er bevisst.")
        sys.exit(2)
    tester = AuthTester()
    success = tester.run_all_tests(locked_only="--locked-only" in sys.argv)
    sys.exit(0 if success else 1)