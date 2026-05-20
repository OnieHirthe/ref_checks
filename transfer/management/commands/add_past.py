from django.core.management.base import BaseCommand
from users.models import *
from django.db.models.functions import Lower

# trasfer app`s models are generated based on data from the DIFFERENT DATABASE
from transfer.models import PastAbstracts, PastUsers

# it was decided to move only past reports (no participations without reports), made in the years 2022-2025 (D Kobets)
# i decided not to make any new models for past years for smoother transitions between the years: the goal is - no extra actions at the start and the end of the conference, except flag management in settings and manual (?) template changes

"""
The transfer itself is a one-time procedure: in case of the roll-back newly created instances (UserAuth, Profile) will have
    added_in_transfer=True
set. For Participation and Report models the field is just  the year = everything before 2026

"""


def create_user_inst(past_user):
    user = UserAuth(
            email=past_user.mail,
            created=past_user.date_created,
            modified=past_user.date_changed,
            is_confirmed=True,
            added_in_transfer=True,
            password=past_user.pass_field
            )
    
    user.save()
    return user


def create_profile_inst(past_user, user, ct_dict):
    
    profile = Profile(
        user=user,
        first_name_ru=past_user.first_name,
        last_name_ru=past_user.last_name,
        middle_name_ru=past_user.middle_name,
        position_ru=past_user.dolzhnost,
        org_ru=past_user.organization,
        org_short_ru=past_user.organization_short,
        citizenship=ct_dict[past_user.citizenship] if past_user.citizenship is not None else None,
        added_in_transfer=True
        )

    profile.save()
    return profile

def create_part_inst(profile, year):
    part = Participation(
        profile=profile,
        year=year,
        online=False,
    )

    part.save()
    return part

def create_report_inst(past_abstract, profile, sec_dict):

    # skipping authors and advisor name and organization fields FOR MANUAL INPUT
    report = Report(
        year=past_abstract.year,
        profile=profile,
        title=past_abstract.title,
        abstract=past_abstract.text,
        lang='ru',
        plenary=past_abstract.plenary,
        section=sec_dict[past_abstract.section_id],
        status='accepted',
        created=past_abstract.date_created,
        modified=past_abstract.date_changed,
        transfer_uuid=past_abstract.uuid,
    )

    if past_abstract.scientific_director is None:
        report.has_advisor=False

    report.save()
    return report


class Command(BaseCommand):

    def handle(self, *args, **options):
        # using non-default db
        past_inst = PastUsers.objects.using("kmu_transfer").annotate(lower_mail=Lower("mail")).distinct("lower_mail").order_by("lower_mail")
        rep_inst = PastAbstracts.objects.using("kmu_transfer")
        
        ct_dict = {
            "1310" : Citizenship.objects.get(title_ru="Республика Молдова"),
            "140" : Citizenship.objects.get(title_ru="Армения"),
            "1710" : Citizenship.objects.get(title_ru="Российская Федерация"),
            "210" : Citizenship.objects.get(title_ru="Беларусь"),
            "2150" : Citizenship.objects.get(title_ru="Узбекистан"),
            "40": Citizenship.objects.get(title_ru="Азербайджан"),
            "420": Citizenship.objects.get(title_ru="Вьетнам"),
            "720" : Citizenship.objects.get(title_ru="Индия"),
            "760" : Citizenship.objects.get(title_ru="Исламская Республика Иран"),
            "830" : Citizenship.objects.get(title_ru="Казахстан"),
            "900" : Citizenship.objects.get(title_ru="Киргизия"),
            "920" : Citizenship.objects.get(title_ru="Китайская Народная Республика"),
            "940" : Citizenship.objects.get(title_ru="Колумбия")
        }

        sec_dict = {
            "10" : Section.objects.get(name_ru="Физика Солнечной системы"),
            "20" : Section.objects.get(name_ru="Астрофизика и радиоастрономия"),
            "30" : Section.objects.get(name_ru="Дистанционное зондирование Земли"),
            "40" : Section.objects.get(name_ru="Космическое приборостроение и эксперимент"),
            "50" : Section.objects.get(name_ru="Теория и моделирование физических процессов"),
            "60" : Section.objects.get(name_ru="Исследование планет"),
            "70" : Section.objects.get(name_ru="Космос в социальных науках и мировой политике"),
            "80" : Section.objects.get(name_ru="Доклады юниоров (9-11 классы)"),
        }

        for inst in past_inst:
            user = None
            email_match_qs = UserAuth.objects.filter(email__iexact=str(inst.mail).strip().lower())

            # lookup
            if email_match_qs.count() == 1:
                user = email_match_qs.first()
            # no matches case, can not reister with duplicate emails
            else:
                names_match_qs = Profile.objects.filter(
                    last_name_ru__iexact=str(inst.last_name).strip().lower(),
                    first_name_ru__iexact=str(inst.first_name).strip().lower())
            
                if names_match_qs.count() == 1:
                    user = names_match_qs.first().user
                
                # in case of multiple matches, create new user
            
            # user creation       
            if user is None:
                user = create_user_inst(inst)

            # profile creation
            if not hasattr(user, "profile") or user.profile is None:
                profile = create_profile_inst(inst, user, ct_dict)
            else:
                profile = Profile.objects.get(id=user.profile.id)

            # some emails could be left out during lower distinct - need to regain other profiles` uid
            all_uids = list(PastUsers.objects.using("kmu_transfer").annotate(lower_mail=Lower("mail")).filter(lower_mail=inst.mail).values_list('uid', flat=True))
            # reports lookup
            past_reps = rep_inst.filter(uid__in=all_uids)
            
            # reports count
            if past_reps.count() > 0:

                # create participations, separate in case of multiple reports per year
                for past_rep in past_reps.distinct("year"):
                    create_part_inst(profile,  past_rep.year)

                for past_rep in past_reps: 
                    create_report_inst(past_rep, profile, sec_dict)

                if user.added_in_transfer:
                    print(f"{inst.mail} user {user.profile} added,", end="")
                else:
                    print(f"{inst.mail} user {user.profile} found,", end="")

                print(f" reports: {past_reps.values('year')}")
            

