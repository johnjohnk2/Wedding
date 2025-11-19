from __future__ import unicode_literals
import uuid

from django.db import models


def _random_uuid():
    return uuid.uuid4().hex


class Party(models.Model):
    """
    Un foyer (Parents, Mariés, Famille X, etc.)
    """
    name = models.TextField()
    invitation_id = models.CharField(
        max_length=32,
        db_index=True,
        default=_random_uuid,
        unique=True,
    )

    # commentaire libre des invités (facultatif)
    comments = models.TextField(null=True, blank=True)

    # nos deux compteurs
    nb_mairie = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Nombre de personnes à la mairie",
    )
    nb_soiree = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Nombre de personnes à la soirée",
    )

    # optionnel, mais pratique : savoir si au moins une personne vient
    is_attending = models.BooleanField(default=None, null=True)

    def __str__(self):
        return f"Party: {self.name}"

    @property
    def any_guests_attending(self):
        """
        True si au moins un Guest du foyer est marqué comme venant.
        Utilisé par la vue si tu veux.
        """
        return self.guest_set.filter(is_attending=True).exists()


class Guest(models.Model):
    """
    Une personne individuelle
    """
    party = models.ForeignKey(Party, on_delete=models.CASCADE)

    first_name = models.TextField()
    last_name = models.TextField(null=True, blank=True)
    is_attending = models.BooleanField(default=None, null=True)
    is_child = models.BooleanField(default=False)
    comments = models.TextField(blank=True, null=True)


    @property
    def name(self):
        return u"{} {}".format(self.first_name, self.last_name or "").strip()

    @property
    def unique_id(self):
        # utilisé dans les templates d'origine
        return str(self.pk)

    def __str__(self):
        return f"Guest: {self.first_name} {self.last_name or ''}".strip()
