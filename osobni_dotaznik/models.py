from django.db import models
from django.contrib.auth.models import User


class OsobniDotaznik(models.Model):
    # Workflow stavy
    STAV_DRAFT = "draft"
    STAV_PROVOZ_ODESLAL = "provoz_odeslal"
    STAV_HR_KONTROLUJE = "hr_kontroluje"
    STAV_HR_SCHVALIL = "hr_schvalil"
    STAV_VRACENO_PROVOZU = "vraceno_provozu"

    STAVY_CHOICES = [
        (STAV_DRAFT, "Rozpracovaný (provoz)"),
        (STAV_PROVOZ_ODESLAL, "Odesláno z provozu"),
        (STAV_HR_KONTROLUJE, "HR kontroluje"),
        (STAV_HR_SCHVALIL, "Schváleno HR"),
        (STAV_VRACENO_PROVOZU, "Vráceno na doplnění provozu"),
    ]

    TYP_POMERU_HPP = "HPP"
    TYP_POMERU_DPP = "DPP"
    TYP_POMERU_DPC = "DPC"

    TYP_POMERU_CHOICES = [
        (TYP_POMERU_HPP, "Hlavní pracovní poměr"),
        (TYP_POMERU_DPP, "Dohoda o provedení práce"),
        (TYP_POMERU_DPC, "Dohoda o pracovní činnosti"),
    ]

    provoz = models.ForeignKey(
        "core.Provoz",
        on_delete=models.PROTECT,
        related_name="dotazniky",
        null=True,
        blank=True,
    )
    pozice = models.ForeignKey(
        "core.Pozice",
        on_delete=models.PROTECT,
        related_name="dotazniky",
        null=True,
        blank=True,
    )

    typ_pomeru = models.CharField(
        "Typ pracovního poměru",
        max_length=10,
        choices=TYP_POMERU_CHOICES,
        null=True,
        blank=True,
    )

    # Kdo a kdy dotazník založil / odeslal
    created_at = models.DateTimeField(
        "Datum založení",
        auto_now_add=True,
    )
    created_by = models.ForeignKey(
        User,
        verbose_name="Vytvořil (uživatel)",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dotazniky_vytvorene",
    )
    updated_at = models.DateTimeField(
        "Datum poslední změny",
        auto_now=True,
    )
    stav = models.CharField(
        "Stav dotazníku",
        max_length=32,
        choices=STAVY_CHOICES,
        default=STAV_DRAFT,
    )

    # Osobní údaje
    titul = models.CharField(
        "Titul",
        max_length=50,
        blank=True,
        help_text="Např. Bc., Mgr., Ing.",
    )
    jmeno = models.CharField(
        "Jméno",
        max_length=100,
    )
    prijmeni = models.CharField(
        "Příjmení",
        max_length=100,
    )
    rodna_prijmeni = models.CharField(
        "Rodné a všechna dřívější příjmení",
        max_length=255,
        blank=True,
    )
    datum_narozeni = models.DateField(
        "Datum narození",
    )
    misto_narozeni = models.CharField(
        "Místo narození",
        max_length=255,
    )
    statni_obcanstvi = models.CharField(
        "Státní občanství",
        max_length=255,
    )
    rodinny_stav = models.CharField(
        "Rodinný stav",
        max_length=255,
        blank=True,
    )
    telefon = models.CharField(
        "Telefon",
        max_length=50,
        blank=True,
    )  # * nepovinné
    email = models.EmailField(
        "E-mail",
        blank=True,
    )  # * nepovinné
    rodne_cislo = models.CharField(
        "Rodné číslo",
        max_length=20,
    )
    zdravotni_pojistovna = models.CharField(
        "Zdravotní pojišťovna",
        max_length=255,
    )

    # Bankovní spojení
    cislo_uctu = models.CharField(
        "Číslo účtu",
        max_length=50,
    )
    kod_banky = models.CharField(
        "Kód banky",
        max_length=10,
    )
    nazev_banky = models.CharField(
        "Název banky / spořitelny",
        max_length=255,
        blank=True,
    )

    # Adresa trvalého bydliště
    trvale_ulice = models.CharField(
        "Trvalé bydliště – ulice",
        max_length=255,
    )
    trvale_cislo_popisne = models.CharField(
        "Trvalé bydliště – číslo popisné/orientační",
        max_length=50,
    )
    trvale_mesto = models.CharField(
        "Trvalé bydliště – město/obec",
        max_length=255,
    )
    trvale_psc = models.CharField(
        "Trvalé bydliště – PSČ",
        max_length=20,
    )

    # Doručovací adresa
    dorucovaci_ulice = models.CharField(
        "Doručovací adresa – ulice",
        max_length=255,
        blank=True,
    )
    dorucovaci_cislo_popisne = models.CharField(
        "Doručovací adresa – číslo popisné/orientační",
        max_length=50,
        blank=True,
    )
    dorucovaci_mesto = models.CharField(
        "Doručovací adresa – město/obec",
        max_length=255,
        blank=True,
    )
    dorucovaci_psc = models.CharField(
        "Doručovací adresa – PSČ",
        max_length=20,
        blank=True,
    )

    # Informace o pobírání důchodu
    duchod_predcasny = models.BooleanField(
        "Předčasný důchod",
        default=False,
    )
    duchod_starobni = models.BooleanField(
        "Starobní důchod",
        default=False,
    )
    duchod_invalidni = models.BooleanField(
        "Invalidní důchod",
        default=False,
    )
    duchod_datum_vzniku = models.CharField(
        "Datum vzniku nároku na důchod",
        max_length=255,
        blank=True,
    )
    duchod_kdo_vyplaci = models.CharField(
        "Kdo důchod vyplácí",
        max_length=255,
        blank=True,
    )
    duchod_kdo_dopl_info = models.CharField(
        "Další informace k důchodu",
        max_length=255,
        blank=True,
    )

    # Vzdělání
    vzdelani_zakladni = models.BooleanField(
        "Základní škola",
        default=False,
    )
    vzdelani_sou = models.BooleanField(
        "Střední odborné učiliště",
        default=False,
    )
    vzdelani_ss = models.BooleanField(
        "Střední škola",
        default=False,
    )
    vzdelani_gymnazium = models.BooleanField(
        "Gymnázium",
        default=False,
    )
    vzdelani_vs = models.BooleanField(
        "Vysoká škola",
        default=False,
    )
    vzdelani_misto_studia = models.CharField(
        "Vzdělání – místo studia",
        max_length=255,
        blank=True,
    )
    vzdelani_cr_zahranici = models.CharField(
        "Vzdělání – ČR / zahraničí",
        max_length=50,
        blank=True,  # např. "ČR" / "zahraničí"
    )
    vzdelani_rok_ukonceni = models.CharField(
        "Vzdělání – rok ukončení",
        max_length=10,
        blank=True,
    )
    vzdelani_mesto_obec = models.CharField(
        "Vzdělání – město/obec",
        max_length=255,
        blank=True,
    )
    vzdelani_skola_nazev = models.CharField(
        "Vzdělání – škola (název)",
        max_length=255,
        blank=True,
    )
    vzdelani_obor = models.CharField(
        "Vzdělání – obor",
        max_length=255,
        blank=True,
    )
    vzdelani_zakonceno_vyucni_list = models.BooleanField(
        "Zakončeno – výuční list",
        default=False,
    )
    vzdelani_zakonceno_maturita = models.BooleanField(
        "Zakončeno – maturitní vysvědčení",
        default=False,
    )
    vzdelani_zakonceno_diplom = models.BooleanField(
        "Zakončeno – diplom",
        default=False,
    )

    # Poslední zaměstnavatel
    posledni_zam_nazev_firmy = models.CharField(
        "Poslední zaměstnavatel – název firmy",
        max_length=255,
        blank=True,
    )
    posledni_zam_pracovni_zarazeni = models.CharField(
        "Poslední zaměstnavatel – pracovní zařazení",
        max_length=255,
        blank=True,
    )
    posledni_zam_od = models.CharField(
        "Poslední zaměstnavatel – od",
        max_length=50,
        blank=True,
    )
    posledni_zam_do = models.CharField(
        "Poslední zaměstnavatel – do",
        max_length=50,
        blank=True,
    )

    # Údaje pro cizince
    cizinec_cislo_dokladu = models.CharField(
        "Číslo dokladu totožnosti (OP/PAS)",
        max_length=100,
        blank=True,
    )
    cizinec_povoleni_prace = models.CharField(
        "Povolení k výkonu práce",
        max_length=255,
        blank=True,
    )
    cizinec_povoleni_pobytu = models.CharField(
        "Povolení k pobytu na území ČR",
        max_length=255,
        blank=True,
    )
    cizinec_adresa_ulice = models.CharField(
        "Adresa cizince v ČR – ulice",
        max_length=255,
        blank=True,
    )
    cizinec_adresa_cislo = models.CharField(
        "Adresa cizince v ČR – číslo popisné/orientační",
        max_length=50,
        blank=True,
    )
    cizinec_adresa_stat_mesto = models.CharField(
        "Adresa cizince v ČR – stát/město",
        max_length=255,
        blank=True,
    )
    cizinec_adresa_psc = models.CharField(
        "Adresa cizince v ČR – PSČ",
        max_length=20,
        blank=True,
    )

    # Účast na nemocenském a důchodovém pojištění v cizině
    pojisteni_cizina_byl = models.BooleanField(
        "Účast na důchodovém pojištění v cizině – byl/a",
        default=False,
    )
    pojisteni_cizina_nazev_adresa_nositele = models.TextField(
        "Název a adresa cizozemského nositele pojištění",
        blank=True,
    )
    pojisteni_cizina_cislo_pojisteni = models.CharField(
        "Číslo cizozemského pojištění",
        max_length=255,
        blank=True,
    )

    # Nařízené srážky ze mzdy
    srazky_existuji = models.BooleanField(
        "Nařízené srážky ze mzdy existují",
        default=False,
    )
    srazky_vymahajici_orgam_a_cj = models.TextField(
        "Vymáhající orgán a číslo jednací (srážky)",
        blank=True,
    )
    pocet_vyzivovanych_osob = models.PositiveIntegerField(
        "Počet vyživovaných osob",
        default=0,
    )

    # Další údaje
    zmenena_prac_schopnost = models.BooleanField(
        "Změněná pracovní schopnost",
        default=False,
    )
    vedeni_v_evidenci_up = models.BooleanField(
        "Veden v evidenci úřadu práce",
        default=False,
    )
    jiny_pracovni_pomer = models.BooleanField(
        "Mám ještě jiný pracovní poměr",
        default=False,
    )
    je_osvc = models.BooleanField(
        "Jsem OSVČ",
        default=False,
    )
    zapoctovy_list_predlozen = models.BooleanField(
        "Zápočtový list předložen",
        default=False,
    )
    cisty_trestni_rejstrik = models.BooleanField(
        "Čistý trestní rejstřík",
        default=False,
    )
    jine_poznamky = models.TextField(
        "Jiné (poznámky)",
        blank=True,
    )
    hr_poznamka_pro_provoz = models.TextField(
        "Poznámka HR pro provoz",
        blank=True,
    )

    created_by = models.ForeignKey(
        User,
        verbose_name="Vytvořil uživatel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dotazniky_vytvorene",
    )

    odeslal_na_hr = models.ForeignKey(
        User,
        verbose_name="Odeslal na HR",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dotazniky_odeslane_na_hr",
    )
    odeslal_na_hr_at = models.DateTimeField(
        "Odesláno na HR",
        null=True,
        blank=True,
    )

    hr_posledni_kontrola = models.ForeignKey(
        User,
        verbose_name="Poslední kontrola HR",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dotazniky_kontrolovane_hr",
    )
    hr_posledni_kontrola_at = models.DateTimeField(
        "Datum poslední HR kontroly",
        null=True,
        blank=True,
    )

    hr_schvalil = models.ForeignKey(
        User,
        verbose_name="Schválil HR",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dotazniky_schvalene_hr",
    )
    hr_schvalil_at = models.DateTimeField(
        "Datum schválení HR",
        null=True,
        blank=True,
    )

    hr_vratil_provozu = models.ForeignKey(
        User,
        verbose_name="Vrátil na provoz",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dotazniky_vracene_provozu_hr",
    )
    hr_vraceno_provozu_at = models.DateTimeField(
        "Datum vrácení na provoz",
        null=True,
        blank=True,
    )

    hr_poznamka_pro_provoz = models.TextField(
        "Poznámka HR pro provoz",
        blank=True,
    )

    # Potvrzení
    potvrzeni_podpis_text = models.TextField(
        "Text k podpisu zaměstnance",
        blank=True,
    )

    # Pracovní zařazení / nastavení
    uvazek_fte = models.DecimalField(
        "Úvazek (FTE)",
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Např. 1.00, 0.75, 0.50",
    )
    pracovni_doba_popis = models.CharField(
        "Rozvržení pracovní doby",
        max_length=255,
        blank=True,
        help_text="Např. dvousměnný provoz, PO–PÁ, krátký/dlouhý týden…",
    )
    mzda_hruba = models.DecimalField(
        "Hrubá mzda / odměna",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Např. 25000.00 nebo hodinová sazba",
    )
    DOBA_NEURCITA = "neurcita"
    DOBA_URCITA = "urcita"
    DOBA_TRVANI_CHOICES = [
        (DOBA_NEURCITA, "Na dobu neurčitou"),
        (DOBA_URCITA, "Na dobu určitou"),
    ]

    doba_trvani = models.CharField(
        "Doba trvání pracovního poměru",
        max_length=20,
        choices=DOBA_TRVANI_CHOICES,
        null=True,
        blank=True,
    )
    doba_urcita_do = models.DateField(
        "Doba určitá do",
        null=True,
        blank=True,
        help_text="Vyplňte pouze pokud jde o dobu určitou.",
    )

    datum_nastupu = models.DateField(
        "Datum nástupu do práce",
        null=True,
        blank=True,
    )

    zkusebni_doba_mesice = models.PositiveIntegerField(
        "Délka zkušební doby (měsíce)",
        null=True,
        blank=True,
        help_text="Např. 3 měsíce",
    )

    def __str__(self):
        cele_jmeno = f"{self.jmeno} {self.prijmeni}"
        if self.titul:
            cele_jmeno = f"{self.titul} {cele_jmeno}"
        return f"{cele_jmeno} ({self.rodne_cislo})"


class OsobniDotaznikPriloha(models.Model):
    dotaznik = models.ForeignKey(
        OsobniDotaznik,
        on_delete=models.CASCADE,
        related_name="prilohy",
    )
    soubor = models.FileField(
        upload_to="dotaznik_prilohy/",
        verbose_name="Soubor",
        blank=True,
        null=True,
    )
    popis = models.CharField(
        "Popis (např. OP, potvrzení, ...)",
        max_length=255,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)


