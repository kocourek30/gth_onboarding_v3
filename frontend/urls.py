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



    path("dotaznik/<int:dotaznik_id>/priloha/add/", views.priloha_add, name="priloha_add"),
    path("priloha/<int:priloha_id>/delete/", views.priloha_delete, name="priloha_delete"),
    path("hr/dotaznik/<int:dotaznik_id>/", views.dotaznik_detail_hr, name="dotaznik_detail_hr"),
    path("hr/dotaznik/<int:dotaznik_id>/generate-contract/", views.hr_generate_contract, name="hr_generate_contract"),
path("hr/dotaznik/<int:dotaznik_id>/generate-wage/", views.hr_generate_wage_doc, name="hr_generate_wage_doc"),
path("hr/dotaznik/<int:dotaznik_id>/schvalit/", views.hr_schvalit_dotaznik, name="hr_schvalit_dotaznik"),
path("priloha/<int:priloha_id>/download/", views.priloha_download, name="priloha_download"),
path("hr/dotaznik/<int:dotaznik_id>/vratit-provozu/",
     views.hr_vratit_provozu,
     name="hr_vratit_provozu"),


    path('dotaznik/<int:dotaznik_id>/generovat-mzdovy-vymer/', views.generovat_mzdovy_vymer, name='generovat_mzdovy_vymer'),
    path("hr/dokument/<int:dokument_id>/delete/", views.dokument_delete, name="dokument_delete"),







]
