from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_cv, name='upload_cv'),
    path('query/', views.query_cv, name='query_cv'),
]
