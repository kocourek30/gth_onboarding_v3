from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = "frontend"

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="frontend:login", permanent=False)),
    path("login/", views.RoleBasedLoginView.as_view(), name="login"),
    path("logout/", views.simple_logout, name="logout"),  # ← naše vlastní logout view
    path("hr/", views.hr_dashboard, name="hr_dashboard"),
    path("provoz/", views.provoz_dashboard, name="provoz_dashboard"),
   
   path(
    "dotaznik/<int:dotaznik_id>/edit/",
    views.dotaznik_edit,
    name="dotaznik_edit",
),
path(
    "dotaznik/<int:dotaznik_id>/delete/",
    views.dotaznik_delete,
    name="dotaznik_delete",
),
path(
    "dotaznik/<int:dotaznik_id>/kontrola/",
    views.dotaznik_kontrola,
    name="dotaznik_kontrola",
),
path(
    "dotaznik/<int:dotaznik_id>/odeslat-hr/",
    views.dotaznik_odeslat_hr,
    name="dotaznik_odeslat_hr",
),
path(
    "provoz/dotaznik/<int:dotaznik_id>/",
    views.dotaznik_detail_provoz,
    name="dotaznik_detail_provoz",
),
path(
    "dotaznik/priloha/<int:priloha_id>/delete/",
    views.priloha_delete,
    name="priloha_delete",
),



]
