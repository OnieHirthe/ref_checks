from landing.models import *
from django import forms


class ContactForm(forms.ModelForm):
    
    data_check = forms.BooleanField(required=True, error_messages={'required': 'Обязательное поле'} )

    class Meta:
        model = Subscriber
        fields = ['email', 'comment']

        labels = {
            'email' : "E-mail",
            'comment' : "Ваш комментарий"
        }

        widgets = {
            'email' : forms.TextInput(attrs={'placeholder' : 'space@gmail.com'}),
            'comment' : forms.Textarea(attrs={'placeholder' : 'Текстовое сообщение'})
        }

        error_messages={
            'email' : {
                'invalid' : 'Некорректный email',
                'required' : 'Обязательное поле'
            }
        }

    def __init__(self, *args, **kwargs):
        
        super(ContactForm, self).__init__(*args, **kwargs)
        
        if not self.data:
            self.fields['email'].required = False
            self.fields['data_check'].required = False

        self.fields['data_check'].widget.attrs['onchange'] = "enableButton(this, 'submit-button', 'inactive');deleteElement('field-data-check-error');"
        self.fields['email'].widget.attrs['onchange'] = f"removeClass('id_email', 'red-border');deleteElement('field-email-error');"

