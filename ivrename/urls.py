from . import views
from django.conf.urls import url

urlpatterns = [
    url('get_iv/', views.get_iv, name='get_iv'),
]
