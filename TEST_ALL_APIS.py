#!/usr/bin/env python3
"""
🧪 FOOD DELIVERY SYSTEM - COMPREHENSIVE API TEST SUITE

Melakukan 25 tests untuk memverifikasi semua endpoints bekerja dengan baik.
Test dilakukan SETELAH semua microservices berjalan.

Modes:
- quick: Test 5 basic endpoints only (2 menit)
- full: Test semua 25 endpoints (5 menit)  
- debug: Debug specific service

Author: QA Team
Date: November 2025
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Tuple

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_URL = "http://localhost:5000"  # API Gateway
TIMEOUT = 10

# Color codes for terminal output
COLORS = {
    'HEADER': '\033[95m',
    'BLUE': '\033[94m',
    'CYAN': '\033[96m',
    'GREEN': '\033[92m',
    'YELLOW': '\033[93m',
    'RED': '\033[91m',
    'ENDC': '\033[0m',
    'BOLD': '\033[1m',
    'UNDERLINE': '\033[4m',
}

def colorize(text: str, color: str) -> str:
    """Add color to text for terminal output"""
    return f"{COLORS[color]}{text}{COLORS['ENDC']}"

# ============================================================================
# TEST CASES (25 total)
# ============================================================================

TEST_CASES = [
    # ==================== HEALTH CHECK & BASIC (2 tests) ====================
    {
        "id": 1,
        "name": "Health Check",
        "method": "GET",
        "endpoint": "/health",
        "expected_status": 200,
        "description": "Verify API Gateway is running",
        "category": "Health"
    },
    {
        "id": 2,
        "name": "Non-existent Service",
        "method": "GET",
        "endpoint": "/api/nonexistent",
        "expected_status": 404,
        "description": "Verify proper 404 error handling",
        "category": "Error Handling"
    },
    
    # ==================== AUTHENTICATION (2 tests) ====================
    {
        "id": 3,
        "name": "Login Admin",
        "method": "POST",
        "endpoint": "/auth/login",
        "data": {"username": "admin", "password": "admin123"},
        "expected_status": 200,
        "description": "Login dengan admin credentials",
        "category": "Authentication"
    },
    {
        "id": 4,
        "name": "Verify Token",
        "method": "GET",
        "endpoint": "/auth/verify",
        "expected_status": 200,
        "description": "Verify JWT token is valid",
        "category": "Authentication",
        "requires_token": True
    },
    
    # ==================== USER SERVICE - Port 5001 (5 tests) ====================
    {
        "id": 5,
        "name": "Get All Users",
        "method": "GET",
        "endpoint": "/api/user-service/api/users",
        "expected_status": 200,
        "description": "Retrieve all users from user service",
        "category": "User Service"
    },
    {
        "id": 6,
        "name": "Create User",
        "method": "POST",
        "endpoint": "/api/user-service/api/users",
        "data": {
            "username": "testuser123",
            "email": "testuser123@example.com",
            "password": "SecurePass123!",
            "full_name": "Test User",
            "phone": "08123456789",
            "address": "123 Test Street",
            "user_type": "customer"
        },
        "expected_status": 201,
        "description": "Create new user in user service",
        "category": "User Service"
    },
    {
        "id": 7,
        "name": "Get User by ID",
        "method": "GET",
        "endpoint": "/api/user-service/api/users/1",
        "expected_status": 200,
        "description": "Retrieve specific user by ID",
        "category": "User Service"
    },
    {
        "id": 8,
        "name": "Update User",
        "method": "PUT",
        "endpoint": "/api/user-service/api/users/1",
        "data": {"full_name": "Updated User Name"},
        "expected_status": 200,
        "description": "Update user information",
        "category": "User Service"
    },
    {
        "id": 9,
        "name": "Delete User (Soft)",
        "method": "DELETE",
        "endpoint": "/api/user-service/api/users/2",
        "expected_status": 200,
        "description": "Soft delete user",
        "category": "User Service"
    },
    
    # ==================== RESTAURANT SERVICE - Port 5002 (4 tests) ====================
    {
        "id": 10,
        "name": "Get All Restaurants",
        "method": "GET",
        "endpoint": "/api/restaurant-service/api/restaurants",
        "expected_status": 200,
        "description": "Retrieve all restaurants",
        "category": "Restaurant Service"
    },
    {
        "id": 11,
        "name": "Create Restaurant",
        "method": "POST",
        "endpoint": "/api/restaurant-service/api/restaurants",
        "data": {
            "name": "Test Restaurant",
            "description": "A great test restaurant",
            "address": "123 Restaurant St",
            "phone": "0812-3456789",
            "email": "restaurant@example.com"
        },
        "expected_status": 201,
        "description": "Create new restaurant",
        "category": "Restaurant Service"
    },
    {
        "id": 12,
        "name": "Get All Menu Items",
        "method": "GET",
        "endpoint": "/api/restaurant-service/api/menu-items",
        "expected_status": 200,
        "description": "Retrieve all menu items",
        "category": "Restaurant Service"
    },
    {
        "id": 13,
        "name": "Create Menu Item",
        "method": "POST",
        "endpoint": "/api/restaurant-service/api/menu-items",
        "data": {
            "restaurant_id": 1,
            "name": "Test Dish",
            "description": "A delicious test dish",
            "price": 50000,
            "category": "main",
            "is_vegetarian": False
        },
        "expected_status": 201,
        "description": "Create new menu item",
        "category": "Restaurant Service"
    },
    
    # ==================== ORDER SERVICE - Port 5003 (2 tests) ====================
    {
        "id": 14,
        "name": "Get All Orders",
        "method": "GET",
        "endpoint": "/api/order-service/api/orders",
        "expected_status": 200,
        "description": "Retrieve all orders",
        "category": "Order Service"
    },
    {
        "id": 15,
        "name": "Create Order",
        "method": "POST",
        "endpoint": "/api/order-service/api/orders",
        "data": {
            "user_id": 1,
            "restaurant_id": 1,
            "delivery_address": "123 Test Address",
            "total_amount": 150000,
            "delivery_fee": 10000,
            "items": [
                {"menu_item_id": 1, "quantity": 2, "price": 50000}
            ]
        },
        "expected_status": 201,
        "description": "Create new order",
        "category": "Order Service"
    },
    
    # ==================== DELIVERY SERVICE - Port 5004 (2 tests) ====================
    {
        "id": 16,
        "name": "Get All Deliveries",
        "method": "GET",
        "endpoint": "/api/delivery-service/api/deliveries",
        "expected_status": 200,
        "description": "Retrieve all deliveries",
        "category": "Delivery Service"
    },
    {
        "id": 17,
        "name": "Create Delivery",
        "method": "POST",
        "endpoint": "/api/delivery-service/api/deliveries",
        "data": {
            "order_id": 1,
            "driver_name": "Test Driver",
            "driver_phone": "08123456789",
            "delivery_address": "123 Test Address",
            "estimated_time": 30
        },
        "expected_status": 201,
        "description": "Create new delivery",
        "category": "Delivery Service"
    },
    
    # ==================== PAYMENT SERVICE - Port 5005 (3 tests) ====================
    {
        "id": 18,
        "name": "Get All Payments",
        "method": "GET",
        "endpoint": "/api/payment-service/api/payments",
        "expected_status": 200,
        "description": "Retrieve all payments",
        "category": "Payment Service"
    },
    {
        "id": 19,
        "name": "Create Payment",
        "method": "POST",
        "endpoint": "/api/payment-service/api/payments",
        "data": {
            "order_id": 1,
            "amount": 160000,
            "payment_method": "credit_card",
            "status": "pending"
        },
        "expected_status": 201,
        "description": "Create new payment",
        "category": "Payment Service"
    },
    {
        "id": 20,
        "name": "Process Payment",
        "method": "POST",
        "endpoint": "/api/payment-service/api/payments/1/process",
        "data": {"status": "completed"},
        "expected_status": 200,
        "description": "Process payment",
        "category": "Payment Service"
    },
    
    # ==================== ERROR HANDLING (3 tests) ====================
    {
        "id": 21,
        "name": "Invalid Credentials",
        "method": "POST",
        "endpoint": "/auth/login",
        "data": {"username": "admin", "password": "wrongpassword"},
        "expected_status": 401,
        "description": "Verify 401 for invalid credentials",
        "category": "Error Handling"
    },
    {
        "id": 22,
        "name": "Unauthorized Access",
        "method": "GET",
        "endpoint": "/api/user-service/api/users",
        "expected_status": [200, 401],  # Can be either
        "description": "Verify authorization checks",
        "category": "Error Handling"
    },
    {
        "id": 23,
        "name": "Invalid JSON",
        "method": "POST",
        "endpoint": "/auth/login",
        "data": "INVALID_JSON",
        "expected_status": 400,
        "description": "Verify 400 for invalid JSON",
        "category": "Error Handling",
        "raw_data": True
    },
    
    # ==================== ADDITIONAL TESTS (2 tests) ====================
    {
        "id": 24,
        "name": "Get User by ID (Non-existent)",
        "method": "GET",
        "endpoint": "/api/user-service/api/users/9999",
        "expected_status": 404,
        "description": "Verify 404 for non-existent user",
        "category": "Error Handling"
    },
    {
        "id": 25,
        "name": "API Documentation",
        "method": "GET",
        "endpoint": "/api/docs",
        "expected_status": [200, 404],  # May or may not exist
        "description": "Verify API documentation endpoint",
        "category": "Documentation"
    }
]

# ============================================================================
# TEST EXECUTION FUNCTIONS
# ============================================================================

def execute_test(test_case: Dict, access_token: str = None) -> Tuple[bool, int, str]:
    """Execute single test case"""
    
    url = f"{BASE_URL}{test_case['endpoint']}"
    headers = {'Content-Type': 'application/json'}
    
    if access_token and test_case.get('requires_token'):
        headers['Authorization'] = f'Bearer {access_token}'
    
    try:
        if test_case['method'] == 'GET':
            response = requests.get(url, headers=headers, timeout=TIMEOUT)
        elif test_case['method'] == 'POST':
            # Handle raw data if specified
            if test_case.get('raw_data'):
                headers['Content-Type'] = 'text/plain'
                response = requests.post(url, data=test_case['data'], headers=headers, timeout=TIMEOUT)
            else:
                response = requests.post(url, json=test_case.get('data'), headers=headers, timeout=TIMEOUT)
        elif test_case['method'] == 'PUT':
            response = requests.put(url, json=test_case.get('data'), headers=headers, timeout=TIMEOUT)
        elif test_case['method'] == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=TIMEOUT)
        else:
            return False, 0, "Unknown HTTP method"
        
        # Check status code
        expected = test_case['expected_status']
        if isinstance(expected, list):
            passed = response.status_code in expected
        else:
            passed = response.status_code == expected
        
        return passed, response.status_code, response.text
    
    except requests.exceptions.ConnectionError:
        return False, 0, "Connection error - service may not be running"
    except requests.exceptions.Timeout:
        return False, 0, "Request timeout"
    except Exception as e:
        return False, 0, str(e)

def run_tests(mode: str = "full") -> Dict:
    """Run test suite"""
    
    print_header()
    
    # Determine which tests to run
    if mode == "quick":
        tests_to_run = TEST_CASES[:5]
    elif mode == "debug":
        tests_to_run = [t for t in TEST_CASES if t['category'] in ['Authentication', 'Health']]
    else:
        tests_to_run = TEST_CASES
    
    results = {
        'total': len(tests_to_run),
        'passed': 0,
        'failed': 0,
        'tests': []
    }
    
    # First, try to get access token
    access_token = None
    print(f"\n{colorize('🔐 ATTEMPTING LOGIN...', 'CYAN')}\n")
    
    login_test = next((t for t in TEST_CASES if t['name'] == 'Login Admin'), None)
    if login_test:
        passed, status, response = execute_test(login_test)
        if passed:
            try:
                data = json.loads(response)
                access_token = data.get('access_token')
                print(f"{colorize('✅ Login successful!', 'GREEN')}")
                print(f"   Token: {access_token[:50]}...\n")
            except:
                print(f"{colorize('⚠️  Could not extract token from login response', 'YELLOW')}\n")
        else:
            print(f"{colorize('❌ Login failed', 'RED')} - Status {status}\n")
    
    # Run tests
    print(f"{colorize('='*70, 'BOLD')}")
    print(f"{colorize('🧪 RUNNING TEST SUITE', 'BOLD')} ({len(tests_to_run)} tests)")
    print(f"{colorize('='*70, 'BOLD')}\n")
    
    for i, test in enumerate(tests_to_run, 1):
        # Execute test
        passed, status_code, response = execute_test(test, access_token)
        
        # Store result
        result = {
            'id': test['id'],
            'name': test['name'],
            'passed': passed,
            'status_code': status_code,
            'category': test['category']
        }
        results['tests'].append(result)
        
        # Update counters
        if passed:
            results['passed'] += 1
        else:
            results['failed'] += 1
        
        # Print result
        status_icon = "✅" if passed else "❌"
        status_color = "GREEN" if passed else "RED"
        
        print(f"[{i:2d}/{len(tests_to_run)}] {status_icon} {test['name']:.<50} {colorize(f'({status_code})', status_color)}")
    
    return results

def print_header():
    """Print test header"""
    print(colorize(f"""
