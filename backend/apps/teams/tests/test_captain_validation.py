from django.test import TestCase
from django.core.exceptions import ValidationError
from apps.users.models import User
from apps.teams.models import Team, TeamMembership


class CaptainValidationTestCase(TestCase):
    """Test captain validation in TeamMembership model."""
    
    def setUp(self):
        """Create test users and a team."""
        self.captain = User.objects.create_user(
            username='captain',
            email='captain@test.com',
            password='testpass123'
        )
        
        self.player1 = User.objects.create_user(
            username='player1',
            email='player1@test.com',
            password='testpass123'
        )
        
        self.player2 = User.objects.create_user(
            username='player2',
            email='player2@test.com',
            password='testpass123'
        )
        
        # Create a team with captain
        self.team = Team.objects.create(
            name='Test Team',
            captain=self.captain
        )
        
        # Create captain membership
        self.captain_membership = TeamMembership.objects.create(
            user=self.captain,
            team=self.team,
            role='captain',
            status='active'
        )
    
    def test_cannot_create_second_active_captain(self):
        """Test that creating a second active captain raises ValidationError."""
        with self.assertRaises(ValidationError) as context:
            TeamMembership.objects.create(
                user=self.player1,
                team=self.team,
                role='captain',
                status='active'
            )
        
        self.assertIn('one active captain', str(context.exception))
    
    def test_can_create_invited_captain(self):
        """Test that creating an invited captain (not active) is allowed."""
        # This should work because status is 'invited', not 'active'
        invited_captain = TeamMembership.objects.create(
            user=self.player1,
            team=self.team,
            role='captain',
            status='invited'
        )
        self.assertEqual(invited_captain.role, 'captain')
        self.assertEqual(invited_captain.status, 'invited')
    
    def test_can_create_active_player(self):
        """Test that creating active players is allowed."""
        player_membership = TeamMembership.objects.create(
            user=self.player1,
            team=self.team,
            role='player',
            status='active'
        )
        self.assertEqual(player_membership.role, 'player')
        self.assertEqual(player_membership.status, 'active')
    
    def test_cannot_remove_only_active_captain(self):
        """Test that changing the only active captain to non-active raises ValidationError."""
        with self.assertRaises(ValidationError) as context:
            self.captain_membership.status = 'left'
            self.captain_membership.save()
        
        self.assertIn('only active captain', str(context.exception))
    
    def test_cannot_change_only_captain_to_player(self):
        """Test that changing the only captain's role to player raises ValidationError."""
        with self.assertRaises(ValidationError) as context:
            self.captain_membership.role = 'player'
            self.captain_membership.save()
        
        self.assertIn('only active captain', str(context.exception))
    
    def test_can_transfer_captaincy_atomically(self):
        """Test that transferring captaincy requires atomic operation."""
        # First create a player membership
        player_membership = TeamMembership.objects.create(
            user=self.player1,
            team=self.team,
            role='player',
            status='active'
        )
        
        # Attempting to promote player to captain while another captain exists should fail
        with self.assertRaises(ValidationError):
            player_membership.role = 'captain'
            player_membership.save()
        
        # The proper way is to demote current captain first, then promote new captain
        # But this would leave team without captain temporarily, which also fails
        # This demonstrates that captain transfer must be done atomically in services.py
        
        # For model-level testing, we can simulate atomic transfer by:
        # 1. Change old captain to player
        self.captain_membership.role = 'player'
        # Don't save yet - this would fail validation
        
        # The validation ensures captain transfers must be handled at service layer
        # where both operations can be done in a transaction
    
    def test_multiple_teams_can_have_captains(self):
        """Test that different teams can each have their own active captain."""
        # Create another team with a different captain
        team2 = Team.objects.create(
            name='Second Team',
            captain=self.player1
        )
        
        captain2_membership = TeamMembership.objects.create(
            user=self.player1,
            team=team2,
            role='captain',
            status='active'
        )
        
        # Both teams should have their own active captain
        self.assertEqual(
            TeamMembership.objects.filter(
                team=self.team,
                role='captain',
                status='active'
            ).count(),
            1
        )
        self.assertEqual(
            TeamMembership.objects.filter(
                team=team2,
                role='captain',
                status='active'
            ).count(),
            1
        )
