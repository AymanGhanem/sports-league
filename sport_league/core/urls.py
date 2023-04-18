# Django Imports
from django.urls import path

# App Imports
from core.views import HomeView, upload_csv, handler

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('upload-csv/', upload_csv, name='upload_csv'),
    path('handler/', handler, name='handler'),
]
