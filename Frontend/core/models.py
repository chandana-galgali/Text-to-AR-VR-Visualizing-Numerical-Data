from django.db import models

class ExtractedData(models.Model):
    raw_text = models.TextField()
    extracted_json = models.JSONField()
    visualization_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Data Entry #{self.id} - {self.visualization_type}"
