from django.core.management.base import BaseCommand
from .citizenships import citizenships
from users.models import Citizenship

class Command(BaseCommand):

    def handle(self, *args, **options):
        
        c_instances = []

        for code, _, title_ru, title_en in citizenships:
            c_instances.append(
                Citizenship(
                    code=code,
                    title_ru=title_ru,
                    title_en=title_en
                ))
        
        Citizenship.objects.bulk_create(c_instances)

