from django.urls import path
from .views import GoogleAuthInit, GoogleAuthCallback, WhoAmI

urlpatterns = [
    path('google/login/', GoogleAuthInit.as_view()),
    path('google/callback/', GoogleAuthCallback.as_view()),
    path("whoami/", WhoAmI.as_view()),
]
