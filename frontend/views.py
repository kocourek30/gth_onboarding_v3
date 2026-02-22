from django import forms
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect

from core.models import UserProfile, Provoz, Pozice
from osobni_dotaznik.models import GenerovanyDokument, OsobniDotaznik, OsobniDotaznikPriloha
from .forms import StartDotaznikForm, OsobniDotaznikEditForm, PrilohaForm
from django.utils import timezone

# --- HR část -------------------------------------------------------------

from django.db.models import Q

@login_required
def hr_dashboard(request):
    profil = getattr(request.user, "profile", None)
    if not profil or profil.role != "hr":
        return redirect("frontend:provoz_dashboard")

    q_nove = request.GET.get("q_nove", "").strip()
    q_schv = request.GET.get("q_schvalene", "").strip()
    q_vrac = request.GET.get("q_vracene", "").strip()

    dotazniky_nove = OsobniDotaznik.objects.filter(
        stav=OsobniDotaznik.STAV_PROVOZ_ODESLAL
    ).order_by("-created_at")

    if q_nove:
        dotazniky_nove = dotazniky_nove.filter(
            Q(jmeno__icontains=q_nove)
            | Q(prijmeni__icontains=q_nove)
            | Q(provoz__nazev__icontains=q_nove)
            | Q(pozice__nazev__icontains=q_nove)
            | Q(typ_pomeru__icontains=q_nove)
        )

    dotazniky_schvalene = OsobniDotaznik.objects.filter(
        stav=OsobniDotaznik.STAV_HR_SCHVALIL
    ).order_by("-updated_at")

    if q_schv:
        dotazniky_schvalene = dotazniky_schvalene.filter(
            Q(jmeno__icontains=q_schv)
            | Q(prijmeni__icontains=q_schv)
            | Q(provoz__nazev__icontains=q_schv)
            | Q(pozice__nazev__icontains=q_schv)
            | Q(typ_pomeru__icontains=q_schv)
        )

    dotazniky_vracene_provozu = OsobniDotaznik.objects.filter(
        stav=OsobniDotaznik.STAV_VRACENO_PROVOZU
    ).order_by("-updated_at")

    if q_vrac:
        dotazniky_vracene_provozu = dotazniky_vracene_provozu.filter(
            Q(jmeno__icontains=q_vrac)
            | Q(prijmeni__icontains=q_vrac)
            | Q(provoz__nazev__icontains=q_vrac)
            | Q(pozice__nazev__icontains=q_vrac)
            | Q(typ_pomeru__icontains=q_vrac)
        )

    context = {
        "dotazniky_nove": dotazniky_nove,
        "dotazniky_schvalene": dotazniky_schvalene,
        "dotazniky_vracene_provozu": dotazniky_vracene_provozu,
    }
    return render(request, "frontend/hr_dashboard.html", context)



@login_required
def dotaznik_detail_hr(request, dotaznik_id):
    profil = getattr(request.user, "profile", None)
    if not profil or profil.role != "hr":
        return redirect("frontend:provoz_dashboard")

    dotaznik = get_object_or_404(OsobniDotaznik, id=dotaznik_id)

    povolene_stavy = [
        OsobniDotaznik.STAV_PROVOZ_ODESLAL,
        OsobniDotaznik.STAV_HR_KONTROLUJE,
        OsobniDotaznik.STAV_HR_SCHVALIL,
        OsobniDotaznik.STAV_VRACENO_PROVOZU,
    ]
    if dotaznik.stav not in povolene_stavy:
        return redirect("frontend:hr_dashboard")

    povinne_chybi = []
    if not dotaznik.jmeno:
        povinne_chybi.append("Jméno")
    if not dotaznik.prijmeni:
        povinne_chybi.append("Příjmení")
    if not dotaznik.rodne_cislo:
        povinne_chybi.append("Rodné číslo")
    if not dotaznik.cislo_uctu:
        povinne_chybi.append("Číslo účtu")
    if not dotaznik.trvale_ulice or not dotaznik.trvale_mesto or not dotaznik.trvale_psc:
        povinne_chybi.append("Trvalé bydliště")

    muze_generovat = (len(povinne_chybi) == 0)

    # vygenerované dokumenty k dotazníku (mzdové výměry, smlouvy, ...)
    dokumenty = dotaznik.dokumenty.order_by("-vygenerovano")

    dotaznik.hr_posledni_kontrola = request.user
    dotaznik.hr_posledni_kontrola_at = timezone.now()
    dotaznik.save(update_fields=["hr_posledni_kontrola", "hr_posledni_kontrola_at"])

    return render(
        request,
        "frontend/dotaznik_detail_hr.html",
        {
            "dotaznik": dotaznik,
            "povinne_chybi": povinne_chybi,
            "muze_generovat": muze_generovat,
            "dokumenty": dokumenty,
        },
    )



