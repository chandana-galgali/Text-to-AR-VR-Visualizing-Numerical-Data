from django.http import JsonResponse
from .models import Visualization
from rest_framework.decorators import api_view

@api_view(['GET'])
def visualization_data(request, id):
    """API endpoint to provide visualization data to Unity"""
    try:
        visualization = Visualization.objects.get(id=id)
        return JsonResponse({
            "success": True,
            "data": visualization.processed_data,
            "type": visualization.visualization_type,
            "id": visualization.id
        })
    except Visualization.DoesNotExist:
        return JsonResponse({
            "success": False,
            "error": "Visualization not found"
        }, status=404)