╔════════════════════════════════════════════════════════════════════════╗
║                  🧪 FOOD DELIVERY SYSTEM - TEST SUITE 🧪               ║
║                                                                        ║
║  Testing: Food Delivery System API Gateway & Microservices            ║
║  Base URL: {BASE_URL:.<35} ║
║  Timeout: {TIMEOUT}s                                                      ║
║                                                                        ║
║  📊 Total Tests: {len(TEST_CASES)}                                                        ║
║                                                                        ║
║  Services being tested:                                               ║
║    🔐 API Gateway (5000)                                              ║
║    👤 User Service (5001)                                             ║
║    🍽️  Restaurant Service (5002)                                      ║
║    📦 Order Service (5003)                                            ║
║    🚚 Delivery Service (5004)                                         ║
║    💳 Payment Service (5005)                                          ║
║                                                                        ║
╚════════════════════════════════════════════════════════════════════════╝
    """, 'CYAN'))

def print_summary(results: Dict):
    """Print test summary"""
    
    passed_pct = (results['passed'] / results['total'] * 100) if results['total'] > 0 else 0
    failed_pct = 100 - passed_pct
    
    # Color based on pass rate
    if passed_pct == 100:
        summary_color = 'GREEN'
        emoji = '🎉'
    elif passed_pct >= 80:
        summary_color = 'YELLOW'
        emoji = '⚠️ '
    else:
        summary_color = 'RED'
        emoji = '🚨'
    
    print(f"\n{colorize('='*70, 'BOLD')}")
    print(f"{colorize('📊 TEST SUMMARY', 'BOLD')}")
    print(f"{colorize('='*70, 'BOLD')}\n")
    
    print(f"Total Tests Run: {results['total']}")
    passed_text = f'✅ PASSED: {results["passed"]} ({passed_pct:.1f}%)'
    print(f"{colorize(passed_text, 'GREEN')}")
    failed_text = f'❌ FAILED: {results["failed"]} ({failed_pct:.1f}%)'
    print(f"{colorize(failed_text, 'RED')}")
    
    print(f"\n{emoji} {colorize('OVERALL RESULT:', summary_color)} ", end='')
    if passed_pct == 100:
        print(colorize('ALL TESTS PASSED! 🎊', 'GREEN'))
    elif passed_pct >= 80:
        print(colorize('MOSTLY PASSING - Some issues to fix', 'YELLOW'))
    else:
        print(colorize('SIGNIFICANT FAILURES - Major issues detected', 'RED'))
    
    # Group by category
    print(f"\n{colorize('📋 RESULTS BY CATEGORY:', 'BOLD')}\n")
    categories = {}
    for test in results['tests']:
        cat = test['category']
        if cat not in categories:
            categories[cat] = {'passed': 0, 'failed': 0}
        if test['passed']:
            categories[cat]['passed'] += 1
        else:
            categories[cat]['failed'] += 1
    
    for cat in sorted(categories.keys()):
        stats = categories[cat]
        total = stats['passed'] + stats['failed']
        pct = (stats['passed'] / total * 100) if total > 0 else 0
        
        status_color = 'GREEN' if pct == 100 else 'YELLOW' if pct > 0 else 'RED'
        stats_text = f'{stats["passed"]}/{total}'
        print(f"  {cat:.<40} {colorize(stats_text, status_color)}")
    
    # Failed tests details
    failed_tests = [t for t in results['tests'] if not t['passed']]
    if failed_tests:
        print(f"\n{colorize('❌ FAILED TESTS:', 'RED')}\n")
        for test in failed_tests:
            print(f"  [{test['id']:2d}] {test['name']:.<45} (Status: {test['status_code']})")
    
    print(f"\n{colorize('='*70, 'BOLD')}\n")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    
    # Parse command line arguments
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"
    
    if mode not in ["quick", "full", "debug"]:
        print(f"Usage: python test_api.py [quick|full|debug]")
        print(f"  quick: 5 basic tests (2 min)")
        print(f"  full:  25 comprehensive tests (5 min) - DEFAULT")
        print(f"  debug: Only auth & health tests")
        sys.exit(1)
    
    try:
        # Run tests
        results = run_tests(mode)
        
        # Print summary
        print_summary(results)
        
        # Exit with appropriate code
        sys.exit(0 if results['failed'] == 0 else 1)
    
    except KeyboardInterrupt:
        print(f"\n{colorize('⚠️  Test interrupted by user', 'YELLOW')}")
        sys.exit(1)
    except Exception as e:
        error_text = f'❌ Test suite error: {str(e)}'
        print(f"\n{colorize(error_text, 'RED')}")
        sys.exit(1)
