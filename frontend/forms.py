from django import forms
from osobni_dotaznik.models import OsobniDotaznik


class StartDotaznikForm(forms.ModelForm):
    class Meta:
        model = OsobniDotaznik
        fields = ["provoz", "pozice"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user and hasattr(user, "profile"):
            profil = user.profile
            if profil.spravovane_provozy.exists():
                self.fields["provoz"].queryset = profil.spravovane_provozy.all()


from django import forms
from osobni_dotaznik.models import OsobniDotaznik, OsobniDotaznikPriloha


class OsobniDotaznikEditForm(forms.ModelForm):
    class Meta:
        model = OsobniDotaznik
        fields = [
            "provoz",
            "pozice",
            "typ_pomeru",
            # stav z formuláře neukazujeme
            "titul",
            "jmeno",
            "prijmeni",
            "rodna_prijmeni",
            "rodne_cislo",
            "datum_narozeni",
            "misto_narozeni",
            "statni_obcanstvi",
            "rodinny_stav",
            "telefon",
            "email",
            "zdravotni_pojistovna",
            "cislo_uctu",
            "kod_banky",
            "nazev_banky",
            "trvale_ulice",
            "trvale_cislo_popisne",
            "trvale_mesto",
            "trvale_psc",
            "dorucovaci_ulice",
            "dorucovaci_cislo_popisne",
            "dorucovaci_mesto",
            "dorucovaci_psc",
            "duchod_predcasny",
            "duchod_starobni",
            "duchod_invalidni",
            "duchod_datum_vzniku",
            "duchod_kdo_vyplaci",
            "duchod_kdo_dopl_info",
            "vzdelani_zakladni",
            "vzdelani_sou",
            "vzdelani_ss",
            "vzdelani_gymnazium",
            "vzdelani_vs",
            "vzdelani_misto_studia",
            "vzdelani_cr_zahranici",
            "vzdelani_rok_ukonceni",
            "vzdelani_mesto_obec",
            "vzdelani_skola_nazev",
            "vzdelani_obor",
            "vzdelani_zakonceno_vyucni_list",
            "vzdelani_zakonceno_maturita",
            "vzdelani_zakonceno_diplom",
            "posledni_zam_nazev_firmy",
            "posledni_zam_pracovni_zarazeni",
            "posledni_zam_od",
            "posledni_zam_do",
            "cizinec_cislo_dokladu",
            "cizinec_povoleni_prace",
            "cizinec_povoleni_pobytu",
            "cizinec_adresa_ulice",
            "cizinec_adresa_cislo",
            "cizinec_adresa_psc",
            "cizinec_adresa_stat_mesto",
            "pojisteni_cizina_byl",
            "pojisteni_cizina_nazev_adresa_nositele",
            "pojisteni_cizina_cislo_pojisteni",
            "srazky_existuji",
            "pocet_vyzivovanych_osob",
            "srazky_vymahajici_orgam_a_cj",
            "zmenena_prac_schopnost",
            "vedeni_v_evidenci_up",
            "jiny_pracovni_pomer",
            "je_osvc",
            "zapoctovy_list_predlozen",
            "cisty_trestni_rejstrik",
            "jine_poznamky",
        ]
        widgets = {
            # texty
            "titul": forms.TextInput(attrs={"class": "form-control form-control-sm"}),
            "jmeno": forms.TextInput(attrs={"class": "form-control form-control-sm"}),
            "prijmeni": forms.TextInput(attrs={"class": "form-control form-control-sm"}),
            "rodna_prijmeni": forms.TextInput(attrs={"class": "form-control form-control-sm"}),
            "rodne_cislo": forms.TextInput(attrs={"class": "form-control form-control-sm"}),
            "misto_narozeni": forms.TextInput(attrs={"class": "form-control form-control-sm"}),
            "statni_obcanstvi": forms.TextInput(attrs={"class": "form-control form-control-sm"}),
            "rodinny_stav": forms.TextInput(attrs={"class": "form-control form-control-sm"}),
            "telefon": forms.TextInput(attrs={"class": "form-control form-control-sm"}),
            "email": forms.EmailInput(attrs={"class": "form-control form-control-sm"}),
            "zdravotni_pojistovna": forms.TextInput(attrs={"class": "form-control form-control-sm"}),
            "cislo_uctu": forms.TextInput(attrs={"class": "form-control form-control-sm"}),
            "kod_banky": forms.TextInput(attrs={"class": "form-control form-control-sm"}),
            "nazev_banky": forms.TextInput(attrs={"class": "form-control form-control-sm"}),

            "trvale_ulice": forms.TextInput(attrs={"class": "form-control form-control-sm"}),
            "trvale_cislo_popisne": forms.TextInput(attrs={"class": "form-control form-control-sm"}),
            "trvale_mesto": forms.TextInput(attrs={"class": "form-control form-control-sm"}),
            "trvale_psc": forms.TextInput(attrs={"class": "form-control form-control-sm"}),

            "dorucovaci_ulice": forms.TextInput(attrs={"class": "form-control form-control-sm"}),
            "dorucovaci_cislo_popisne": forms.TextInput(attrs={"class": "form-control form-control-sm"}),
            "dorucovaci_mesto": forms.TextInput(attrs={"class": "form-control form-control-sm"}),
            "dorucovaci_psc": forms.TextInput(attrs={"class": "form-control form-control-sm"}),

            "duchod_kdo_vyplaci": forms.TextInput(attrs={"class": "form-control form-control-sm"}),
            "duchod_kdo_dopl_info": forms.TextInput(attrs={"class": "form-control form-control-sm"}),

            "vzdelani_misto_studia": forms.TextInput(attrs={"class": "form-control form-control-sm"}),
            "vzdelani_cr_zahranici": forms.TextInput(attrs={"class": "form-control form-control-sm"}),
            "vzdelani_rok_ukonceni": forms.TextInput(attrs={"class": "form-control form-control-sm"}),
            "vzdelani_mesto_obec": forms.TextInput(attrs={"class": "form-control form-control-sm"}),
            "vzdelani_skola_nazev": forms.TextInput(attrs={"class": "form-control form-control-sm"}),
            "vzdelani_obor": forms.TextInput(attrs={"class": "form-control form-control-sm"}),

            "posledni_zam_nazev_firmy": forms.TextInput(attrs={"class": "form-control form-control-sm"}),
            "posledni_zam_pracovni_zarazeni": forms.TextInput(attrs={"class": "form-control form-control-sm"}),
            "posledni_zam_od": forms.TextInput(attrs={
                "class": "form-control form-control-sm",
                "placeholder": "MM/RRRR",
            }),
            "posledni_zam_do": forms.TextInput(attrs={
                "class": "form-control form-control-sm",
                "placeholder": "MM/RRRR",
            }),

            "cizinec_cislo_dokladu": forms.TextInput(attrs={"class": "form-control form-control-sm"}),
            "cizinec_povoleni_prace": forms.TextInput(attrs={"class": "form-control form-control-sm"}),
            "cizinec_povoleni_pobytu": forms.TextInput(attrs={"class": "form-control form-control-sm"}),
            "cizinec_adresa_ulice": forms.TextInput(attrs={"class": "form-control form-control-sm"}),
            "cizinec_adresa_cislo": forms.TextInput(attrs={"class": "form-control form-control-sm"}),
            "cizinec_adresa_psc": forms.TextInput(attrs={"class": "form-control form-control-sm"}),
            "cizinec_adresa_stat_mesto": forms.TextInput(attrs={"class": "form-control form-control-sm"}),

            "pojisteni_cizina_nazev_adresa_nositele": forms.Textarea(attrs={
                "class": "form-control form-control-sm",
                "rows": 3,
            }),
            "pojisteni_cizina_cislo_pojisteni": forms.TextInput(attrs={"class": "form-control form-control-sm"}),

            "srazky_vymahajici_orgam_a_cj": forms.Textarea(attrs={
                "class": "form-control form-control-sm",
                "rows": 3,
            }),

            "jine_poznamky": forms.Textarea(attrs={
                "class": "form-control form-control-sm",
                "rows": 3,
            }),

            # datumy
            "datum_narozeni": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control form-control-sm",
                },
                format="%Y-%m-%d",
            ),
            "duchod_datum_vzniku": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control form-control-sm",
                },
                format="%Y-%m-%d",
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["provoz"].disabled = True
        if "typ_pomeru" in self.fields:
            self.fields["typ_pomeru"].widget.attrs.update(
                {"class": "form-select form-select-sm"}
            )
        # formáty pro HTML5 date input
        self.fields["datum_narozeni"].input_formats = ["%Y-%m-%d"]
        self.fields["duchod_datum_vzniku"].input_formats = ["%Y-%m-%d"]

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.stav = OsobniDotaznik.STAV_DRAFT
        if commit:
            obj.save()
        return obj




from osobni_dotaznik.models import OsobniDotaznikPriloha

class PrilohaForm(forms.ModelForm):
    class Meta:
        model = OsobniDotaznikPriloha
        fields = ["soubor", "popis"]
        widgets = {
            "soubor": forms.ClearableFileInput(attrs={"class": "form-control form-control-sm"}),
            "popis": forms.TextInput(attrs={
                "class": "form-control form-control-sm",
                "placeholder": "Např. občanský průkaz, potvrzení o studiu…",
            }),
        }

    def clean(self):
        cleaned = super().clean()
        soubor = cleaned.get("soubor")
        popis = cleaned.get("popis")
        # pokud user klikne na „Nahrát“ bez souboru, klidně to ignorujeme
        if not soubor and not popis:
            raise forms.ValidationError("Vyberte prosím soubor nebo zadejte popis.")
        return cleaned

