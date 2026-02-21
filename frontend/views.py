from django import forms
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST

from core.models import UserProfile, Provoz, Pozice
from osobni_dotaznik.models import OsobniDotaznik, OsobniDotaznikPriloha
from .forms import StartDotaznikForm, OsobniDotaznikEditForm, PrilohaForm


@login_required
def hr_dashboard(request):
    return render(request, "frontend/hr_dashboard.html")


@login_required
def provoz_dashboard(request):
    profil = getattr(request.user, "profile", None)

    moje_provozy = Provoz.objects.none()
    if profil and profil.spravovane_provozy.exists():
        moje_provozy = profil.spravovane_provozy.all().order_by(
            "cislo_provozu",
            "nazev",
        )

    if request.method == "POST":
        start_form = StartDotaznikForm(request.POST, user=request.user)
        if start_form.is_valid():
            provoz = start_form.cleaned_data["provoz"]
            pozice = start_form.cleaned_data["pozice"]

            dotaznik = OsobniDotaznik.objects.create(
                provoz=provoz,
                pozice=pozice,
                created_by=request.user,
                jmeno="",
                prijmeni="",
                datum_narozeni="2000-01-01",
                misto_narozeni="",
                statni_obcanstvi="",
                rodne_cislo="000000/0000",
                zdravotni_pojistovna="",
                cislo_uctu="",
                kod_banky="",
                trvale_ulice="",
                trvale_cislo_popisne="",
                trvale_mesto="",
                trvale_psc="",
                dorucovaci_ulice="",
                dorucovaci_cislo_popisne="",
                dorucovaci_mesto="",
                dorucovaci_psc="",
            )
            return redirect("frontend:dotaznik_edit", dotaznik_id=dotaznik.id)
    else:
        start_form = StartDotaznikForm(user=request.user)

    provozy_ids = moje_provozy.values_list("id", flat=True)

    # rozpracované (draft + vráceno na doplnění provozu)
    dotazniky_rozpracovane = OsobniDotaznik.objects.filter(
        provoz_id__in=provozy_ids,
        stav__in=[
            OsobniDotaznik.STAV_DRAFT,
            OsobniDotaznik.STAV_VRACENO_PROVOZU,
        ],
    ).order_by("-created_at")

    # odeslané / ve workflow (cokoli jiného než draft/vráceno)
    dotazniky_odeslane = OsobniDotaznik.objects.filter(
        provoz_id__in=provozy_ids,
    ).exclude(
        stav__in=[
            OsobniDotaznik.STAV_DRAFT,
            OsobniDotaznik.STAV_VRACENO_PROVOZU,
        ]
    ).order_by("-updated_at")

    context = {
        "moje_provozy": moje_provozy,
        "start_form": start_form,
        "dotazniky_rozpracovane": dotazniky_rozpracovane,
        "dotazniky_odeslane": dotazniky_odeslane,
    }
    return render(request, "frontend/provoz_dashboard.html", context)


@login_required
def dotaznik_edit(request, dotaznik_id):
    dotaznik = get_object_or_404(OsobniDotaznik, id=dotaznik_id)

    # provoz / oblastní mohou editovat:
    # - draft
    # - vráceno na doplnění provozu
    povolene_stavy = [
        OsobniDotaznik.STAV_DRAFT,
        OsobniDotaznik.STAV_VRACENO_PROVOZU,
    ]
    if dotaznik.stav not in povolene_stavy:
        return redirect("frontend:provoz_dashboard")

    # volitelně: kontrola, že user má k dotazníku přístup (spravované provozy)
    profil = getattr(request.user, "profile", None)
    if profil and profil.spravovane_provozy.exists():
        if dotaznik.provoz not in profil.spravovane_provozy.all():
            return redirect("frontend:provoz_dashboard")

    if request.method == "POST":
        # rozlišíme akci podle jména tlačítka
        if "ulozit_dotaznik" in request.POST:
            form = OsobniDotaznikEditForm(request.POST, instance=dotaznik)
            priloha_form = PrilohaForm()  # teď neřešíme upload
            if form.is_valid():
                form.save()
                # stav necháváme (draft/vráceno); o odeslání rozhoduje samostatné tlačítko
                return redirect("frontend:provoz_dashboard")
        elif "pridat_prilohu" in request.POST:
            # při nahrávání přílohy hlavní form vůbec nevalidujeme
            form = OsobniDotaznikEditForm(instance=dotaznik)
            priloha_form = PrilohaForm(request.POST, request.FILES)
            if priloha_form.is_valid():
                pridana = priloha_form.save(commit=False)
                pridana.dotaznik = dotaznik
                pridana.save()
                return redirect("frontend:dotaznik_edit", dotaznik_id=dotaznik.id)
        else:
            # fallback – kdyby přišel POST bez známého tlačítka
            form = OsobniDotaznikEditForm(request.POST, instance=dotaznik)
            priloha_form = PrilohaForm()
    else:
        form = OsobniDotaznikEditForm(instance=dotaznik)
        priloha_form = PrilohaForm()

    return render(
        request,
        "frontend/dotaznik_edit.html",
        {
            "form": form,
            "dotaznik": dotaznik,
            "priloha_form": priloha_form,
        },
    )


