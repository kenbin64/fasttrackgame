"""
Test script for DimensionOS Platform.

Tests:
- User registration
- User login
- Get user info
- Get resource metrics
- Update payment status
"""

import requests
import json


BASE_URL = "http://localhost:8000"


def test_registration():
    """Test user registration."""
    print("\n🧪 Testing user registration...")
    
    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json={
            "email": "test@example.com",
            "password": "SecurePass123!",
            "tier": "free"
        }
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        print("✅ Registration successful!")
        return response.json()
    else:
        print("❌ Registration failed!")
        return None


def test_login():
    """Test user login."""
    print("\n🧪 Testing user login...")
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ Login successful!")
        return response.json()
    else:
        print("❌ Login failed!")
        return None


def test_get_user_info(access_token):
    """Test getting user info."""
    print("\n🧪 Testing get user info...")
    
    response = requests.get(
        f"{BASE_URL}/api/user/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ Get user info successful!")
        return response.json()
    else:
        print("❌ Get user info failed!")
        return None


def test_get_resource_metrics(access_token):
    """Test getting resource metrics."""
    print("\n🧪 Testing get resource metrics...")
    
    response = requests.get(
        f"{BASE_URL}/api/resources/metrics",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ Get resource metrics successful!")
        return response.json()
    else:
        print("❌ Get resource metrics failed!")
        return None


def test_update_payment_status(access_token):
    """Test updating payment status."""
    print("\n🧪 Testing update payment status...")
    
    response = requests.post(
        f"{BASE_URL}/api/payment/status",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "payment_status": "paid",
            "amount": 10.0,
            "period": "2026-02"
        }
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ Update payment status successful!")
        return response.json()
    else:
        print("❌ Update payment status failed!")
        return None


def main():
    """Run all tests."""
    print("🚀 DimensionOS Platform - Test Suite")
    print("=" * 50)
    
    # Test registration
    reg_result = test_registration()
    if not reg_result:
        print("\n❌ Registration failed - stopping tests")
        return
    
    access_token = reg_result["access_token"]
    
    # Test login
    login_result = test_login()
    if login_result:
        access_token = login_result["access_token"]
    
    # Test get user info
    test_get_user_info(access_token)
    
    # Test get resource metrics
    test_get_resource_metrics(access_token)
    
    # Test update payment status
    test_update_payment_status(access_token)
    
    print("\n" + "=" * 50)
    print("✅ All tests complete!")


if __name__ == "__main__":
    main()

