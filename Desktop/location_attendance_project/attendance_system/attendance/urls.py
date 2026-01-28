from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('setup/', views.setup_profile, name='setup_profile'),
    path('check-in/', views.check_in, name='check_in'),
    path('check-out/', views.check_out, name='check_out'),
    path('records/', views.attendance_records, name='attendance_records'),
    path('detail/<int:attendance_id>/', views.attendance_detail, name='attendance_detail'),
    path('api/location/', views.get_location, name='get_location'),
]
