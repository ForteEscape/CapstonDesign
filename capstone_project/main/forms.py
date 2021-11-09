from django import forms

class Company(forms.Form):
    duration_set = (
        (7, '1주일'),
        (30, '1개월'),
        (90, '3개월'),
    )

    duration_option = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control'}), choices=duration_set)
    company_name_text = forms.CharField(widget=forms.TextInput, max_length=20)