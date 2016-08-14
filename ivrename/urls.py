from . import views
from django.conf.urls import url

urlpatterns = [
    url(r'get_iv/', views.get_iv, name='get_iv'),
    url(r'^index/', web.index, name='index'),
]
