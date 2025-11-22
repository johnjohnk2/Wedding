from django.contrib import admin
from .models import Guest, Party


class GuestInline(admin.TabularInline):
    model = Guest
    extra = 0
    fields = ("first_name", "last_name", "is_child", "is_attending")
    readonly_fields = ("first_name", "last_name")


@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ("name", "nb_mairie", "nb_soiree", "is_attending")
    list_filter = ("is_attending",)
    search_fields = ("name",)
    inlines = [GuestInline]
    readonly_fields = ("invitation_id", "nb_mairie", "nb_soiree", "is_attending")

@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "party", "is_child", "is_attending")
    list_filter = ("is_child", "is_attending")
    search_fields = ("first_name", "last_name", "party__name")

