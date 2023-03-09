"""licenta URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from users import views as users_views
from snowplowrouting import views as snpr_views



urlpatterns = [
    path('admin/', admin.site.urls),
    path('register-admin/', users_views.register_admin, name='register-admin'),
    path('register-employee/', users_views.register_employee, name='register-employee'),
    path('login/', users_views.login_users, name="login"),
    path('logout/', users_views.logout_users, name="logout"),
    path('accounts/profile-admin/', snpr_views.AdminHomeView.as_view(template_name='admin_profile.html'), name="admin_profile"),
    path('accounts/profile-admin/add-employee', snpr_views.AddEmployeeView.as_view(template_name='add_resources.html'), name="add_employee"),
    path('accounts/profile-worker/', snpr_views.WorkerHomeView.as_view(template_name='worker_profile.html'), name="worker_profile")
]
