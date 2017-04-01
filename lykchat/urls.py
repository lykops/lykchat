"""lykwxchat URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url

from .views import Manage, Interface


urlpatterns = [
    # url(r'^admin/', admin.site.urls),
    url(r'^$', Manage().index, name='index'),
    url(r'^login$', Manage().login, name='login'),
    url(r'^sendmsg', Interface().sendmsg, name='sendmsg'),
    url(r'^check_login', Interface().check_login, name='check_login'),
    url(r'^wx_logout$', Manage().wx_logout, name='wx_logout'),
    url(r'^logout$', Manage().logout, name='logout'),
]
