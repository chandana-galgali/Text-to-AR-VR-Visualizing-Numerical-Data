from django.urls import path
from . import views
from .api import visualization_data

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('process/', views.process_data, name='process_data'),
    path('result/<int:id>/', views.result, name='result'),
    # API endpoint for Unity to fetch visualization data
    path('api/visualization/<int:id>/', visualization_data, name='visualization_data'),
]