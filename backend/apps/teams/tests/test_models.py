from django.test import TestCase
from apps.users.models import User
from apps.teams.models import Team


class TeamSlugGenerationTestCase(TestCase):
    """Test automatic slug generation for Team model."""
    
    def setUp(self):
        """Create a test user to use as captain."""
        self.user = User.objects.create_user(
            username='testcaptain',
            email='captain@test.com',
            password='testpass123'
        )
    
    def test_slug_generated_from_name_on_create(self):
        """Test that slug is automatically generated from name when creating a team."""
        team = Team.objects.create(
            name='Test Team',
            captain=self.user
        )
        self.assertEqual(team.slug, 'test-team')
    
    def test_slug_lowercase_conversion(self):
        """Test that slug converts name to lowercase."""
        team = Team.objects.create(
            name='UPPERCASE TEAM',
            captain=self.user
        )
        self.assertEqual(team.slug, 'uppercase-team')
    
    def test_slug_spaces_to_hyphens(self):
        """Test that spaces are replaced with hyphens."""
        team = Team.objects.create(
            name='Team With Spaces',
            captain=self.user
        )
        self.assertEqual(team.slug, 'team-with-spaces')
    
    def test_slug_removes_special_characters(self):
        """Test that special characters are removed except hyphens and alphanumerics."""
        team = Team.objects.create(
            name='Team@#$%Name!',
            captain=self.user
        )
        self.assertEqual(team.slug, 'teamname')
    
    def test_slug_uniqueness_with_numeric_suffix(self):
        """Test that duplicate slugs get numeric suffix for uniqueness."""
        team1 = Team.objects.create(
            name='Duplicate Team',
            captain=self.user
        )
        
        user2 = User.objects.create_user(
            username='captain2',
            email='captain2@test.com',
            password='testpass123'
        )
        
        team2 = Team.objects.create(
            name='Duplicate Team',
            captain=user2
        )
        
        self.assertEqual(team1.slug, 'duplicate-team')
        self.assertEqual(team2.slug, 'duplicate-team-1')
    
    def test_slug_regenerated_on_name_update(self):
        """Test that slug is regenerated when name is updated."""
        team = Team.objects.create(
            name='Original Name',
            captain=self.user
        )
        self.assertEqual(team.slug, 'original-name')
        
        team.name = 'Updated Name'
        team.save()
        self.assertEqual(team.slug, 'updated-name')
    
    def test_slug_max_length_60_characters(self):
        """Test that slug does not exceed 60 characters."""
        long_name = 'A' * 100  # Create a very long name
        team = Team.objects.create(
            name=long_name[:50],  # name max is 50
            captain=self.user
        )
        self.assertLessEqual(len(team.slug), 60)
    
    def test_slug_handles_multiple_spaces(self):
        """Test that multiple consecutive spaces are converted to single hyphen."""
        team = Team.objects.create(
            name='Team    With    Spaces',
            captain=self.user
        )
        self.assertEqual(team.slug, 'team-with-spaces')
    
    def test_slug_removes_leading_trailing_hyphens(self):
        """Test that leading and trailing hyphens are removed."""
        team = Team.objects.create(
            name='  Team Name  ',
            captain=self.user
        )
        self.assertFalse(team.slug.startswith('-'))
        self.assertFalse(team.slug.endswith('-'))
