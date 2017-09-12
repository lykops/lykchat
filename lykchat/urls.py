"""lykchat URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
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

from library.storage.database.mongo import Op_Mongo
from library.storage.database.redis_api import Op_Redis
from lykchat.sysadmin.user import User
from lykchat.views import Login 
from lykchat.wechat import Wechat


# from django.contrib import admin
mongoclient = Op_Mongo()
redisclient = Op_Redis()
log_mongoclient = Op_Mongo(dest='log', idletime=1000 * 60 * 60)

urlpatterns = [
    # url(r'^admin/', admin.site.urls),
    url(r'^$', User(mongoclient=mongoclient, redisclient=redisclient, log_mongoclient=log_mongoclient).summary, name='index'),
    url(r'^login.html', Login(mongoclient=mongoclient, redisclient=redisclient, log_mongoclient=log_mongoclient).login, name='login'),
    url(r'^logout.html', Login(mongoclient=mongoclient, redisclient=redisclient, log_mongoclient=log_mongoclient).logout, name='logout'),
    
    url(r'^user/create_admin', Login(mongoclient=mongoclient, redisclient=redisclient, log_mongoclient=log_mongoclient).create_admin, name='create_admin'),
    url(r'^user/detail', User(mongoclient=mongoclient, redisclient=redisclient, log_mongoclient=log_mongoclient).detail),
    url(r'^user/list', User(mongoclient=mongoclient, redisclient=redisclient, log_mongoclient=log_mongoclient).summary, name='user_list'),
    url(r'^user/add', User(mongoclient=mongoclient, redisclient=redisclient, log_mongoclient=log_mongoclient).add, name='user_add'),
    url(r'^user/edit', User(mongoclient=mongoclient, redisclient=redisclient, log_mongoclient=log_mongoclient).edit),
    url(r'^user/chgpwd', User(mongoclient=mongoclient, redisclient=redisclient, log_mongoclient=log_mongoclient).change_pwd),
    url(r'^user/disable', User(mongoclient=mongoclient, redisclient=redisclient, log_mongoclient=log_mongoclient).disable),
    url(r'^user/enable', User(mongoclient=mongoclient, redisclient=redisclient, log_mongoclient=log_mongoclient).enable),
    url(r'^user/$', User(mongoclient=mongoclient, redisclient=redisclient, log_mongoclient=log_mongoclient).summary),
    
    url(r'^wechat/$', Wechat(mongoclient=mongoclient, redisclient=redisclient, log_mongoclient=log_mongoclient).summary, name='wechat_list'),
    url(r'^wechat/list', Wechat(mongoclient=mongoclient, redisclient=redisclient, log_mongoclient=log_mongoclient).summary, name='wechat_list'),
    url(r'^wechat/detail', Wechat(mongoclient=mongoclient, redisclient=redisclient, log_mongoclient=log_mongoclient).detail),
    url(r'^wechat/logout', Wechat(mongoclient=mongoclient, redisclient=redisclient, log_mongoclient=log_mongoclient).logout),
    url(r'^wechat/check', Wechat(mongoclient=mongoclient, redisclient=redisclient, log_mongoclient=log_mongoclient).check),
    url(r'^wechat/sendmsg', Wechat(mongoclient=mongoclient, redisclient=redisclient, log_mongoclient=log_mongoclient).sendmsg),
    
    
    
    url(r'^logging/$', User(mongoclient=mongoclient, redisclient=redisclient, log_mongoclient=log_mongoclient).get_logging, name='logging'),
]
