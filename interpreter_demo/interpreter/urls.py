from django.urls import path
from . import views

app_name = 'index'
urlpatterns = [
    path('', views.interpreter, name='interpreter'),
    path('tasks/', views.task_list, name='task_list'),
    path('<int:task_id>/', views.interpreter, name='tasks'),
    path('run_test/', views.run_test, name='run_test'),
    path('save_code/', views.save_code, name='save_code'),
    path('send/', views.send_success, name='send_success'),
]
