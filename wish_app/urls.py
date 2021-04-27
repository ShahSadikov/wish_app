from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('user/register', views.register_user),
    path('user/login', views.login_user),
    path('user/dashboard', views.dashboard),
    path('user/logout', views.logout_user),
    path('wishes/new', views.create_new_wish),
    path('wishes/create_form', views.create_wish_form),
    path('wishes/<int:wish_id>/delete', views.delete_wish),
    path('wishes/<int:wish_id>/edit', views.edit_wish),
    path('wishes/<int:wish_id>/update', views.update_wish),
    path('wishes/<int:wish_id>/grant', views.grant_wish),
    path('wishes/<int:wish_id>/like', views.add_like),
    path('wishes/stats', views.wish_stats),
]