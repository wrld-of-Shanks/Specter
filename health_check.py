#!/usr/bin/env python3
"""
Comprehensive Backend Health Check Script for SPECTER Legal Assistant
Tests CORS, API endpoints, environment variables, and MongoDB connection
"""

import os
import sys
import json
import requests
from typing import Dict, List, Tuple
from urllib.parse import urlparse

class BackendHealthChecker:
    def __init__(self, backend_url: str):
        self.backend_url = backend_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 30

    def check_cors(self, endpoint: str) -> Dict[str, any]:
        """Test CORS preflight request for an endpoint"""
        url = f"{self.backend_url}{endpoint}"
        headers = {
            'Origin': 'https://specter0.netlify.app',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type,Authorization'
        }

        try:
            response = self.session.options(url, headers=headers)
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
                'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
            }

            # Check if CORS is properly configured
            cors_ok = (
                cors_headers['Access-Control-Allow-Origin'] == 'https://specter0.netlify.app' and
                'POST' in cors_headers['Access-Control-Allow-Methods'] and
                cors_headers['Access-Control-Allow-Credentials'] == 'true'
            )

            return {
                'status': 'PASS' if cors_ok else 'FAIL',
                'status_code': response.status_code,
                'cors_headers': cors_headers,
                'response_time': response.elapsed.total_seconds(),
                'issues': [] if cors_ok else ['CORS headers missing or misconfigured']
            }
        except Exception as e:
            return {
                'status': 'ERROR',
                'status_code': None,
                'cors_headers': {},
                'response_time': None,
                'issues': [f'CORS check failed: {str(e)}']
            }

    def check_api_endpoint(self, endpoint: str, method: str = 'POST', data: Dict = None) -> Dict[str, any]:
        """Test API endpoint functionality"""
        url = f"{self.backend_url}{endpoint}"

        try:
            if method == 'POST':
                response = self.session.post(url, json=data, headers={'Content-Type': 'application/json'})
            else:
                response = self.session.get(url)

            # Check response content
            try:
                response_data = response.json()
            except:
                response_data = {'raw_response': response.text[:200]}

            # Determine if response is expected
            is_success = response.status_code in [200, 201, 400]  # 400 for validation errors is OK

            return {
                'status': 'PASS' if is_success else 'FAIL',
                'status_code': response.status_code,
                'response_data': response_data,
                'response_time': response.elapsed.total_seconds(),
                'issues': [] if is_success else [f'Unexpected status code: {response.status_code}']
            }
        except Exception as e:
            return {
                'status': 'ERROR',
                'status_code': None,
                'response_data': {},
                'response_time': None,
                'issues': [f'API check failed: {str(e)}']
            }

    def check_environment_variables(self) -> Dict[str, any]:
        """Check for required environment variables in deployment"""
        required_vars = [
            'DATABASE_NAME',
            'JWT_SECRET_KEY',
            'MONGODB_URL',
            'RAZORPAY_KEY_ID',
            'RAZORPAY_KEY_SECRET'
        ]

        optional_vars = [
            'LAWYER_RECEIVER_EMAIL',
            'LAWYER_SMTP_USER',
            'LAWYER_SMTP_PASS',
            'LAWYER_SMTP_HOST',
            'LAWYER_SMTP_PORT'
        ]

        issues = []
        missing_required = []
        missing_optional = []

        # Check required variables
        for var in required_vars:
            if not os.getenv(var):
                missing_required.append(var)

        # Check optional variables
        for var in optional_vars:
            if not os.getenv(var):
                missing_optional.append(var)

        if missing_required:
            issues.append(f"Missing required environment variables: {', '.join(missing_required)}")

        if missing_optional:
            issues.append(f"Missing optional environment variables: {', '.join(missing_optional)}")

        # Check MongoDB URL format if present
        mongodb_url = os.getenv('MONGODB_URL')
        if mongodb_url:
            try:
                parsed = urlparse(mongodb_url)
                if parsed.scheme not in ['mongodb', 'mongodb+srv']:
                    issues.append("MONGODB_URL has invalid scheme (should be mongodb:// or mongodb+srv://)")
                if not parsed.netloc:
                    issues.append("MONGODB_URL missing host information")
            except Exception as e:
                issues.append(f"MONGODB_URL format error: {str(e)}")

        status = 'PASS' if not issues else 'FAIL'
        return {
            'status': status,
            'missing_required': missing_required,
            'missing_optional': missing_optional,
            'issues': issues
        }

    def check_mongodb_connection(self) -> Dict[str, any]:
        """Test MongoDB connection using environment variables"""
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            import asyncio

            mongodb_url = os.getenv('MONGODB_URL')
            if not mongodb_url:
                return {
                    'status': 'ERROR',
                    'issues': ['MONGODB_URL environment variable not set']
                }

            # Try to connect (this is a simple synchronous check)
            client = AsyncIOMotorClient(mongodb_url, serverSelectionTimeoutMS=5000)

            async def test_connection():
                try:
                    # Just try to get server info
                    await client.admin.command('ping')
                    return True
                except Exception as e:
                    return False
                finally:
                    client.close()

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(test_connection())
                loop.close()

                return {
                    'status': 'PASS' if result else 'FAIL',
                    'issues': [] if result else ['MongoDB connection failed - check URL and network']
                }
            except Exception as e:
                loop.close()
                return {
                    'status': 'ERROR',
                    'issues': [f'MongoDB connection test failed: {str(e)}']
                }

        except ImportError:
            return {
                'status': 'ERROR',
                'issues': ['Motor (MongoDB driver) not installed']
            }
        except Exception as e:
            return {
                'status': 'ERROR',
                'issues': [f'MongoDB check failed: {str(e)}']
            }

    def run_comprehensive_check(self) -> Dict[str, any]:
        """Run all checks and generate comprehensive report"""
        print(f"🔍 Starting comprehensive health check for: {self.backend_url}")
        print("=" * 60)

        results = {}

        # 1. CORS Check
        print("\n1️⃣  Testing CORS Configuration...")
        cors_login = self.check_cors('/auth/login')
        cors_register = self.check_cors('/auth/register')

        results['cors'] = {
            'login': cors_login,
            'register': cors_register,
            'overall_status': 'PASS' if cors_login['status'] == 'PASS' and cors_register['status'] == 'PASS' else 'FAIL'
        }

        print(f"   Login endpoint CORS: {'✅ PASS' if cors_login['status'] == 'PASS' else '❌ FAIL'}")
        print(f"   Register endpoint CORS: {'✅ PASS' if cors_register['status'] == 'PASS' else '❌ FAIL'}")

        # 2. API Endpoint Check
        print("\n2️⃣  Testing API Endpoints...")

        # Test registration
        register_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'full_name': 'Test User'
        }
        api_register = self.check_api_endpoint('/auth/register', 'POST', register_data)

        # Test login
        login_data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        api_login = self.check_api_endpoint('/auth/login', 'POST', login_data)

        results['api_endpoints'] = {
            'register': api_register,
            'login': api_login,
            'overall_status': 'PASS' if api_register['status'] == 'PASS' and api_login['status'] == 'PASS' else 'FAIL'
        }

        print(f"   Register endpoint: {'✅ PASS' if api_register['status'] == 'PASS' else '❌ FAIL'}")
        print(f"   Login endpoint: {'✅ PASS' if api_login['status'] == 'PASS' else '❌ FAIL'}")

        # 3. Environment Variables Check
        print("\n3️⃣  Checking Environment Variables...")
        env_check = self.check_environment_variables()
        results['environment'] = env_check

        print(f"   Environment check: {'✅ PASS' if env_check['status'] == 'PASS' else '❌ FAIL'}")
        if env_check['issues']:
            for issue in env_check['issues']:
                print(f"   ⚠️  {issue}")

        # 4. MongoDB Connection Check
        print("\n4️⃣  Testing MongoDB Connection...")
        mongo_check = self.check_mongodb_connection()
        results['mongodb'] = mongo_check

        print(f"   MongoDB connection: {'✅ PASS' if mongo_check['status'] == 'PASS' else '❌ FAIL'}")
        if mongo_check['issues']:
            for issue in mongo_check['issues']:
                print(f"   ⚠️  {issue}")

        # Overall status
        overall_status = all([
            results['cors']['overall_status'] == 'PASS',
            results['api_endpoints']['overall_status'] == 'PASS',
            results['environment']['status'] == 'PASS',
            results['mongodb']['status'] == 'PASS'
        ])

        results['overall_status'] = 'PASS' if overall_status else 'FAIL'

        print("\n" + "=" * 60)
        print(f"🏁  COMPREHENSIVE HEALTH CHECK: {'✅ ALL SYSTEMS OPERATIONAL' if overall_status else '❌ ISSUES DETECTED'}")

        return results

