from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
import os
import requests

def user_directory_path(instance, filename):
    # Files will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return f'user_{instance.user.id}/{filename}'

class Document(models.Model):
    title = models.CharField(max_length=100)
    file = models.FileField(
        upload_to=user_directory_path, 
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')

    def __str__(self):
        return self.title
    
    def filename(self):
        return os.path.basename(self.file.name)

@receiver(post_save, sender=Document)
def reload_knowledge_base(sender, instance, created, **kwargs):
    """
    Signal to reload the knowledge base whenever a new document is uploaded
    """
    if created:
        try:
            # Call the API to reload the knowledge base
            response = requests.post(
                f'http://localhost:8001/load_knowledge/{instance.user.id}',
                timeout=5
            )
            # Log success or failure as needed
            print(f"Knowledge base reload for user {instance.user.id}: {response.status_code}")
        except Exception as e:
            # Log the error
            print(f"Error reloading knowledge base: {str(e)}")