from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import UserProfile, Provoz, Pozice


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    fk_name = "user"
    extra = 0
    # tady necháme bez filter_horizontal – inline stejně používá jen jednoduchý widget


class UserAdmin(DjangoUserAdmin):
    inlines = [UserProfileInline]
    fieldsets = (
        (None, {
            "fields": (
                "username",
                "password",
                "first_name",
                "last_name",
                "email",
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
                "last_login",
                "date_joined",
            )
        }),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "password1", "password2"),
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role")
    list_filter = ("role",)
    search_fields = ("user__username", "user__first_name", "user__last_name")
    filter_horizontal = ("spravovane_provozy",)  # ← tady bude dvousloupcový widget


class ProvozAdmin(admin.ModelAdmin):
    list_display = ("cislo_provozu", "nazev", "mesto", "kraj", "psc", "manazer", "email")
    search_fields = ("cislo_provozu", "nazev", "mesto", "kraj", "manazer", "email")
    list_per_page = 1000


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Provoz, ProvozAdmin)


@admin.register(Pozice)
class PoziceAdmin(admin.ModelAdmin):
    list_display = ("nazev", "kod", "aktivni")
    list_filter = ("aktivni",)
    search_fields = ("nazev", "kod")

