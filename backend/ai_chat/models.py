from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.

class Conversation(models.Model):
    """用户和AI之间的对话"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_conversations')
    title = models.CharField(max_length=255, default='新对话')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    use_memory = models.BooleanField(default=True)
    memory_summary = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.title} ({self.user.username})"
    
    def update_memory_summary(self, new_summary):
        """更新记忆摘要"""
        self.memory_summary = new_summary
        self.save(update_fields=['memory_summary'])
    
    class Meta:
        ordering = ['-updated_at']

class Message(models.Model):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    )
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."