def simple_logout(request):
    logout(request)
    return redirect("frontend:login")


@login_required
def dotaznik_delete(request, dotaznik_id):
    dotaznik = get_object_or_404(OsobniDotaznik, id=dotaznik_id)

    # bezpečnost: smažeme jen drafty
    if dotaznik.stav != OsobniDotaznik.STAV_DRAFT:
        return redirect("frontend:provoz_dashboard")

    if request.method == "POST":
        dotaznik.delete()
        return redirect("frontend:provoz_dashboard")

    return render(
        request,
        "frontend/dotaznik_delete_confirm.html",
        {"dotaznik": dotaznik},
    )


@login_required
def dotaznik_kontrola(request, dotaznik_id):
    dotaznik = get_object_or_404(OsobniDotaznik, id=dotaznik_id)

    # provoz může kontrolovat jen draft NEBO vrácený dotazník
    if dotaznik.stav not in [
        OsobniDotaznik.STAV_DRAFT,
        OsobniDotaznik.STAV_VRACENO_PROVOZU,
    ]:
        return redirect("frontend:provoz_dashboard")

    # volitelně: kontrola přístupu podle provozu
    profil = getattr(request.user, "profile", None)
    if profil and profil.spravovane_provozy.exists():
        if dotaznik.provoz not in profil.spravovane_provozy.all():
            return redirect("frontend:provoz_dashboard")

    return render(
        request,
        "frontend/dotaznik_kontrola.html",
        {"dotaznik": dotaznik},
    )


@login_required
@require_POST
def dotaznik_odeslat_hr(request, dotaznik_id):
    dotaznik = get_object_or_404(OsobniDotaznik, id=dotaznik_id)

    # odeslat na HR půjde:
    # - z draftu
    # - z vráceného provozu (po doplnění)
    if dotaznik.stav not in [
        OsobniDotaznik.STAV_DRAFT,
        OsobniDotaznik.STAV_VRACENO_PROVOZU,
    ]:
        return redirect("frontend:provoz_dashboard")

    # volitelně: kontrola přístupu podle provozu
    profil = getattr(request.user, "profile", None)
    if profil and profil.spravovane_provozy.exists():
        if dotaznik.provoz not in profil.spravovane_provozy.all():
            return redirect("frontend:provoz_dashboard")

    dotaznik.stav = OsobniDotaznik.STAV_PROVOZ_ODESLAL
    dotaznik.save()
    return redirect("frontend:provoz_dashboard")


@login_required
def dotaznik_detail_provoz(request, dotaznik_id):
    dotaznik = get_object_or_404(OsobniDotaznik, id=dotaznik_id)

    # volitelně: kontrola, že jde o „jeho“ provoz
    profil = getattr(request.user, "profile", None)
    if profil and profil.spravovane_provozy.exists():
        if dotaznik.provoz not in profil.spravovane_provozy.all():
            return redirect("frontend:provoz_dashboard")

    return render(
        request,
        "frontend/dotaznik_detail_provoz.html",
        {"dotaznik": dotaznik},
    )


@login_required
@require_POST
def priloha_delete(request, priloha_id):
    priloha = get_object_or_404(OsobniDotaznikPriloha, id=priloha_id)
    dotaznik = priloha.dotaznik

    # kontrola, že user má k dotazníku přístup
    profil = getattr(request.user, "profile", None)
    if profil and profil.spravovane_provozy.exists():
        if dotaznik.provoz not in profil.spravovane_provozy.all():
            return redirect("frontend:provoz_dashboard")

    priloha.delete()
    return redirect("frontend:dotaznik_edit", dotaznik_id=dotaznik.id)


class RoleBasedLoginView(LoginView):
    template_name = "frontend/login_standalone.html"

    def get_success_url(self):
        user = self.request.user
        profil = getattr(user, "profile", None)

        if profil is None or not profil.role:
            return reverse("admin:index")

        if profil.role == "hr":
            return reverse("frontend:hr_dashboard")

        if profil.role in ("manager_provozu", "oblastni_manager"):
            return reverse("frontend:provoz_dashboard")

        return reverse("admin:index")
