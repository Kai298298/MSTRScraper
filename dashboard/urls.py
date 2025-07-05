from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('data/', views.data_view, name='data'),
    path('anlagen-listen/', views.anlagen_listen_view, name='anlagen_listen'),
    path('liste/<int:liste_id>/', views.liste_detail_view, name='liste_detail'),
    path('anlage-speichern/', views.anlage_speichern, name='anlage_speichern'),
    path('liste/<int:liste_id>/loeschen/', views.liste_loeschen, name='liste_loeschen'),
    path('liste/<int:liste_id>/duplizieren/', views.liste_duplizieren, name='liste_duplizieren'),
    path('charts/', views.charts_view, name='charts'),
    path('api/data/', views.api_data, name='api_data'),
    path('api/chart-data/', views.api_chart_data, name='api_chart_data'),
    path('export/', views.export_data, name='export_data'),
    path('impressum/', views.impressum_view, name='impressum'),
    path('hilfe/', views.hilfe_view, name='hilfe'),
    path('track-event/', views.track_event, name='track_event'),
    path('analytics/', views.analytics_dashboard, name='analytics'),
    path('betreiber/', views.betreiber_view, name='betreiber'),
    path('betreiber/<str:betreibernummer>/', views.betreiber_detail_view, name='betreiber_detail'),
]
