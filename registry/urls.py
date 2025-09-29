from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('ngo-dashboard/', views.ngo_dashboard, name='ngo_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('add-project/', views.add_project, name='add_project'),
    path('upload-record/', views.upload_record, name='upload_record'),
    path('verify-record/<uuid:record_id>/', views.verify_record, name='verify_record'),
]
