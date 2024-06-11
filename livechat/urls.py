from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<slug:slug>/", views.room, name="room"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_room", views.create_room, name="create_room"),
    path("error", views.error, name="error"),
    path("leave_room/<int:user_id>/<int:room_id>/", views.leave_room, name="leave_room"),
    path("edit_room/<slug:slug>/", views.edit_room, name="edit_room"),
    path("delete_room/<slug:slug>/", views.delete_room, name="delete_room"),

]
