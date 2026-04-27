from django.urls import path

from .views import BoardDetail, BoardsList

urlpatterns = [
    path("", BoardsList.as_view(), name="boards-list"),
    path("<int:pk>/", BoardDetail.as_view(), name="board-detail"),
]
