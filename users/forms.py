from django import forms
from users.models import *
from users.widgets import *
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils.translation import get_language
from django.db.models import Q


class UserAuthRegistrationForm(forms.Form):

    email = forms.EmailField(label="E-mail", error_messages={'invalid': _('E-mail не соответсвует стандартному формату'), 'required' : _("Необходимо заполнить это поле") }, widget=forms.TextInput())
    password = forms.CharField(label= _("Пароль"), error_messages={'required' : _("Необходимо заполнить это поле")}, widget=forms.PasswordInput())
    password_confirm = forms.CharField(label= _("Подтвердите пароль"), error_messages={'required' : _("Необходимо заполнить это поле")}, widget=forms.PasswordInput())
    consent_confirm = forms.BooleanField(label="", error_messages={'required' : _("Необходимо заполнить это поле")})

    def __init__(self, *args, **kwargs):

        super(UserAuthRegistrationForm, self).__init__(*args, **kwargs) 
        if not self.data:
            self.fields['email'].required = False
            self.fields['password'].required = False
            self.fields['password_confirm'].required = False
            self.fields['consent_confirm'].required = False

    def clean_email(self):
        email = self.cleaned_data['email']

        # if user with this email exists and IS_COFIRMED - throw error
        potential_user = UserAuth.objects.filter(email__iexact=email.lower())
        if potential_user.count() == 1:
            if potential_user.first().is_confirmed:
                raise ValidationError(_("Профиль с этим почтовым адресом уже зарегистрирован"))

        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password != password_confirm:
            raise ValidationError(_("Пароли не совпадают"))

        return cleaned_data

class UserAuthLoginForm(forms.Form):

    email = forms.EmailField(label="E-mail", error_messages={'invalid': _('E-mail не соответсвует стандартному формату'), 'required' : _("Необходимо заполнить это поле") }, widget=forms.TextInput(attrs={'placeholder' : 'space@gmail.com'}))
    password = forms.CharField(label= _("Пароль"), error_messages={'required' : _("Необходимо заполнить это поле")}, widget=forms.PasswordInput())

    user_cache = None
    

    def __init__(self, *args, **kwargs):

        super(UserAuthLoginForm, self).__init__(*args, **kwargs) 
        
        if not self.data:
            self.fields['email'].required = False
            self.fields['password'].required = False

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        email = cleaned_data.get("email")

        if email and password:
            try:
                user_instance = UserAuth.objects.get(email__iexact=email.lower())
                confirmed_user = authenticate(id=user_instance.id, password=password)
                if confirmed_user is None:
                    raise ValidationError(_('Неправильно введен email или пароль.'))
            except UserAuth.DoesNotExist:
                raise ValidationError(_('Неправильно введен email или пароль.'))

            if not confirmed_user.is_confirmed:
                raise ValidationError(_('Пожалуйста, подтвердите email или пройдите Регистрацию на сайте еще раз.'))

            self.user_cache = confirmed_user
            
        return cleaned_data


class PasswordChangeExternalForm(forms.Form):

    email = forms.CharField(label="E-mail", widget=forms.TextInput(attrs={'placeholder' : 'space@gmail.com'}))

    user = None

    def __init__(self, *args, **kwargs):
        super(PasswordChangeExternalForm, self).__init__(*args, **kwargs)
    
        if not self.data:
            self.fields['email'].required = False

    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            user = UserAuth.objects.get(email__iexact=email.lower())
            self.user = user
        except UserAuth.DoesNotExist:
            raise ValidationError(_("Пользователь с таким email адресом не найден. Пройдите Регистрацию на сайте."))
        return email
    

class PasswordChangeCodeForm(forms.Form):

    code = forms.CharField(label=_("Код из письма"), widget=forms.TextInput()) 
    
    auth_id = None
    user = None

    def __init__(self, *args, **kwargs):
        auth_id = kwargs.pop('auth_id', None)
        super(PasswordChangeCodeForm, self).__init__(*args, **kwargs)
        
        self.auth_id = auth_id

    def clean_code(self):
        code = self.cleaned_data["code"]
        try:
            auth_instance = AuthCode.objects.get(id=self.auth_id)
            if not auth_instance.compare_code(code):
                raise ValidationError(_("Неверный код"))
            else:
                self.user = auth_instance.user
                auth_instance.delete()
        except AuthCode.DoesNotExist:
            raise ValidationError(_("Неверный код"))
            
        return code


