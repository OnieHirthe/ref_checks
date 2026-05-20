from django.core.management.base import BaseCommand
import csv
from landing.models import Subscriber
import datetime as dt

class Command(BaseCommand):

    def handle(self, *args, **options):
        
        users_csv_file = "/home/annas/kmu_files/kmu_transfer_users"

        labels = ['uid', 'uuid', 'username', 'mail', 'pass', 'first_name', 'middle_name', 'last_name',
        'dolzhnost', 'organization', 'organization_short', 'citizenship', 'forma0', 'forma1', 'consent',
        'date_created', 'date_changed']
        
        emails = []

        with open(users_csv_file, "r") as f:
            csv_reader = csv.DictReader(f, fieldnames=labels)
           
            

            for index, row in enumerate(csv_reader):
                if "@" in row['mail']:
                    emails.append(row['mail'].lower())
                else:
                    print("invalid email:", row['mail'])
               # print(row['mail'], row['first_name'], row['last_name'])

        subs = list(Subscriber.objects.values_list('email', flat=True))
        
        print(len(emails))
        print(len(subs))

        print(len(set(subs) & set(emails)))

        emails.sort()

        sieve_file_name = "info_list_2024_2025" 
        sieve_file = f"/home/annas/kmu_files/{sieve_file_name}"


        with open(sieve_file, "w") as f:
            f.write("{")
            for email in emails:
                f.write(f"\tredirect :copy \"{email}\";\n")
            f.write("}")


