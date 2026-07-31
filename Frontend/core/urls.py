from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('process/', views.process_text, name='process_text'),
    path('bar/', views.visualize, {'viz_type': 'bar'}, name='bar_chart'),
    path('line/', views.visualize, {'viz_type': 'line'}, name='line_chart'),
    path('<str:viz_type>/', views.visualize, name='visualize'),  # Generic visualize path
]