@login_required
@require_POST
def hr_generate_contract(request, dotaznik_id):
    profil = getattr(request.user, "profile", None)
    if not profil or profil.role != "hr":
        return redirect("frontend:provoz_dashboard")

    dotaznik = get_object_or_404(OsobniDotaznik, id=dotaznik_id)

    # TODO: vlastní generování smlouvy + dalších dokumentů (uložení příloh, logování apod.)

    # po úspěšném generování označíme jako schválené / připravené k podpisu
    dotaznik.stav = OsobniDotaznik.STAV_HR_SCHVALIL
    dotaznik.hr_schvalil = request.user
    dotaznik.hr_schvalil_at = timezone.now()
    dotaznik.save()

    return redirect("frontend:dotaznik_detail_hr", dotaznik_id=dotaznik.id)



@login_required
@require_POST
def hr_generate_wage_doc(request, dotaznik_id):
    profil = getattr(request.user, "profile", None)
    if not profil or profil.role != "hr":
        return redirect("frontend:provoz_dashboard")

    dotaznik = get_object_or_404(OsobniDotaznik, id=dotaznik_id)
    # TODO: generování mzdového dokumentu
    return redirect("frontend:dotaznik_detail_hr", dotaznik_id=dotaznik.id)


@login_required
@require_POST
def hr_schvalit_dotaznik(request, dotaznik_id):
    profil = getattr(request.user, "profile", None)
    if not profil or profil.role != "hr":
        return redirect("frontend:provoz_dashboard")

    dotaznik = get_object_or_404(OsobniDotaznik, id=dotaznik_id)

    dotaznik.stav = OsobniDotaznik.STAV_HR_SCHVALIL
    dotaznik.hr_schvalil = request.user
    dotaznik.hr_schvalil_at = timezone.now()
    dotaznik.save()
    return redirect("frontend:hr_dashboard")


# --- Provoz část ---------------------------------------------------------

