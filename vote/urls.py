"""vote URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path, include
from . import settings

from polls.views import show_subjects,show_teachers,praise_or_criticize,login,logout,get_captcha,export_teachers_excel
from polls import views



urlpatterns = [
    path('admin/', admin.site.urls),
    path("",show_subjects),
    path("teachers/",show_teachers),
    path("praise/",praise_or_criticize),
    path("criticize/",praise_or_criticize),
    path("login/",login),
    path("logout/",logout),
    path('captcha/',get_captcha),
    path('excel/',export_teachers_excel),
    path('teachers_data/',views.get_teachers_data),
    path("echarts",views.echarts),
    path("register/",views.register)
    #path('pdf/',views.export_pdf),

]

if settings.DEBUG:

    import debug_toolbar

    urlpatterns.insert(0, path('__debug__/', include(debug_toolbar.urls)))
