"""
Script to test the Users API endpoints.
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def print_response(title, response):
    """Pretty print API response."""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

def test_registration():
    """Test user registration."""
    url = f"{BASE_URL}/auth/register/"
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPass123!",
        "password_confirm": "TestPass123!"
    }
    response = requests.post(url, json=data)
    print_response("1. User Registration", response)
    
    if response.status_code == 201:
        return response.json()['auth']['token']
    return None

def test_login():
    """Test user login."""
    url = f"{BASE_URL}/auth/login/"
    data = {
        "username_or_email": "testuser",
        "password": "TestPass123!"
    }
    response = requests.post(url, json=data)
    print_response("2. User Login", response)
    
    if response.status_code == 200:
        return response.json()['auth']['token']
    return None

def test_get_current_user(token):
    """Test getting current user profile."""
    url = f"{BASE_URL}/users/me/"
    headers = {"Authorization": f"Token {token}"}
    response = requests.get(url, headers=headers)
    print_response("3. Get Current User", response)

def test_update_profile(token):
    """Test updating user profile."""
    url = f"{BASE_URL}/users/me/"
    headers = {"Authorization": f"Token {token}"}
    data = {
        "bio": "This is my test bio for Podium platform!"
    }
    response = requests.patch(url, json=data, headers=headers)
    print_response("4. Update Profile", response)

def test_get_public_profile():
    """Test getting public profile."""
    url = f"{BASE_URL}/profiles/testuser/"
    response = requests.get(url)
    print_response("5. Get Public Profile", response)

def test_get_user_stats():
    """Test getting user statistics."""
    url = f"{BASE_URL}/profiles/1/stats/"
    response = requests.get(url)
    print_response("6. Get User Stats", response)

def test_list_users():
    """Test listing users."""
    url = f"{BASE_URL}/users/"
    response = requests.get(url)
    print_response("7. List Users", response)

def test_search_users():
    """Test searching users."""
    url = f"{BASE_URL}/users/?search=test"
    response = requests.get(url)
    print_response("8. Search Users", response)

def test_logout(token):
    """Test user logout."""
    url = f"{BASE_URL}/auth/logout/"
    headers = {"Authorization": f"Token {token}"}
    response = requests.post(url, headers=headers)
    print_response("9. User Logout", response)

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("TESTING PODIUM USERS API")
    print("="*60)
    print("\nMake sure the Django server is running on http://localhost:8000")
    print("Run: python manage.py runserver")
    
    input("\nPress Enter to start tests...")
    
    # Test registration
    token = test_registration()
    
    if not token:
        print("\n❌ Registration failed. Trying login instead...")
        token = test_login()
    
    if token:
        # Test authenticated endpoints
        test_get_current_user(token)
        test_update_profile(token)
        test_get_public_profile()
        test_get_user_stats()
        test_list_users()
        test_search_users()
        test_logout(token)
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED")
        print("="*60)
    else:
        print("\n❌ Could not obtain authentication token")

if __name__ == "__main__":
    main()
