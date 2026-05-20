from django import forms
from users.models import *
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db.models import Q
from admin_interfaces.models import *
from users.forms import ReportForm
from users.widgets import InputDropdown



class SubsectionForm(forms.ModelForm):
    
    class Meta:
        model = Subsection
        fields = ["name_ru", "name_en", "section"]
        labels = {
            'name_ru' : "Название на русском",
            'name_en' : "Название на английском"
        }

        error_messages = {
            'name_ru' : { 'required': "Необходимо заполнить это поле" },
            'name_en' : { 'required': "Необходимо заполнить это поле" },
        }

    def __init__(self, *args, **kwargs):

        section = kwargs.pop("section", None)

        super(SubsectionForm, self).__init__(*args, **kwargs)
        
        self.fields['section'].initial = section.id

        if not self.data:
            self.fields['name_ru'].required = False
            self.fields['name_en'].required = False


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ["content", "profile", "report"]
        labels = {
            "content" : "Текст комментария"
        }
        error_messages = {
            'content' : { 'required': "Необходимо заполнить это поле" },
        }

    def __init__(self, *args, **kwargs):
        
        report = kwargs.pop("report", None)
        profile = kwargs.pop("profile", None)
        
        super(CommentForm, self).__init__(*args, **kwargs)

        self.fields['report'].initial = report.id
        self.fields['profile'].initial = profile.id


class FilterForm(forms.Form):

    status = forms.ChoiceField(widget=forms.Select(attrs={"onchange" : "setFilter(this);"}), choices=(Report.status.field.choices + [(None, "--Выбрать статус--")]))
    section_id = forms.ChoiceField(widget=forms.Select(attrs={"onchange" : "setFilter(this);"}), choices=Section.objects.choices_with_empty())
    online = forms.ChoiceField(widget=forms.Select(attrs={"onchange" : "setFilter(this);"}), choices=(("True", "онлайн"), ("False", "очно"), (None, "--Выбрать форму участия--")))
    citizenship = forms.ChoiceField(widget=forms.Select(attrs={"onchange" : "setFilter(this);"}), choices=(("russian", "граждане РФ"), ("other", "иностранные граждане"), (None, "--Выбрать гражданство--")))
    reports = forms.ChoiceField(widget=forms.Select(attrs={"onchange" : "setFilter(this);"}), choices=(("no", "без докладов"), ("yes", "с докладом"), (None, "--Выбрать доклады--")))
    



class SectionAttachForm(forms.Form):
    section_id = forms.ChoiceField(choices=Section.objects.choices('ru'), label="")


class SubsectionAttachForm(forms.Form):
    subsection_id = forms.ChoiceField(choices=(), label="")

    def __init__(self, *args, **kwargs):
        section = kwargs.pop("section", None)
        
        super(SubsectionAttachForm, self).__init__(*args, **kwargs)
        
        subsection_choices = section.subsection_choices_with_empty()
        self.fields['subsection_id'].choices = subsection_choices
        self.fields['subsection_id'].widget.choices = subsection_choices


class ReportTitleForm(forms.ModelForm):
    
    class Meta:
        model = Report
        fields = ["title"]
        labels = { "title" : ""}


class ReportAbstractForm(forms.ModelForm):

    class Meta:
        model = Report
        fields = ["abstract"]
        labels = { "abstract" : ""}



class ReportPlenaryForm(forms.ModelForm):
    
    class Meta:
        model = Report
        fields = ["plenary"]
        labels = { "plenary" : ""}
    

class ReportLanguageForm(forms.ModelForm):
    
    class Meta:
        model = Report
        fields = ["lang"]
        labels = { "lang" : ""}


class ReportPublinkForm(forms.ModelForm):

    class Meta:
        model = Report
        fields = ["pub_link"]
        labels = { "pub_link" : ""}


FIELDFORM = {
    "title" : ReportTitleForm,
    "abstract" : ReportAbstractForm,
    "plenary" : ReportPlenaryForm,
    "lang" : ReportLanguageForm,
    "pub_link" : ReportPublinkForm,
}


class ReportHasAdvisorForm(forms.ModelForm):

    class Meta:
        model = Report
        fields = ["has_advisor"]
        labels = {"has_advisor" : ""}
        widgets = {"has_advisor" : forms.CheckboxInput(attrs={"onchange" : "changeVisibility('advisor-target');"})}


class ReportAuthorsForm(forms.Form):
    
    authors_field = forms.ModelMultipleChoiceField(queryset=Author.objects.all(), required=False)
   
    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance', None)
        print(instance)
        super(ReportAuthorsForm, self).__init__(*args, **kwargs)

        if instance.exists():
            print("instance exists")
            self.fields['authors_field'].initial = instance.authors.values_list('id', flat=True)


class BlackListedUserForm(forms.Form):
    
    user = forms.ChoiceField(widget=InputDropdown())

    def __init__(self, *args, **kwargs):

        query = kwargs.pop('query', None)

        super(BlackListedUserForm, self).__init__(*args, **kwargs)
        
        if query is not None and query != '':
            qs = UserAuth.objects.filter(Q(email__icontains=query) | Q(profile__last_name_en__icontains=query) | Q(profile__last_name_ru__icontains=query) | Q(profile__org_ru__icontains=query) | Q(profile__org_en__icontains=query))
            choices = tuple([ (inst.email, f"{inst.profile.short_rus_name()} ({inst.profile.short_en_name()}) - {inst.profile.org_ru}") for inst in qs ] )
            print(qs)
            print(choices)
            self.fields['user'].choices = choices
            self.fields['user'].widget.attrs['data-query'] = query



class BlackListedForm(forms.ModelForm):

    user = forms.ChoiceField(widget=InputDropdown(), choices=UserAuth.objects.bl_choices(), label="Пользователь", required=False)
    class Meta:
        model = BlackListedEntry
        fields = ["level", "comment"]
        labels = {
            "level" : "Куда добавляется запись",
            "comment" : "Кто или почему добавляется"
        }

    def clean_user(self):
        user_email = self.cleaned_data["user"]
        print(f"in validate user email value \"{user_email}\"")
        if user_email != '':
            try:
                user_instance = UserAuth.objects.get(email=user_email)
            except Exception as e:
                print(e)
                raise ValidationError("Пожалуйста, выберите пользователя из списка")
            
            if hasattr(user_instance, "in_bl") and self.instance.id != user_instance.in_bl.id:
                raise ValidationError(f"Этот пользователь уже есть в {'сером' if user_instance.in_bl.level == 'gray' else 'черном'} списке")

            self.instance.user = user_instance
        else:
            self.instance.user = None
        return user_email

    def __init__(self, *args, **kwargs):
        
        super(BlackListedForm, self).__init__(*args, **kwargs)

        if hasattr(self.instance, 'user') and self.instance.user is not None:
            self.fields['user'].initial = self.instance.user.email
            print("setting email")

        if not self.data:
            self.fields['comment'].required = False

class BroadcastSectionForm(forms.ModelForm):

    class Meta:
        model = Section
        fields = ["conference_link"]

    def __init__(self, *args, **kwargs):
        

        super(BroadcastSectionForm, self).__init__(*args, **kwargs)
        
        self.fields['conference_link'].widget = forms.TextInput(attrs={"id" : f"id_conference_link_{ self.instance.id }"})

