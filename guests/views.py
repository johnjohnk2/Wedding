import base64
from collections import namedtuple
import random
from datetime import datetime
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import Count, Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views.generic import ListView
from guests import csv_import
from guests.invitation import get_invitation_context, INVITATION_TEMPLATE, guess_party_by_invite_id_or_404, \
    send_invitation_email
from guests.models import Guest, Party
from guests.save_the_date import get_save_the_date_context, send_save_the_date_email, SAVE_THE_DATE_TEMPLATE, \
    SAVE_THE_DATE_CONTEXT_MAP


class GuestListView(ListView):
    model = Guest


@login_required
def export_guests(request):
    export = csv_import.export_guests()
    response = HttpResponse(export.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=all-guests.csv'
    return response


@login_required
def dashboard(request):
    parties_with_pending_invites = Party.objects.filter(
        is_invited=True, is_attending=None
    ).order_by('category', 'name')
    parties_with_unopen_invites = parties_with_pending_invites.filter(invitation_opened=None)
    parties_with_open_unresponded_invites = parties_with_pending_invites.exclude(invitation_opened=None)
    attending_guests = Guest.objects.filter(is_attending=True)
    category_breakdown = attending_guests.values('party__category').annotate(count=Count('*'))
    total_mairie = Party.objects.aggregate(Sum('nb_mairie'))['nb_mairie__sum'] or 0
    total_soiree = Party.objects.aggregate(Sum('nb_soiree'))['nb_soiree__sum'] or 0
    return render(request, 'guests/dashboard.html', context={
        'couple_name': settings.BRIDE_AND_GROOM,
        'website_url': settings.WEDDING_WEBSITE_URL,        
        'guests': Guest.objects.filter(is_attending=True).count(),
        'possible_guests': Guest.objects.filter(party__is_invited=True).exclude(is_attending=False).count(),
        'not_coming_guests': Guest.objects.filter(is_attending=False).count(),
        'pending_invites': parties_with_pending_invites.count(),
        'pending_guests': Guest.objects.filter(party__is_invited=True, is_attending=None).count(),
        'parties_with_unopen_invites': parties_with_unopen_invites,
        'parties_with_open_unresponded_invites': parties_with_open_unresponded_invites,
        'unopened_invite_count': parties_with_unopen_invites.count(),
        'total_invites': Party.objects.filter(is_invited=True).count(),
        'category_breakdown': category_breakdown,
        'guestlist': Guest.objects.filter(is_attending=True),
        'notcoming': Guest.objects.filter(is_attending=False),
        'total_mairie': total_mairie,
        'total_soiree': total_soiree,
    })


def invitation(request, invite_id):
    party = guess_party_by_invite_id_or_404(invite_id)
    guests = party.guest_set.all()

    if request.method == 'POST':
        # récupération des champs mairie / soirée
        nb_mairie = request.POST.get('nb_mairie') or 0
        nb_soiree = request.POST.get('nb_soiree') or 0

        try:
            nb_mairie = int(nb_mairie)
            nb_soiree = int(nb_soiree)
        except ValueError:
            nb_mairie = 0
            nb_soiree = 0

        max_guests = guests.count()

        nb_mairie = max(0, min(nb_mairie, max_guests))
        nb_soiree = max(0, min(nb_soiree, max_guests))

        party.nb_mairie = nb_mairie
        party.nb_soiree = nb_soiree

        # ✔️ un foyer "vient" s'il a au moins une personne à un des deux events
        party.is_attending = (nb_mairie + nb_soiree) > 0

        # ⭐️ nouvelle ligne : récupération du commentaire
        party.comments = request.POST.get('comments', '').strip()

        # sauvegarde
        party.save()

        # ✔️ mettre à jour chaque Guest pour refléter la décision du foyer
        guests.update(is_attending=party.is_attending)

        return HttpResponseRedirect(reverse('rsvp-confirm', args=[invite_id]))

    return render(request, 'guests/invitation.html', {
        'party': party,
        'guests': guests,
        'couple_name': settings.BRIDE_AND_GROOM,
        'website_url': settings.WEDDING_WEBSITE_URL,
    })





InviteResponse = namedtuple('InviteResponse', ['guest_pk', 'is_attending'])


def _parse_invite_params(params):
    responses = {}
    for param, value in params.items():
        if param.startswith('attending'):
            pk = int(param.split('-')[-1])
            response = responses.get(pk, {})
            response['attending'] = True if value == 'yes' else False
            responses[pk] = response

    for pk, response in responses.items():
        yield InviteResponse(pk, response['attending'])


def rsvp_confirm(request, invite_id=None):
    party = guess_party_by_invite_id_or_404(invite_id)
    return render(request, template_name='guests/rsvp_confirmation.html', context={
        'party': party,
        'support_email': settings.DEFAULT_WEDDING_REPLY_EMAIL,
        'couple_name' : settings.BRIDE_AND_GROOM,
        'website_url': settings.WEDDING_WEBSITE_URL,                
    })


@login_required
def invitation_email_preview(request, invite_id):
    party = guess_party_by_invite_id_or_404(invite_id)
    context = get_invitation_context(party)
    return render(request, INVITATION_TEMPLATE, context=context)


@login_required
def invitation_email_test(request, invite_id):
    party = guess_party_by_invite_id_or_404(invite_id)
    send_invitation_email(party, recipients=[settings.DEFAULT_WEDDING_TEST_EMAIL])
    return HttpResponse('sent!')


def save_the_date_random(request):
    template_id = random.choice(SAVE_THE_DATE_CONTEXT_MAP.keys())
    return save_the_date_preview(request, template_id)


def save_the_date_preview(request, template_id):
    context = get_save_the_date_context(template_id)
    context['email_mode'] = False
    return render(request, SAVE_THE_DATE_TEMPLATE, context=context)


@login_required
def test_email(request, template_id):
    context = get_save_the_date_context(template_id)
    send_save_the_date_email(context, [settings.DEFAULT_WEDDING_TEST_EMAIL])
    return HttpResponse('sent!')


def _base64_encode(filepath):
    with open(filepath, "rb") as image_file:
        return base64.b64encode(image_file.read())
