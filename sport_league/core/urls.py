# Django Imports
from django.urls import path

# App Imports
from core.views import HomeView, SignupView, SigninView, upload_csv, handler, logout_view

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('upload-csv/', upload_csv, name='upload_csv'),
    path('handler/', handler, name='handler'),
    path('sign-up/', SignupView.as_view(), name='sign_up'),
    path('sign-in/', SigninView.as_view(), name='sign_in'),
    path('logout-out/', logout_view, name='log_out'),
]
