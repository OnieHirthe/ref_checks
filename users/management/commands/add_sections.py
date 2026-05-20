from django.core.management.base import BaseCommand
from .sections import sections
from users.models import Section

class Command(BaseCommand):

    def handle(self, *args, **options):
        
        s_instances = []

        for title_ru, title_en in sections:
            s_instances.append(
                Section(
                    name_ru=title_ru,
                    name_en=title_en
                ))
        
        Section.objects.bulk_create(s_instances)

