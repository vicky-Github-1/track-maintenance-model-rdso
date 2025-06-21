from django.urls import path
from .views import register_view, login_view, logout_view, home_view

urlpatterns = [
    path('', home_view, name='home'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
   
    
    # in dashboard
    # path('predict/', views.predict_view, name='predict'),
    # path('stats/', views.stats_view, name='stats'),
    # path('upload/', views.upload_view, name='upload')


]
