from django.forms import *
from django.contrib.auth import authenticate
from apka.models import Obwod, Wynik, Kandydat, Statystyka


class WynikForm(ModelForm):
    kandydat = ModelChoiceField(queryset=Kandydat.objects.all(), required=True)

    class Meta:
        model = Wynik
        fields = ('kandydat', 'liczba',)

    def clean_liczba(self):
        liczba = self.cleaned_data.get('liczba')
        if liczba < 0:
            raise ValidationError('Liczba głosów nie może być ujemna')
        return liczba


class UserLoginForm(Form):
    user = CharField()
    password = CharField(widget=PasswordInput)

    def clean(self):
        username = self.cleaned_data.get('user')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if user is None:
            raise ValidationError('Dane logowania są niepoprawne.')
        return self.cleaned_data

WynikFormSet = formset_factory(WynikForm, extra=0)
