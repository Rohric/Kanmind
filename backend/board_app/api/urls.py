from django.urls import path
from .views import BoardsList

urlpatterns = [
    path('', BoardsList.as_view(), name='boards-list'),

]
