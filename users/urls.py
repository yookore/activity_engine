from django.conf.urls import url
from users import views

urlpatterns=(
    url(r'^(?P<username>[\w\d]+)$', views.get_user, name='getuser'),
)