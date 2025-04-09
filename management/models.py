from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_delete
class College(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class ParticipantProfile(models.Model):
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    mobile_number = models.CharField(max_length=15)
    email=models.CharField(max_length=254)
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='participants')
    is_banned= models.BooleanField(default=False)
    def __str__(self):
        return self.name


class Event(models.Model):
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Mixed', 'Mixed'),
    )
    name = models.CharField(max_length=100)  # e.g., Athletics Men - 100M
    sport = models.CharField(max_length=50)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    max_team_members = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return self.name

class Team(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    members = models.ManyToManyField(ParticipantProfile, blank=True)
    captain= models.ForeignKey(ParticipantProfile, related_name="captain_teams", on_delete=models.SET_NULL, null=True, blank=True)
    gender = models.CharField(max_length=50, choices=[("Male", "Male"), ("Female", "Female"), ("Mixed", "Mixed")])
    
    def add_participant(self, participant):
        if not self.participants.exists():
            self.captain = participant
            self.save()
        self.participants.add(participant)
    def is_full(self):
        return self.members.count() >= self.event.max_team_members

    def __str__(self):
        return f"{self.college} - {self.event.name}"

class Match(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    teams = models.ManyToManyField(Team)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    scores = models.JSONField(null=True, blank=True)  # Flexible score field
    finished = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{', '.join(str(team) for team in self.teams.all())} - {self.event.name}"

class TeamJoinRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='join_requests')
    participant = models.ForeignKey(ParticipantProfile, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.participant.name} -> {self.team} ({self.status})"

class Feedback(models.Model):
    participant = models.ForeignKey(ParticipantProfile, on_delete=models.CASCADE)
    message = models.TextField()
    image = models.ImageField(upload_to='feedback_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Feedback from {self.participant.name}"
