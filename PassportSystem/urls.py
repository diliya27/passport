"""
URL configuration for PassportSystem project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path,include
from passport_app import views
from passport_app.views import PassportOfficerUpdateView 
urlpatterns = [
    path('admin/', admin.site.urls),
    # path('',include('passport_app.urls')),
    path("",views.IndexPageView.as_view(), name="index"),
    path('home/', views.HomeView.as_view(), name='home'),
    path('admin-login/',views.AdminLogin.as_view(),name='admin-login'),
    path('admin-logout/',views.AdminLogout.as_view(),name='admin-logout'),
    path('add_passportofficer/',views.AddPassportOfficerView.as_view(),name='add-passportofficer'),
    path('list_passportofficer/', views.ListPassportofficerView.as_view(), name='list-passportofficer'),
    path('update-passportofficer/<int:id>/',PassportOfficerUpdateView.as_view(), name='update-passportofficer'),
    path('delete_passportofficer/<int:pk>/',views.DeletePassportOfficerView.as_view(),name='delete-passportofficer'),

    path('add_passportverifier/',views.AddVerificationOfficerView.as_view(),name='add-verificationofficer'),
    path('list_verificationofficer/', views.ListverificationOfficer.as_view(), name='list-verificationofficer'),





    path('user/',include('user_app.urls')),







    # path('add-officer/', views.AddPassportOfficerView.as_view(), name='add_officer'),
]
