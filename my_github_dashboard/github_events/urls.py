from django.urls import path 
from . import views 
 
urlpatterns = [ 
    path('webhook/', views.github_webhook_receiver, name='github_webhook_receiver'), 
    path('', views.event_list, name='event_list'), # For the UI 
]