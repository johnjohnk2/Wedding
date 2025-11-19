from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.conf import settings
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

    readonly_fields = (
        "invitation_id",
        "invitation_url",
        "invitation_message",   # ⭐️ Nouveau champ
        "nb_mairie",
        "nb_soiree",
        "is_attending",
    )

    def invitation_url(self, obj):
        if not obj.invitation_id:
            return "(Pas de lien)"
        base = settings.WEDDING_WEBSITE_URL.rstrip("/")
        url = f"{base}{reverse('invitation', args=[obj.invitation_id])}"
        return format_html('<a href="{}" target="_blank">{}</a>', url, url)

    invitation_url.short_description = "Lien d'invitation"

    # ⭐️ CHAMP MESSAGE PRÊT À COPIER-COLLER
    def invitation_message(self, obj):
        if not obj.invitation_id:
            return "(Pas de message — pas d'invitation)"

        # URL des infos du mariage
        info_url = "https://wedding.johnjohnk.duckdns.org/"

        # URL RSVP personnalisée
        base = settings.WEDDING_WEBSITE_URL.rstrip("/")
        rsvp_url = f"{base}{reverse('invitation', args=[obj.invitation_id])}"

        return format_html(
            "<div style='white-space: pre-wrap;'>"
            "Bonjour {name},\n\n"
            "Voici toutes les informations concernant notre mariage :\n"
            "👉 <a href='{info}' target='_blank'>{info}</a>\n\n"
            "Et voici votre lien personnalisé pour confirmer votre présence (carton réponse) :\n"
            "👉 <a href='{rsvp}' target='_blank'>{rsvp}</a>\n\n"
            "Votre carton réponse est mis à jour en temps réel et vous pouvez modifier "
            "votre réponse à tout moment.\n\n"
            "À très vite ✨\n"
            "Jonathan & Juliette"
            "</div>",
            name=obj.name,
            info=info_url,
            rsvp=rsvp_url,
        )

    invitation_message.short_description = "Message prêt à copier-coller"


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "party", "is_child", "is_attending")
    list_filter = ("is_child", "is_attending")
    search_fields = ("first_name", "last_name", "party__name")

    def short_comment(self, obj):
        if obj.comments:
            return obj.comments[:40] + ("…" if len(obj.comments) > 40 else "")
        return ""

    short_comment.short_description = "Commentaire"
