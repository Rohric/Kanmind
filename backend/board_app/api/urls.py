from django.urls import path

from .views import BoardDetail, BoardsList, TestApiView

urlpatterns = [
    path("", BoardsList.as_view(), name="boards-list"),
    path("test/", TestApiView.as_view(), name="api-test"),
    path("<int:pk>/", BoardDetail.as_view(), name="board-detail"),
]
