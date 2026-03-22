"""
Test script for public profile endpoint.

Run with: python manage.py shell < test_public_profile.py
"""
import requests

BASE_URL = 'http://localhost:8000/api'

def test_public_profile():
    """Test the public profile endpoint."""
    print("Testing Public Profile Endpoint")
    print("=" * 50)
    
    # Test 1: Get user by username (public - no auth)
    print("\n1. Testing GET /api/users/testuser/ (no auth)")
    response = requests.get(f'{BASE_URL}/users/testuser/')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Username: {data.get('username')}")
        print(f"Email visible: {'email' in data}")
        print(f"Bio: {data.get('bio', 'N/A')[:50]}...")
        print("✅ Public profile accessible")
    else:
        print(f"❌ Error: {response.text}")
    
    # Test 2: Get non-existent user
    print("\n2. Testing GET /api/users/nonexistent/ (should 404)")
    response = requests.get(f'{BASE_URL}/users/nonexistent/')
    print(f"Status: {response.status_code}")
    if response.status_code == 404:
        print("✅ Correctly returns 404 for non-existent user")
    else:
        print(f"❌ Expected 404, got {response.status_code}")
    
    print("\n" + "=" * 50)
    print("Tests completed!")

if __name__ == '__main__':
    test_public_profile()