@login_required
def provoz_dashboard(request):
    profil = getattr(request.user, "profile", None)
    if not profil or profil.role not in ("manager_provozu", "oblastni_manager"):
        return redirect("frontend:hr_dashboard")

    moje_provozy = Provoz.objects.none()
    if profil.spravovane_provozy.exists():
        moje_provozy = profil.spravovane_provozy.all().order_by(
            "cislo_provozu",
            "nazev",
        )

    if request.method == "POST":
        start_form = StartDotaznikForm(request.POST, user=request.user)
        if start_form.is_valid():
            provoz = start_form.cleaned_data["provoz"]

            # když není vybraný provoz (None), přidej chybu do formuláře
            if provoz is None:
                start_form.add_error("provoz", "Musíte vybrat provoz, než začnete dotazník.")
            else:
                # bezpečnost: provoz musí být mezi spravovanými
                if not profil.spravovane_provozy.filter(id=provoz.id).exists():
                    start_form.add_error("provoz", "Nemáte oprávnění k tomuto provozu.")
                else:
                    dotaznik = OsobniDotaznik.objects.create(
                        provoz=provoz,
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
        # když form není validní, jen propadne na render níže
    else:
        start_form = StartDotaznikForm(user=request.user)

    provozy_ids = moje_provozy.values_list("id", flat=True)

    dotazniky_rozpracovane = OsobniDotaznik.objects.filter(
        provoz_id__in=provozy_ids,
        stav__in=[
            OsobniDotaznik.STAV_DRAFT,
            OsobniDotaznik.STAV_VRACENO_PROVOZU,
        ],
    ).order_by("-created_at")

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
    profil = getattr(request.user, "profile", None)
    if not profil or profil.role not in ("manager_provozu", "oblastni_manager"):
        return redirect("frontend:hr_dashboard")

    dotaznik = get_object_or_404(OsobniDotaznik, id=dotaznik_id)

    povolene_stavy = [
        OsobniDotaznik.STAV_DRAFT,
        OsobniDotaznik.STAV_VRACENO_PROVOZU,
    ]
    if dotaznik.stav not in povolene_stavy:
        return redirect("frontend:provoz_dashboard")

    if not profil.spravovane_provozy.filter(id=dotaznik.provoz_id).exists():
        return redirect("frontend:provoz_dashboard")

    if request.method == "POST":
        print("=== DOTAZNIK_EDIT POST ===", request.POST.get("ulozit_dotaznik"), request.POST.get("pridat_prilohu"))

        if "ulozit_dotaznik" in request.POST:
            form = OsobniDotaznikEditForm(request.POST, instance=dotaznik)
            priloha_form = PrilohaForm()
            print("=== FORM DATA ===", form.data)

            if form.is_valid():
                obj = form.save()
                print("=== OK ULOZENO ===", obj.id)
                return redirect("frontend:provoz_dashboard")
            else:
                print("=== FORM ERRORS ===", form.errors.as_json())

        elif "pridat_prilohu" in request.POST:
            form = OsobniDotaznikEditForm(instance=dotaznik)
            priloha_form = PrilohaForm(request.POST, request.FILES)
            if priloha_form.is_valid():
                pridana = priloha_form.save(commit=False)
                pridana.dotaznik = dotaznik
                pridana.save()
                return redirect("frontend:dotaznik_edit", dotaznik_id=dotaznik.id)
        else:
            print("=== NEZNAME TLACITKO ===", request.POST.keys())
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
    profil = getattr(request.user, "profile", None)
    if not profil or profil.role not in ("manager_provozu", "oblastni_manager"):
        return redirect("frontend:hr_dashboard")

    dotaznik = get_object_or_404(OsobniDotaznik, id=dotaznik_id)

    if dotaznik.stav != OsobniDotaznik.STAV_DRAFT:
        return redirect("frontend:provoz_dashboard")

    if not profil.spravovane_provozy.filter(id=dotaznik.provoz_id).exists():
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
    profil = getattr(request.user, "profile", None)
    if not profil or profil.role not in ("manager_provozu", "oblastni_manager"):
        return redirect("frontend:hr_dashboard")

    dotaznik = get_object_or_404(OsobniDotaznik, id=dotaznik_id)

    if dotaznik.stav not in [
        OsobniDotaznik.STAV_DRAFT,
        OsobniDotaznik.STAV_VRACENO_PROVOZU,
    ]:
        return redirect("frontend:provoz_dashboard")

    if not profil.spravovane_provozy.filter(id=dotaznik.provoz_id).exists():
        return redirect("frontend:provoz_dashboard")

    return render(
        request,
        "frontend/dotaznik_kontrola.html",
        {"dotaznik": dotaznik},
    )


@login_required
@require_POST
def dotaznik_odeslat_hr(request, dotaznik_id):
    profil = getattr(request.user, "profile", None)
    if not profil or profil.role not in ("manager_provozu", "oblastni_manager"):
        return redirect("frontend:hr_dashboard")

    dotaznik = get_object_or_404(OsobniDotaznik, id=dotaznik_id)

    if dotaznik.stav not in [
        OsobniDotaznik.STAV_DRAFT,
        OsobniDotaznik.STAV_VRACENO_PROVOZU,
    ]:
        return redirect("frontend:provoz_dashboard")

    if not profil.spravovane_provozy.filter(id=dotaznik.provoz_id).exists():
        return redirect("frontend:provoz_dashboard")

    dotaznik.stav = OsobniDotaznik.STAV_PROVOZ_ODESLAL
    dotaznik.odeslal_na_hr = request.user
    dotaznik.odeslal_na_hr_at = timezone.now()
    dotaznik.save()
    return redirect("frontend:provoz_dashboard")


@login_required
def dotaznik_detail_provoz(request, dotaznik_id):
    profil = getattr(request.user, "profile", None)
    if not profil or profil.role not in ("manager_provozu", "oblastni_manager"):
        return redirect("frontend:hr_dashboard")

    dotaznik = get_object_or_404(OsobniDotaznik, id=dotaznik_id)

    if not profil.spravovane_provozy.filter(id=dotaznik.provoz_id).exists():
        return redirect("frontend:provoz_dashboard")

    return render(
        request,
        "frontend/dotaznik_detail_provoz.html",
        {"dotaznik": dotaznik},
    )


@login_required
@require_POST
def priloha_delete(request, priloha_id):
    profil = getattr(request.user, "profile", None)
    if not profil or profil.role not in ("manager_provozu", "oblastni_manager"):
        return redirect("frontend:hr_dashboard")

    priloha = get_object_or_404(OsobniDotaznikPriloha, id=priloha_id)
    dotaznik = priloha.dotaznik

    if not profil.spravovane_provozy.filter(id=dotaznik.provoz_id).exists():
        return redirect("frontend:provoz_dashboard")

    print("Mazání přílohy:", priloha.id, priloha.soubor.name)
    priloha.delete()
    return HttpResponseRedirect(
        reverse("frontend:dotaznik_edit", kwargs={"dotaznik_id": dotaznik.id}) + "#prilohy"
    )


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


@login_required
@require_POST
def priloha_add(request, dotaznik_id):
    profil = getattr(request.user, "profile", None)
    if not profil or profil.role not in ("manager_provozu", "oblastni_manager"):
        return redirect("frontend:hr_dashboard")

    dotaznik = get_object_or_404(OsobniDotaznik, id=dotaznik_id)

    if not profil.spravovane_provozy.filter(id=dotaznik.provoz_id).exists():
        return redirect("frontend:provoz_dashboard")

    form = PrilohaForm(request.POST, request.FILES)
    if form.is_valid():
        priloha = form.save(commit=False)
        priloha.dotaznik = dotaznik
        priloha.save()

    return redirect("frontend:dotaznik_edit", dotaznik_id=dotaznik.id)


from django.http import FileResponse
import mimetypes

@login_required
def priloha_download(request, priloha_id):
    profil = getattr(request.user, "profile", None)
    # provoz i HR mají mít přístup – uprav podle potřeby
    if not profil or profil.role not in ("manager_provozu", "oblastni_manager", "hr"):
        return redirect("frontend:login")

    priloha = get_object_or_404(OsobniDotaznikPriloha, id=priloha_id)
    dotaznik = priloha.dotaznik

    # kontrola provozu pro provozní role
    if profil.role in ("manager_provozu", "oblastni_manager"):
        if not profil.spravovane_provozy.filter(id=dotaznik.provoz_id).exists():
            return redirect("frontend:provoz_dashboard")

    # HR může všechny – pokud chceš omezit, přidej logiku

    filename = priloha.soubor.name.split("/")[-1]
    content_type, _ = mimetypes.guess_type(filename)

    response = FileResponse(priloha.soubor.open("rb"), as_attachment=True, filename=filename)
    if content_type:
        response["Content-Type"] = content_type
    return response

@login_required
@require_POST
def hr_vratit_provozu(request, dotaznik_id):
    profil = getattr(request.user, "profile", None)
    if not profil or profil.role != "hr":
        return redirect("frontend:provoz_dashboard")

    dotaznik = get_object_or_404(OsobniDotaznik, id=dotaznik_id)

    poznamka = request.POST.get("hr_poznamka_pro_provoz", "").strip()

    dotaznik.hr_poznamka_pro_provoz = poznamka
    dotaznik.stav = OsobniDotaznik.STAV_VRACENO_PROVOZU
    dotaznik.hr_vratil_provozu = request.user
    dotaznik.hr_vraceno_provozu_at = timezone.now()
    dotaznik.save()

    return redirect("frontend:hr_dashboard")
from docxtpl import DocxTemplate
from django.conf import settings
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.core.files.storage import default_storage
from io import BytesIO
import os
import uuid


@login_required
def generovat_mzdovy_vymer(request, dotaznik_id):
    dotaznik = get_object_or_404(OsobniDotaznik, id=dotaznik_id)

    template_path = os.path.join(
        settings.BASE_DIR,
        "templates",
        "dokumenty",
        "mzdovy_vymer.docx",
    )
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Šablona DOCX nenalezena: {template_path}")

    doc = DocxTemplate(template_path)

    context = {
        "first_name": dotaznik.jmeno or "",
        "last_name": dotaznik.prijmeni or "",
        "date_of_birth": dotaznik.datum_narozeni.strftime("%d.%m.%Y")
        if dotaznik.datum_narozeni
        else "",
        "workplace_name": dotaznik.provoz.nazev if dotaznik.provoz else "",
        "workplace_address": getattr(dotaznik.provoz, "adresa", "")
        if dotaznik.provoz
        else "",
        "wage_effective_from": dotaznik.datum_nastupu.strftime("%d.%m.%Y")
        if dotaznik.datum_nastupu
        else "",
        "base_salary": (
            f"{dotaznik.mzda_hruba:,.0f}".replace(",", " ")
            if dotaznik.mzda_hruba
            else "0"
        ),
        "variable_salary": "0",
    }

    doc.render(context)

    docx_io = BytesIO()
    doc.save(docx_io)
    docx_io.seek(0)

    # název souboru
    safe_jmeno = (dotaznik.jmeno or "").strip().replace(" ", "_")
    safe_prijmeni = (dotaznik.prijmeni or "").strip().replace(" ", "_")
    uniq = uuid.uuid4().hex[:6]
    filename_base = f"mzdovy_vymer_{safe_prijmeni}_{safe_jmeno}_{uniq}"

    # get_or_create dokument
    dokument, created = GenerovanyDokument.objects.get_or_create(
        dotaznik=dotaznik,
        typ="mzdovy_vymer",
        defaults={
            "nazev": f"Mzdový výměr {dotaznik.prijmeni} {dotaznik.jmeno}",
        },
    )

    # smazat starý soubor, pokud existuje
    if dokument.docx_soubor:
        default_storage.delete(dokument.docx_soubor.name)

    dokument.nazev = f"Mzdový výměr {dotaznik.prijmeni} {dotaznik.jmeno}"
    
    # uložit nový soubor (jen JEDNOU!)
    dokument.docx_soubor.save(
        f"{filename_base}.docx",
        ContentFile(docx_io.read()),
        save=True,
    )

    url = reverse("frontend:dotaznik_detail_hr", kwargs={"dotaznik_id": dotaznik.id})
    return redirect(f"{url}#dokumenty")


@login_required
def dokument_delete(request, dokument_id):
    dokument = get_object_or_404(GenerovanyDokument, id=dokument_id)
    dotaznik_id = dokument.dotaznik_id

    if request.method == "POST":
        if dokument.docx_soubor:
            dokument.docx_soubor.delete(save=False)
        if dokument.pdf_soubor:
            dokument.pdf_soubor.delete(save=False)
        dokument.delete()

    return redirect("frontend:dotaznik_detail_hr", dotaznik_id=dotaznik_id)


# views.py
from django.db.models import Exists, OuterRef, Q
from django.utils import timezone
from osobni_dotaznik.models import OsobniDotaznik, GenerovanyDokument
from datetime import timedelta
from django.db.models import Exists, OuterRef, Q
from django.utils import timezone

@login_required
def hr_contract_registry(request):
    profil = getattr(request.user, "profile", None)
    if not profil or profil.role != "hr":
        return redirect("frontend:provoz_dashboard")

    today = timezone.localdate()

    q_docs = GenerovanyDokument.objects.filter(
        dotaznik=OuterRef("pk"),
        typ="mzdovy_vymer",
    )

    # základní set – všichni se schváleným dotazníkem a dokumentem
    dotazniky = (
        OsobniDotaznik.objects.annotate(
            has_doc=Exists(q_docs),
        )
        .filter(
            stav=OsobniDotaznik.STAV_HR_SCHVALIL,
            has_doc=True,
        )
        .select_related("provoz", "pozice")
        .order_by("prijmeni", "jmeno")
    )

    search = request.GET.get("q", "").strip()
    if search:
        dotazniky = dotazniky.filter(
            Q(jmeno__icontains=search)
            | Q(prijmeni__icontains=search)
            | Q(provoz__nazev__icontains=search)
            | Q(pozice__nazev__icontains=search)
        )

    # --- brzy končící smlouvy / zkušebky ---
    KONCI_DO_DNI = 30
    end_limit = today + timedelta(days=KONCI_DO_DNI)

    koncici_smlouvy = (
        dotazniky.filter(
            doba_urcita_do__isnull=False,
            doba_urcita_do__gte=today,
            doba_urcita_do__lte=end_limit,
        )
        .order_by("doba_urcita_do", "prijmeni", "jmeno")[:50]
    )

    koncici_zkusebky = (
        dotazniky.filter(
            zkusebka_konec__isnull=False,
            zkusebka_konec__gte=today,
            zkusebka_konec__lte=end_limit,
        )
        .order_by("zkusebka_konec", "prijmeni", "jmeno")[:50]
    )

    context = {
        "dotazniky": dotazniky,
        "search": search,
        "today": today,
        "koncici_smlouvy": koncici_smlouvy,
        "koncici_zkusebky": koncici_zkusebky,
    }
    return render(request, "frontend/hr_contract_registry.html", context)

from datetime import timedelta

@login_required
def provoz_contract_registry(request):
    profil = getattr(request.user, "profile", None)
    if not profil or profil.role not in ("manager_provozu", "oblastni_manager"):
        return redirect("frontend:hr_dashboard")

    today = timezone.localdate()

    moje_provozy_ids = profil.spravovane_provozy.values_list("id", flat=True)

    q_docs = GenerovanyDokument.objects.filter(
        dotaznik=OuterRef("pk"),
        typ="mzdovy_vymer",
    )

    dotazniky = (
        OsobniDotaznik.objects.annotate(
            has_doc=Exists(q_docs),
        )
        .filter(
            stav=OsobniDotaznik.STAV_HR_SCHVALIL,
            has_doc=True,
            provoz_id__in=moje_provozy_ids,
        )
        .select_related("provoz", "pozice")
        .order_by("prijmeni", "jmeno")
    )

    search = request.GET.get("q", "").strip()
    if search:
        dotazniky = dotazniky.filter(
            Q(jmeno__icontains=search)
            | Q(prijmeni__icontains=search)
            | Q(provoz__nazev__icontains=search)
            | Q(pozice__nazev__icontains=search)
        )

    KONCI_DO_DNI = 30
    end_limit = today + timedelta(days=KONCI_DO_DNI)

    koncici_smlouvy = (
        dotazniky.filter(
            doba_urcita_do__isnull=False,
            doba_urcita_do__gte=today,
            doba_urcita_do__lte=end_limit,
        )
        .order_by("doba_urcita_do", "prijmeni", "jmeno")[:50]
    )

    koncici_zkusebky = (
        dotazniky.filter(
            zkusebka_konec__isnull=False,
            zkusebka_konec__gte=today,
            zkusebka_konec__lte=end_limit,
        )
        .order_by("zkusebka_konec", "prijmeni", "jmeno")[:50]
    )

    context = {
        "dotazniky": dotazniky,
        "search": search,
        "today": today,
        "koncici_smlouvy": koncici_smlouvy,
        "koncici_zkusebky": koncici_zkusebky,
    }
    return render(request, "frontend/hr_contract_registry.html", context)


# views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from osobni_dotaznik.models import OsobniDotaznik

@login_required
def employee_detail(request, dotaznik_id):
    profil = getattr(request.user, "profile", None)
    if not profil:
        return redirect("frontend:login")

    dotaznik = get_object_or_404(OsobniDotaznik, id=dotaznik_id)

    # HR může vidět vše
    if profil.role == "hr":
        pass
    # provoz / oblastní manažer jen své provozy
    elif profil.role in ("manager_provozu", "oblastni_manager"):
        if not profil.spravovane_provozy.filter(id=dotaznik.provoz_id).exists():
            return redirect("frontend:provoz_dashboard")
    else:
        # ostatní role nepustit
        return redirect("frontend:login")

    return render(
        request,
        "frontend/employee_detail.html",  # nebo existující šablona, kterou používáš
        {"dotaznik": dotaznik},
    )


from django.contrib import messages
from django.utils import timezone

@login_required
@require_POST
def hr_generate_documents(request, dotaznik_id):
    profil = getattr(request.user, "profile", None)
    if not profil or profil.role != "hr":
        return redirect("frontend:provoz_dashboard")

    dotaznik = get_object_or_404(OsobniDotaznik, id=dotaznik_id)

    # 1) vygenerovat mzdový výměr (a případně další dokumenty)
    try:
        _vygenerovat_mzdovy_vymer_for_dotaznik(dotaznik)
        # sem případně přidáš další generování (pracovní smlouva apod.)
    except Exception as e:
        messages.error(request, f"Chyba při generování dokumentů: {e}")
        return redirect("frontend:dotaznik_detail_hr", dotaznik_id=dotaznik.id)

    # 2) označit jako schválené HR
    dotaznik.stav = OsobniDotaznik.STAV_HR_SCHVALIL
    dotaznik.hr_schvalil = request.user
    dotaznik.hr_schvalil_at = timezone.now()
    dotaznik.save()

    messages.success(request, "Dokumenty byly vygenerovány a dotazník byl označen jako schválený HR.")
    return redirect("frontend:dotaznik_detail_hr", dotaznik_id=dotaznik.id)



from io import BytesIO
import uuid
import os
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from docxtpl import DocxTemplate

def _vygenerovat_mzdovy_vymer_for_dotaznik(dotaznik):
    template_path = os.path.join(
        settings.BASE_DIR,
        "templates",
        "dokumenty",
        "mzdovy_vymer.docx",
    )
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Šablona DOCX nenalezena: {template_path}")

    doc = DocxTemplate(template_path)

    context = {
        "first_name": dotaznik.jmeno or "",
        "last_name": dotaznik.prijmeni or "",
        "date_of_birth": dotaznik.datum_narozeni.strftime("%d.%m.%Y")
        if dotaznik.datum_narozeni else "",
        "workplace_name": dotaznik.provoz.nazev if dotaznik.provoz else "",
        "workplace_address": getattr(dotaznik.provoz, "adresa", "")
        if dotaznik.provoz else "",
        "wage_effective_from": dotaznik.datum_nastupu.strftime("%d.%m.%Y")
        if dotaznik.datum_nastupu else "",
        "base_salary": (
            f"{dotaznik.mzda_hruba:,.0f}".replace(",", " ")
            if dotaznik.mzda_hruba else "0"
        ),
        "variable_salary": "0",
    }

    doc.render(context)
    docx_io = BytesIO()
    doc.save(docx_io)
    docx_io.seek(0)

    safe_jmeno = (dotaznik.jmeno or "").strip().replace(" ", "_")
    safe_prijmeni = (dotaznik.prijmeni or "").strip().replace(" ", "_")
    uniq = uuid.uuid4().hex[:6]
    filename_base = f"mzdovy_vymer_{safe_prijmeni}_{safe_jmeno}_{uniq}"

    dokument, created = GenerovanyDokument.objects.get_or_create(
        dotaznik=dotaznik,
        typ="mzdovy_vymer",
        defaults={
            "nazev": f"Mzdový výměr {dotaznik.prijmeni} {dotaznik.jmeno}",
        },
    )

    if dokument.docx_soubor:
        default_storage.delete(dokument.docx_soubor.name)

    dokument.nazev = f"Mzdový výměr {dotaznik.prijmeni} {dotaznik.jmeno}"
    dokument.docx_soubor.save(
        f"{filename_base}.docx",
        ContentFile(docx_io.read()),
        save=True,
    )

    return dokument
