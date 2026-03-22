"""
Test the my_teams endpoint directly.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from apps.teams.views import TeamViewSet
from apps.users.models import User

# Get user
username = "TestXD"
user = User.objects.get(username=username)

# Create a fake request
factory = RequestFactory()
request = factory.get('/api/teams/my_teams/')
request.user = user

# Call the view
view = TeamViewSet.as_view({'get': 'my_teams'})
response = view(request)

print(f"\nStatus Code: {response.status_code}")
print(f"\nResponse Data:")
print(response.data)
