from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import Group
from kmu.utils import year
from django.utils.timezone import now as NOW
import uuid
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class UserAuthManager(BaseUserManager):

    def create_user(self, email, password=None):
        user = self.model(
            email = self.normalize_email(email),
            created = NOW(),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def bl_choices(self):
        options = [(user.email, f"{user.profile.short_rus_name()} ({user.profile.short_en_name()}) - {user.profile.org_ru}") for user in self.filter(profile__isnull=False)]
        return tuple(options)
        

class UserAuth(AbstractBaseUser):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    email = models.EmailField(max_length=300, unique=True)
    created = models.DateTimeField(default=NOW)
    modified = models.DateTimeField(auto_now=True, blank=True, null=True)
    is_confirmed = models.BooleanField(default=False)

    groups = models.ManyToManyField(Group, related_name="users")
    objects = UserAuthManager()

    added_in_transfer = models.BooleanField(default=False)

    USERNAME_FIELD = 'id'

    def __str__(self):
        return self.email

    def has_profile(self):
        return hasattr(self, 'profile') and self.profile is not None

    def profile_name_ru(self):
        if self.has_profile():
            return f"{self.profile.first_name_ru} {self.profile.last_name_ru}"
        else:
            return "Ваше Имя"

    def profile_name_en(self):
        if self.has_profile():
            return f"{self.profile.first_name_en} {self.profile.last_name_en}"
        else:
            return "Your Name"

    def is_org(self):
        return self.groups.filter(name="org").exists()

    def is_admin(self):
        return self.groups.filter(name="admin").exists()

    def is_mod(self):
        return self.groups.filter(name="mod").exists()

    def graylisted(self):
        if hasattr(self, "in_bl"):
            return self.in_bl.level == "gray"
        return False
    
    def blacklisted(self):
        if hasattr(self, "in_bl"):
            return self.in_bl.level == "black"
        return False
    
    def unlisted(self):
        return not self.graylisted() and not self.blacklisted()



class AuthBase(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(default=NOW)

    class Meta:
        abstract = True

class AuthLink(AuthBase):
    user = models.ForeignKey("UserAuth", on_delete=models.CASCADE, related_name="auth_links")

class AuthCode(AuthBase):
    user = models.ForeignKey("UserAuth", on_delete=models.CASCADE, related_name="auth_codes")
    code_source = models.UUIDField(default=uuid.uuid4, editable=False)

    def issue_code(self):
        return str(self.code_source)[2:8]

    def compare_code(self, sample):
        print("was in compare")
        print(sample, self.code_source)
        return self.issue_code() == sample 

class SafeGetManager(models.Manager):

    def safe_get(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None


class Profile(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.OneToOneField("UserAuth", on_delete=models.CASCADE, related_name="profile")
    
    first_name_ru = models.CharField(max_length=300, blank=True, null=True)
    last_name_ru = models.CharField(max_length=300, blank=True, null=True)
    middle_name_ru = models.CharField(max_length=300, blank=True, null=True)
    last_name_en = models.CharField(max_length=300, blank=True, null=True)
    first_name_en = models.CharField(max_length=300, blank=True, null=True)

    citizenship = models.ForeignKey("Citizenship", on_delete=models.SET_NULL, related_name="citizens", blank=True, null=True)

    phone = models.CharField(max_length=50, blank=True, null=True)
    
    org_ru = models.TextField(blank=True, null=True)
    org_en = models.TextField(blank=True, null=True)
    org_short_ru = models.CharField(max_length=20, blank=True, null=True)
    org_short_en = models.CharField(max_length=20, blank=True, null=True)

    position_ru = models.TextField(blank=True, null=True)
    position_en = models.TextField(blank=True, null=True)
    
    added_in_transfer = models.BooleanField(default=False)

    required_fields = ['last_name_en', 'first_name_en', 'citizenship', 'org_en', 'position_en']
    
    objects = SafeGetManager()

    def exists(self):
        return Profile.objects.safe_get(id=self.id) is not None

    def __str__(self):
        return f"{self.user.email}_{self.last_name_ru}_{self.first_name_ru}"

    # True if all required fields are filled-in
    def all_required_filled(self):
        for field in self.required_fields:
            if getattr(self, field) is None:
                print(f"{field} is none")
                return False

        return True

    def is_registered(self):
        try:
            self.participations.get(year=year())
            return True
        except:
            return False

    def not_rus_citizen(self):
        return self.citizenship and self.citizenship.code != "RU"

    def get_participation(self):
        if not self.is_registered():
            return None
        else:
            return self.participations.get(year=year())
    

    def get_participation_year(self, given_year):
        try:
            return self.participations.get(year=given_year)
        except:
            return None


    def any_reports_this_year(self):
        return self.reports.filter(year=year()).count() > 0

    def full_rus_name(self):
        name = ""
        if self.last_name_ru:
            name += self.last_name_ru
        if self.first_name_ru:
            name += " " + self.first_name_ru
        if self.middle_name_ru:
            name += " " + self.middle_name_ru
        return name
    
    def short_rus_name(self):
        name = ""
        if self.last_name_ru:
            name += self.last_name_ru
        if self.first_name_ru:
            name += f" {self.first_name_ru[0]}."
        if self.middle_name_ru:
            name += f" { self.middle_name_ru[0]}."
        return name
        
    def full_en_name(self):
        return f"{self.last_name_en} {self.first_name_en}"

    def short_en_name(self):
        if self.first_name_en:
            return f"{self.last_name_en} {self.first_name_en[0]}."
        else:
            return self.last_name_en
    
    def archived_reports(self):
        
        if settings.CONF_FLAGS['CONFERENCE']:
            arch_reports = self.reports.filter(year__lt=year())
            print("ARCHIVED OUTPUT", arch_reports.count())
        else:
            arch_reports = self.reports.all()
        return arch_reports.order_by('-year')


class Participation(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    profile = models.ForeignKey("Profile", on_delete=models.CASCADE, related_name="participations")
    year = models.PositiveSmallIntegerField(default=year)
    online = models.BooleanField(default=False, choices=((False, _("Очная")), (True, _("Онлайн"))))

    created = models.DateTimeField(default=NOW)

    objects = SafeGetManager()

    def __str__(self):
        return f"{self.year}_{self.profile}"
    
    def exists(self):
        return Participation.objects.safe_get(id=self.id) is not None


class Report(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="reports")
    year = models.PositiveSmallIntegerField(default=year)
    
    title = models.TextField()
    abstract = models.TextField()
    
    lang = models.CharField(max_length=3, default="en", choices=(('en', _("Английский")), ('ru', _("Русский"))) )

    pub_link = models.TextField(blank=True, null=True)

    has_advisor = models.BooleanField(default=True)
    advisor = models.ForeignKey("Author", on_delete=models.SET_NULL, related_name="advised", blank=True, null=True)

    plenary = models.BooleanField(default=False, choices=((True, "да"), (False, "нет")))

    section = models.ForeignKey("Section", on_delete=models.SET_NULL, related_name="reports", blank=True, null=True)
    subsection = models.ForeignKey("Subsection", on_delete=models.SET_NULL, related_name="reports", blank=True, null=True)
    status = models.CharField(max_length=20, default="in review", choices=(('in review', _("В рассмотрении")), ('accepted', _("Принят")), ('declined', _("Отклонен")) ))

    objects = SafeGetManager()

    created = models.DateTimeField(default=NOW)
    modified = models.DateTimeField(default=NOW)
   
    # for manual matching with PastAbstracts uuid field
    transfer_uuid = models.UUIDField(default=None, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        self.modified = NOW()
        super(Report, self).save(*args, **kwargs)

    def get_lang(self):
        if self.lang == 'ru':
            return _("Русский")
        else:
            return _("Английский")

    def exists(self):
        return Report.objects.safe_get(id=self.id) is not None

    def set_authors(self, author_ids):
        print("advisor", self.advisor)
        current_authors = Author.objects.filter(report=self, advisor=False)
        print("current authors", current_authors)
        current_authors.update(report=None)
        
        print("should be authors", author_ids)
        should_be_authors = Author.objects.filter(id__in=author_ids)
        should_be_authors.update(report=self)

    def authors_only(self):
        return self.authors.filter(advisor=False)

    def full_authors(self):
        print(self.advisor)
        if self.lang == "en":
            authors_str = f"{self.profile.short_en_name()}" 
        else:
            authors_str = f"{self.profile.short_rus_name()}" 

        if self.advisor and self.has_advisor:
            authors_str += f", {self.advisor.short_name()}"
        
        coauthors = list(self.authors_only())
        if len(coauthors) > 0:
            authors_str += ", "
            for author in coauthors:
                authors_str += f"{author.short_name()}"
                if author != coauthors[-1]:
                    authors_str += ", "
    
        return authors_str
    
    def has_expertise(self):
        return self.expertise_files.count() > 0
        

    def get_expertise(self):
        return self.expertise_files.first()

    def has_presentation(self):
        return self.presentation_files.count() > 0
        

    def get_presentation(self):
        return self.presentation_files.first()

    def ordered_comments(self):
        return self.comments.order_by("created")



class BaseFile(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file_obj = models.FileField(storage=settings.FS)
    filename = models.CharField(max_length=1000)
    added = models.DateTimeField(default=NOW)

    class Meta:
        abstract = True
    
    def delete_file(self):
        print("actual file deletion intiated")
        path = f"{settings.FS.location}/{self.file_obj.name}"
        settings.FS.delete(path)


class PresentationFile(BaseFile):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="presentation_files")
    model_name = "presentation"


class ExpertiseFile(BaseFile):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="expertise_files")
    model_name = "expertise"


class Author(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    first_name = models.CharField(max_length=300)
    last_name = models.CharField(max_length=300)
    middle_name = models.CharField(max_length=300, blank=True, null=True)

    email = models.EmailField(max_length=300)
    org = models.TextField()
   
    advisor = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(blank=True, null=True)
    report = models.ForeignKey("Report", on_delete=models.CASCADE, related_name="authors", blank=True, null=True)

    objects = SafeGetManager()

    def exists(self):
        return Author.objects.safe_get(id=self.id) is not None

    def full_name(self):
        if self.middle_name:
            return f"{self.last_name} {self.first_name} {self.middle_name}"
        else:
            return f"{self.last_name} {self.first_name}"
        
    def short_name(self):
        if self.middle_name:
            return f"{self.last_name} {self.first_name[0]}. {self.middle_name[0]}."
        else:
            return f"{self.last_name} {self.first_name[0]}."



class SectionManager(models.Manager):

    def choices(self, lang_code):
        if lang_code == "ru":
            options = [(section.id, section.name_ru) for section in self.exclude(name_ru="Пленарные доклады")]
        else:
            options = [(section.id, section.name_en) for section in self.exclude(name_ru="Пленарные доклады")]
        return tuple(options)

    def choices_with_empty(self):
        options = [(section.id, section.name_ru) for section in self.exclude(name_ru="Пленарные доклады")]
        options.append((None, "--Выбрать секцию--"))
        return tuple(options)

    

class Section(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name_ru = models.CharField(max_length=300)
    name_en = models.CharField(max_length=300)
   
    conference_link = models.TextField(blank=True, null=True)

    objects = SectionManager()

    def __str__(self):
        return self.name_en

    def ordered_subsections(self):
        return self.subsections.order_by("name_ru")

    def subsection_choices(self):
        return ([(subsection.id, subsection.name_ru) for subsection in self.ordered_subsections()])
    
    def subsection_choices_with_empty(self):
        return ([(subsection.id, subsection.name_ru) for subsection in self.ordered_subsections()] + [(None, "--Выбрать подсекцию--")])


class Subsection(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name_ru = models.CharField(max_length=300)
    name_en = models.CharField(max_length=300)

    section = models.ForeignKey("Section", on_delete=models.CASCADE, related_name="subsections")



class CitizenshipManager(models.Manager):

    def choices(self, lang_code):
        if lang_code == "ru":
            options = [(option.code, option.title_ru) for option in self.all()]
        else:
            options = [(option.code, option.title_en) for option in self.all()]
        return tuple(options)

class Citizenship(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    code = models.CharField(max_length=3, default="en")

    title_ru = models.CharField(max_length=100)
    title_en = models.CharField(max_length=100)

    objects = CitizenshipManager()

    def __str__(self):
        return self.title_en

