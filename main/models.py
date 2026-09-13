import uuid
from django.db import models

class Experience(models.Model):
    EXPERIENCE_CHOICES = [
        ('internship', 'Internship'),
        ('research', 'Research'),
        ('volunteer', 'Volunteer'),
        ('part-time', 'Part-Time'),
        ('full-time', 'Full-Time'),
        ('freelance', 'Freelance'),
        ('committee', 'Committee')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    organization = models.CharField(max_length=255, blank=True, default="")
    description = models.TextField()
    category = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='full-time')
    thumbnail = models.URLField(blank=True, null=True)
    started_at = models.DateField()
    ended_at = models.DateTimeField(blank=True, null=True)
    def __str__(self):
        return self.title
    
    @property
    def is_ongoing(self):
        return self.ended_at is None

    @property
    def description_points(self):
        return [line.strip() for line in self.description.split("\n") if line.strip()]

    @property
    def date_range_display(self):
        start = self.started_at.strftime("%b %Y")
        if self.ended_at:
            end = self.ended_at.strftime("%b %Y")
        else:
            end = "Present"
        return f"{start} — {end}"      


class Skill(models.Model):
    SKILL_CATEGORIES = [
        ('leadership', 'Leadership & Management'),
        ('event', 'Event & Project Coordination'),
        ('communication', 'Communication & Stakeholder Relations'),
        ('technical', 'Technical'),
    ]

    PROFICIENCY_CHOICES = [
        (1, 'Beginner'),
        (2, 'Intermediate'),
        (3, 'Advanced'),
        (4, 'Expert'),
    ]    

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=SKILL_CATEGORIES, default='technical')
    proficiency = models.IntegerField(choices=PROFICIENCY_CHOICES, default=1)
    impact = models.CharField(max_length=255, blank=True)
    context = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name