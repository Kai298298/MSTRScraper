from django.urls import path, include
from rest_framework import routers
from .views import GespeicherteAnlageViewSet, AnlagenListeViewSet, UserViewSet

# API Router
router = routers.DefaultRouter()
router.register(r'anlagen', GespeicherteAnlageViewSet, basename='anlagen')
router.register(r'listen', AnlagenListeViewSet, basename='listen')
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
] 