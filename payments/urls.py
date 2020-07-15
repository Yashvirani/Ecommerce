from django.urls import path
from .views import initiate_payment, callback

app_name='payments'

urlpatterns = [
    path('pay/', initiate_payment, name='pay'),
    path('callback/', callback, name='callback'),
]