def generate_report(results: Dict[str, any], backend_url: str) -> str:
    """Generate detailed markdown report"""
    report = f"""# 🔍 Backend Health Check Report

**Target URL**: {backend_url}
**Check Date**: {requests.utils.formatdate(timeval=None, localtime=True)}
**Overall Status**: {'✅ **PASS**' if results['overall_status'] == 'PASS' else '❌ **FAIL**'}

---

## 1️⃣ CORS Configuration Check

| Endpoint | Status | Response Time | Details |
|----------|--------|---------------|---------|
| `/auth/login` | {results['cors']['login']['status']} | {results['cors']['login'].get('response_time', 'N/A')}s | {', '.join(results['cors']['login'].get('issues', ['OK']))} |
| `/auth/register` | {results['cors']['register']['status']} | {results['cors']['register'].get('response_time', 'N/A')}s | {', '.join(results['cors']['register'].get('issues', ['OK']))} |

## 2️⃣ API Endpoints Check

| Endpoint | Status | Status Code | Response Time | Issues |
|----------|--------|-------------|---------------|--------|
| `/auth/register` | {results['api_endpoints']['register']['status']} | {results['api_endpoints']['register'].get('status_code', 'N/A')} | {results['api_endpoints']['register'].get('response_time', 'N/A')}s | {', '.join(results['api_endpoints']['register'].get('issues', ['None']))} |
| `/auth/login` | {results['api_endpoints']['login']['status']} | {results['api_endpoints']['login'].get('status_code', 'N/A')} | {results['api_endpoints']['login'].get('response_time', 'N/A')}s | {', '.join(results['api_endpoints']['login'].get('issues', ['None']))} |

## 3️⃣ Environment Variables Check

**Status**: {results['environment']['status']}

### Missing Required Variables:
{chr(10).join(f'- ❌ {var}' for var in results['environment']['missing_required']) if results['environment']['missing_required'] else '- ✅ All required variables present'}

### Missing Optional Variables:
{chr(10).join(f'- ⚠️  {var}' for var in results['environment']['missing_optional']) if results['environment']['missing_optional'] else '- ✅ All optional variables present'}

### Issues:
{chr(10).join(f'- {issue}' for issue in results['environment']['issues']) if results['environment']['issues'] else '- ✅ No environment variable issues detected'}

## 4️⃣ MongoDB Connection Check

**Status**: {results['mongodb']['status']}

### Issues:
{chr(10).join(f'- {issue}' for issue in results['mongodb']['issues']) if results['mongodb']['issues'] else '- ✅ MongoDB connection successful'}

---

## 🔧 Suggested Fixes

"""

    if results['overall_status'] == 'FAIL':
        fixes = []

        if results['cors']['overall_status'] == 'FAIL':
            fixes.append("""
### CORS Issues:
- Ensure CORS middleware is properly configured in FastAPI
- Verify allowed origins include your frontend domain
- Check that `allow_credentials=True` is set
""")

        if results['api_endpoints']['overall_status'] == 'FAIL':
            fixes.append("""
### API Endpoint Issues:
- Verify authentication routes are properly registered
- Check database connectivity for user operations
- Ensure JWT secret key is properly configured
""")

        if results['environment']['status'] == 'FAIL':
            fixes.append("""
### Environment Variable Issues:
- Add missing required variables to Render dashboard
- Verify MongoDB URL format and connectivity
- Check for typos in variable names
""")

        if results['mongodb']['status'] == 'FAIL':
            fixes.append("""
### MongoDB Connection Issues:
- Verify MONGODB_URL is correct and accessible
- Check MongoDB cluster status and firewall settings
- Ensure database user has proper permissions
""")

        report += "\n".join(fixes)

    report += f"""

---
**Report Generated**: {requests.utils.formatdate(timeval=None, localtime=True)}
**Backend URL**: {backend_url}
"""

    return report

def main():
    if len(sys.argv) != 2:
        print("Usage: python health_check.py <backend_url>")
        print("Example: python health_check.py https://specter-vwjk.onrender.com")
        sys.exit(1)

    backend_url = sys.argv[1]
    checker = BackendHealthChecker(backend_url)
    results = checker.run_comprehensive_check()

    # Generate and print report
    report = generate_report(results, backend_url)
    print(report)

    # Save report to file
    with open('backend_health_report.md', 'w') as f:
        f.write(report)

    print("📄 Report saved to: backend_health_report.md")

    # Exit with appropriate code
    sys.exit(0 if results['overall_status'] == 'PASS' else 1)

if __name__ == "__main__":
    main()