class PasswordChangeForm(forms.Form):
    
    password = forms.CharField(label= _("Новый пароль"), error_messages={'required' : _("Необходимо заполнить это поле")}, widget=forms.PasswordInput())
    password_confirm = forms.CharField(label= _("Подтвердите пароль"), error_messages={'required' : _("Необходимо заполнить это поле")}, widget=forms.PasswordInput())

    user = None

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(PasswordChangeForm, self).__init__(*args, **kwargs)

        self.user = user

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password == password_confirm:
            self.user.set_password(password)
            self.user.save()
        else:
            raise ValidationError(_("Пароли не совпадают"))

        return cleaned_data

class CitizenshipForm(forms.Form):
    
    citizenship = forms.ChoiceField(widget=InputDropdown())
    
    def __init__(self, *args, **kwargs):
        
        query = kwargs.pop('query', None)
        language = kwargs.pop('language', None)
            
        super(CitizenshipForm, self).__init__(*args, **kwargs)
        
        if query is not None and query != '':
            qs = Citizenship.objects.filter(Q(code__icontains=query) | Q(title_ru__icontains=query) | Q(title_en__icontains=query))
            if language == 'en':
                ordered_qs = qs.order_by('title_en')
                choices = tuple([ (inst.code, inst.title_en) for inst in ordered_qs ])
            else:
                ordered_qs = qs.order_by('title_ru')
                choices = tuple([ (inst.code, inst.title_ru) for inst in ordered_qs ])

            self.fields['citizenship'].choices = choices
            self.fields['citizenship'].widget.attrs['data-query'] = query
            


class ProfileForm(forms.ModelForm):
    
    not_required = ['phone', 'middle_name_ru', 'first_name_ru', 'last_name_ru', 'org_ru', 'org_short_ru', 'org_short_en', 'position_ru']

    email = forms.CharField(label="E-mail", required=False)
    citizenship = forms.ChoiceField(widget=InputDropdown(), choices=Citizenship.objects.choices("en"), error_messages={'required' : _("Необходимо заполнить это поле")})

    class Meta:
        model = Profile
        
        fields = [
            'first_name_en', 'last_name_en', 'first_name_ru', 'last_name_ru', 'middle_name_ru',
            'phone', 'org_ru', 'org_en', 'org_short_ru', 'org_short_en',  'position_ru', 'position_en'
        ]

        labels = {
            'first_name_en': 'First name',
            'last_name_en' : 'Last name',
            'first_name_ru' : 'Имя',
            'last_name_ru' : 'Фамилия',
            'middle_name_ru' : 'Отчество',
            'phone' : _("Номер телефона"),
            'org_ru' : 'Организация',
            'org_en' : 'Organization',
            'org_short_ru' : 'Организация (короткая форма)',
            'org_short_en' : 'Organization (short form)',
            'position_ru' : 'Должность',
            'position_en' : 'Position'
        }
        
        widgets = {
            'position_ru' : forms.TextInput(),
            'position_en' : forms.TextInput()
        }

        error_messages = {
            'first_name_en' : { 'required': _("Необходимо заполнить это поле") },
            'last_name_en' : { 'required': _("Необходимо заполнить это поле") },
            'first_name_ru' : { 'required': _("Необходимо заполнить это поле") },
            'last_name_ru' : { 'required': _("Необходимо заполнить это поле") },
            'email' : { 'required': _("Необходимо заполнить это поле") },
            'org_en' : { 'required': _("Необходимо заполнить это поле") },
            'org_ru' : { 'required': _("Необходимо заполнить это поле") },
            'position_en' : { 'required': _("Необходимо заполнить это поле") },
            'position_ru' : { 'required': _("Необходимо заполнить это поле") },
        }

    def __init__(self, *args, **kwargs):
        
        super(ProfileForm, self).__init__(*args, **kwargs)

        if self.data:
            for fieldname, _ in self.fields.items():
                if fieldname not in self.not_required:
                    self.fields[fieldname].required = True  

    def clean_email(self):
        email = self.cleaned_data["email"]
        if self.instance.exists():
            if email != self.instance.user.email:
                other_users = UserAuth.objects.filter(email__iexact=email.lower())
                if other_users.count() != 0:
                    raise ValidationError(_("Этот E-mail занят"))

        return email

    def clean_citizenship(self):
        citizenship = self.cleaned_data["citizenship"]
        try:
            c_instance = Citizenship.objects.get(code=citizenship)
        except Citizenship.DoesNotExist:
            raise ValidationError("Пожалуйста, выберите страну из списка")
        
        # attached to the instance here, but the instance is not actually SAVED yet, 
        # until save method on the form is called
        self.instance.citizenship = c_instance
        return citizenship
    

