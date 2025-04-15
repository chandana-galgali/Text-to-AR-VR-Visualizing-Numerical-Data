from django.db import models

class Visualization(models.Model):
    input_text = models.TextField()
    processed_data = models.JSONField(null=True, blank=True)
    visualization_type = models.CharField(max_length=100, null=True, blank=True)
    visualization_image = models.TextField(null=True, blank=True)  # Store base64 image
    processing_method = models.CharField(max_length=20, default='script')  # 'script', 'openai', or 'fallback'
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Visualization {self.id} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"