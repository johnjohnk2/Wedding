import csv
from django.core.management.base import BaseCommand
from guests.models import Party, Guest


class Command(BaseCommand):
    help = "Import guests from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_path",
            type=str,
            help="Path to the CSV file to import (semicolon-separated)."
        )

    def handle(self, *args, **options):
        csv_path = options["csv_path"]

        self.stdout.write(self.style.WARNING(f"Importing from {csv_path}..."))

        with open(csv_path, encoding="ISO-8859-1") as f:
            reader = csv.DictReader(f, delimiter=";")

            for row in reader:
                first = row["first_name"].strip()
                last = row["last_name"].strip()
                party_name = row["party"].strip()
                is_child = row["is_child"].strip().lower() == "yes"

                # ---- Party : normalisation + lookup case-insensitive ----
                party = None
                if party_name:
                    normalized = (
                        party_name.strip()
                        .replace("\xa0", " ")   # Excel et ses espaces chelous
                    )

                    # Essayer de retrouver une Party existante (ignore case)
                    party = Party.objects.filter(name__iexact=normalized).first()

                    if not party:
                        party = Party.objects.create(name=normalized)

                # ---- Guest : update_or_create pour éviter les doublons ----
                guest, created = Guest.objects.update_or_create(
                    first_name=first,
                    last_name=last,
                    party=party,
                    defaults={
                        "is_child": is_child,
                    },
                )

                if created:
                    msg = f"+ Created {first} {last}"
                else:
                    msg = f"~ Updated {first} {last}"
                self.stdout.write(self.style.SUCCESS(msg))

        self.stdout.write(self.style.SUCCESS("Import terminé !"))
