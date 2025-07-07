from django.urls import path
from .views import register_view, login_view, logout_view, home_view,predict_view,alert_engineer,dashboard_view,user_list,create_user,edit_user,delete_user,assign_task,engineer_tasks,upload_and_predict,clear_user_predictions

urlpatterns = [
    path('', home_view, name='home'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('predict/', predict_view, name='predict'),
    path('alert-engineer/', alert_engineer, name='alert_engineer'),
    path('dashboard/',dashboard_view, name='dashboard'),
    path('admin/users/', user_list, name='user_list'),
    path('admin/users/create/', create_user, name='create_user'),
    path('admin/users/edit/<int:pk>/', edit_user, name='edit_user'),
    path('admin/users/delete/<int:pk>/', delete_user, name='delete_user'),
    path('assign-task/', assign_task, name='assign-task'),
    path('my-tasks/', engineer_tasks, name='engineer-tasks'),
    path('upload/', upload_and_predict, name='upload_and_predict'),
    path('clear-my-predictions/', clear_user_predictions, name='clear_predictions'),
   
    
    # in dashboard
    # path('predict/', views.predict_view, name='predict'),
    # path('stats/', views.stats_view, name='stats'),
    # path('upload/', views.upload_view, name='upload')


]
