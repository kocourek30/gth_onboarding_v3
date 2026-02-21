from django.db import models
from django.contrib.auth.models import User



class UserProfile(models.Model):
    ROLE_CHOICES = [
        ("manager_provozu", "Manažer provozu"),
        ("oblastni_manager", "Oblastní manažer"),
        ("hr", "HR"),
        ("reditelka", "Ředitelka"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=32, choices=ROLE_CHOICES)

    spravovane_provozy = models.ManyToManyField(
        "core.Provoz",
        verbose_name="Spravované provozy",
        blank=True,
        related_name="spravujici_uzivatele",
        help_text="Provozy, za které tento uživatel odpovídá (manažer provozu / oblastní manažer).",
    )

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    

class Provoz(models.Model):
    cislo_provozu = models.IntegerField()
    nazev = models.CharField(max_length=255)
    ulice = models.CharField(max_length=255)
    mesto = models.CharField(max_length=255)
    kraj = models.CharField(max_length=255)
    psc = models.CharField(max_length=20)
    manazer = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)

    def __str__(self):
        return f"{self.cislo_provozu} - {self.nazev}"


class Pozice(models.Model):
    nazev = models.CharField(max_length=100, unique=True)
    kod = models.CharField(
        max_length=50,
        unique=True,
        help_text="Strojový kód, např. KUCHAR, SEFKUCHAR, MANAZER_PROVOZU…",
    )

    aktivni = models.BooleanField(default=True)

    class Meta:
        ordering = ["nazev"]

    def __str__(self):
        return self.nazev


