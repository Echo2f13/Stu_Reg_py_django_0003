from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='Startup_page'),
    path('std-login', views.student_login, name='student_login_page'),
    path('std-signup', views.student_signup, name='student_signup_page'),
    path('admin-login', views.admin_login, name='admin_login_page'),

]
