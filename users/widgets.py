from django import forms

class CustomRadioSelect(forms.RadioSelect):
    template_name="widgets/custom_radio.html"
    option_template_name="widgets/custom_radio_option.html"


class CustomSelect(forms.Select):
    template_name="widgets/custom_select.html"
    option_template_name="widgets/custom_select_option.html"

class InputDropdown(forms.Select):
    template_name="widgets/input_dropdown.html" 

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True
