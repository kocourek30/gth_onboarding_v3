from django.contrib import admin
from .models import OsobniDotaznik


@admin.register(OsobniDotaznik)
class OsobniDotaznikAdmin(admin.ModelAdmin):
    list_display = ("cele_jmeno", "rodne_cislo", "stav", "created_at")
    list_filter = ("stav", "created_at")
    search_fields = ("jmeno", "prijmeni", "rodne_cislo", "email")

    def cele_jmeno(self, obj):
        if obj.titul:
            return f"{obj.titul} {obj.jmeno} {obj.prijmeni}"
        return f"{obj.jmeno} {obj.prijmeni}"

    cele_jmeno.short_description = "Jméno a příjmení"
