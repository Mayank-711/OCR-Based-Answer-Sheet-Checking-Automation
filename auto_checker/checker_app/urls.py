from django.urls import path
from . import views

app_name = 'checker'

urlpatterns = [
    path('', views.omr_view, name='omr'),
    path('omr/', views.omr_view, name='omr_page'),
    path('debug/', views.debug_view, name='debug'),
    path('dsa/', views.dsa_view, name='dsa'),
    path('merger/', views.merger_view, name='merger'),
    path('wheel/', views.wheel_view, name='wheel'),
]
