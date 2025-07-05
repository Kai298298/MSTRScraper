from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('plans/', views.plans_view, name='plans'),
    path('start-trial/', views.start_trial, name='start_trial'),
    path('upgrade/<str:plan_name>/', views.upgrade_plan, name='upgrade_plan'),
    path('success/', views.success_view, name='success'),
    path('usage/', views.usage_view, name='usage'),
    path('billing/', views.billing_view, name='billing'),
    path('analytics-data/', views.analytics_data, name='analytics_data'),
]
