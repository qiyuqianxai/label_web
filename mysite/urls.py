"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.conf.urls import url
from django.contrib import admin
from login import views as login_views
from django.conf.urls import include
from label import face_beside_label_views
from image_shower import views as image_shower_views
from label import face_inside_label_views


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # 注册
    url(r'^index/', login_views.index),
    url(r'^login/', login_views.login),
    url(r'^register/', login_views.register),
    url(r'^logout/', login_views.logout),

    # 类间
    url(r'^face_beside_label/$', face_beside_label_views.index),
    url(r'^face_beside_get_database_list/$', face_beside_label_views.multi_get_database_list),
    url(r'^face_beside_get_all_data/$', face_beside_label_views.get_all_data),
    url(r'^face_beside_get_id_range/$', face_beside_label_views.get_id_range),
    url(r'^face_beside_save_label_info/$',face_beside_label_views.save_label_info),

    url(r'^q_index/', image_shower_views.index),
    url(r'^query/$', image_shower_views.query),

    # 类内
    url(r'^face_inside_label/$', face_inside_label_views.index),
    url(r'^face_inside_get_database_id_range_list/$', face_inside_label_views.multi_get_database),
    url(r'^face_inside_get_all_data/$', face_inside_label_views.get_all_data),
    url(r'^face_inside_get_id_range/$',face_inside_label_views.get_id_range),
    url(r'^face_inside_save_label_info/$', face_inside_label_views.save_label_info),

    url(r'^/imgs/(.+)',face_inside_label_views.showpic),

]
