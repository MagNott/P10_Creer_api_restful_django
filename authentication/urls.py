from django.urls import path
from .views import CustomUserView, CustomUserDetailView

urlpatterns = [
    path("users/", CustomUserView.as_view(), name="user-list-create"),
    path(
        "users/<int:user_id>/",
        CustomUserDetailView.as_view(),
        name="user-detail"
    ),
]
