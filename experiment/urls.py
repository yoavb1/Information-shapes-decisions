from . import views
from django.urls import path

app_name = "experiment"

urlpatterns = [
    path('', views.registration, name='registration'),
    path('registration/', views.registration, name='registration'),
    path('consent_form/', views.consent_form, name='consent_form'),
    path('instructions/', views.instructions, name='instructions'),
    path('game/', views.game, name='game'),
    path('block_points/', views.block_points, name='block_points'),
    path('alert_system/', views.alert_system, name='alert_system'),
    path('server/', views.server, name='server'),
    path('parameters/', views.parameters, name='parameters'),
    path('progress/', views.progress, name='progress'),
    path('end/', views.end, name='end'),

]