class ParticipationForm(forms.ModelForm):

    class Meta:
        model = Participation
        
        fields = ['online']
        labels = {
            'online' : _('Форма участия')
        }
        widgets = {"online" : CustomRadioSelect()}


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class ReportFileForm(forms.Form):

    single_file = forms.FileField(error_messages={'required' : _("Необходимо выбрать файл"), 'empty' : _("Пустой загружаемый файл")})

    def __init__(self, *args, **kwargs):
        super(ReportFileForm, self).__init__(*args, **kwargs)
        if not self.data:
            self.fields['single_file'].required = False
        


class ReportForm(forms.ModelForm):

    authors_field = forms.ModelMultipleChoiceField(queryset=Author.objects.all(), required=False)
    #expertise_file = forms.FileField(required=False, label="Экспертное заключение")

    class Meta:
        model = Report

        fields = ['title', 'abstract', 'lang', 'pub_link', 'section', 'has_advisor', 'advisor']
        labels = {
            'title' : _('Название доклада'),
            'abstract' : _('Аннотация доклада'),
            'lang' : _('Язык доклада'),
            'pub_link': _('Ссылка на публикацию'),
            'section' : _('Секция'),
        }
        #help_texts = {
        #    'lang' : _("Предпочтительный язык выступления - английский"),
        #}
        widgets = {
            "lang" : CustomRadioSelect(),
            "section" : CustomSelect(),
            "pub_link" : forms.TextInput()
        }
        error_messages = {
            'title' : { 'required': _("Необходимо заполнить это поле") },
            'abstract' : { 'required': _("Необходимо заполнить это поле") },
            'lang' : { 'required': _("Необходимо заполнить это поле") },
            'advisor' : { 'required': _("Необходимо заполнить это поле") },
            'section' : { 'required': _("Необходимо заполнить это поле") },
        }

    def __init__(self, *args, **kwargs):
            
        super(ReportForm, self).__init__(*args, **kwargs)

        self.fields['section'].choices = Section.objects.choices(get_language())
        self.fields['has_advisor'].widget.attrs['onchange'] = "changeVisibility('advisor-field-container');"
        
        if not self.data:
            self.fields['title'].required = False
            self.fields['abstract'].required = False
            self.fields['lang'].required = False
            self.fields['section'].required = False
            
            self.fields['advisor'].required = False

        if self.instance.exists():
            self.fields['authors_field'].initial = self.instance.authors.values_list('id', flat=True)      


class AuthorForm(forms.ModelForm):

    class Meta:
        model = Author
        fields = ['first_name', 'last_name', 'middle_name', 'email', 'org']
        labels = {
            'first_name' : _("Имя"),
            'last_name' : _("Фамилия"),
            'middle_name' : _("Отчество"),
            'email' : _("E-mail"),
            'org' : _("Организация")
        }
        widgets = {
            'org' : forms.TextInput(),
            'email' : forms.TextInput()
        }
        error_messages = {
            'first_name' : { 'required': _("Необходимо заполнить это поле") },
            'last_name' : { 'required': _("Необходимо заполнить это поле") },
            'email' : { 'required': _("Необходимо заполнить это поле"),
            'invalid': _("E-mail не соответсвует стандартному формату")},
            'org' : { 'required': _("Необходимо заполнить это поле") },
        }
    


    def __init__(self, *args, **kwargs):
        super(AuthorForm, self).__init__(*args, **kwargs)
    
        if not self.data:
            self.fields['first_name'].required = False
            self.fields['last_name'].required = False
            self.fields['email'].required = False
            self.fields['org'].required = False
            

