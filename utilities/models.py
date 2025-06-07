from django.db import models

class Communication(models.Model):
    CHANNEL_CHOICES = [
        ('sms', 'SMS'),
        ('email', 'Email'),
    ]

    SERVICE_CHOICES_SMS = [
        ('twilio', 'Twilio'),
        ('sns', 'AWS SNS'),
    ]

    SERVICE_CHOICES_EMAIL = [
        ('hi@studentpeeps.club', 'hi@studentpeeps.club'),
        ('ayush@studentpeeps.club', 'ayush@studentpeeps.club'),
        ('sidharth@studentpeeps.club', 'sidharth@studentpeeps.club'),
    ]

    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES, unique=True)
    service = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.channel.upper()} via {self.service}"
    
    def get_available_choices(self):
        if self.channel == 'sms':
            return dict(self.SERVICE_CHOICES_SMS)
        if self.channel == 'email':
            return dict(self.SERVICE_CHOICES_EMAIL)
