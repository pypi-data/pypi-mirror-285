from django.urls import path
from api.views import save_data, get_data, get_csrf_token, get_list



urlpatterns = [
    path('save-data', save_data, name='save_data'),
    path('get-data', get_data, name='get_data'),
    path('get-csrf', get_csrf_token, name='get_csrf_token'),
    path('get-list', get_list, name='get_list')
]

