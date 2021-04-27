from django.urls import path, include

urlpatterns = [
    path('', include('wish_app.urls')),
]
