from django.contrib import admin
from django.db.models import Sum

from apka.models import *
from apka.forms import ValidationError
from django.forms.models import BaseInlineFormSet


class WynikInLineFormSet(BaseInlineFormSet):

    def clean(self):
        def clean_liczba(data):
            liczba = data['liczba']
            if liczba < 0:
                raise ValidationError('Liczba nie może być ujemna')
            return liczba

        super(WynikInLineFormSet, self).clean()

        obwod = self.forms[0].cleaned_data['obwod']
        Wynik.objects.select_for_update().filter(obwod=obwod)

        suma = 0
        for form in self.forms:
            print(form.cleaned_data)
            suma += clean_liczba(form.cleaned_data)
        staty = Statystyka.objects.select_for_update().filter(obwod=obwod)
        niewazne = staty.get(etykieta='Głosy nieważne').liczba
        karty = staty.get(etykieta='Wydane karty').liczba
        if niewazne + suma > karty:
            raise ValidationError(
                'Suma głosów kandydatów i głosów nieważnych ({}) jest większa niż'
                ' liczba wydanych kart ({})'.format(niewazne + suma, karty))

    def save(self, commit=True):
        staty = Statystyka.objects.filter(obwod=self.instance)
        suma = 0
        for i in self.cleaned_data:
            suma += i['liczba']
        staty.get(etykieta='Głosy ważne').liczba = suma
        staty.get(etykieta='Głosy oddane').liczba = suma + staty.get(etykieta='Głosy nieważne').liczba
        staty.update()
        return super(WynikInLineFormSet, self).save()


class WynikInline(admin.TabularInline):
    model = Wynik
    formset = WynikInLineFormSet
    fields = ['kandydat', 'liczba']
    extra = 0
    readonly_fields = ['kandydat']
    verbose_name_plural = 'Wyniki'
    can_delete = False


class StatystykiInlineFormSet(BaseInlineFormSet):

    def clean(self):
        super(StatystykiInlineFormSet, self).clean()
        data = {}
        obwod = self.cleaned_data[0]['obwod']
        Statystyka.objects.select_for_update().filter(obwod=obwod)

        for i in self.cleaned_data:
            if i['id'].etykieta == 'Uprawnieni':
                data['Uprawnieni'] = i['liczba']
            elif i['id'].etykieta == 'Wydane karty':
                data['Wydane karty'] = i['liczba']
            elif i['id'].etykieta == 'Głosy oddane':
                data['Głosy oddane'] = i['liczba']
            elif i['id'].etykieta == 'Głosy nieważne':
                data['Głosy nieważne'] = i['liczba']
            elif i['id'].etykieta == 'Głosy ważne':
                data['Głosy ważne'] = i['liczba']
        if data['Uprawnieni'] < data['Wydane karty']:
            raise ValidationError('Liczba uprawnionych do głosowania powinna być nie mniejsza niż liczba wydanych kart.')
        if data['Wydane karty'] < data['Głosy oddane']:
            raise ValidationError('Liczba wydanych kart powinna być nie mniejsza niż liczba oddanych głosów.')
        if data['Głosy oddane'] != data['Głosy ważne'] + data['Głosy nieważne']:
            raise ValidationError('Liczba oddanych głosów ({}) powinna być równa liczba sumie głosów ważnych i'
                                  ' nieważnych ({}).'.format(data['Głosy oddane'], data['Głosy nieważne'] + data['Głosy ważne']))
        suma_kandydatow = Wynik.objects.select_for_update().filter(obwod=obwod).aggregate(Sum('liczba'))['liczba__sum']
        if suma_kandydatow != data['Głosy ważne']:
            raise ValidationError('Liczba głosów ważnych ({}) nie zgadza się z sumą głosów poszczególnych kandydatów'
                                  ' ({}).'.format(data['Głosy ważne'], suma_kandydatow))


class StatystykiInline(admin.TabularInline):
    model = Statystyka
    formset = StatystykiInlineFormSet
    fields = ['etykieta', 'liczba']
    extra = 0
    readonly_fields = ['etykieta']
    verbose_name_plural = 'Statystyki'
    can_delete = False


class ObwodInline(admin.TabularInline):
    model = Obwod
    fields = ['nazwa']
    extra = 0
    verbose_name_plural = 'Obwody'


class GminaInline(admin.TabularInline):
    model = Gmina
    fields = ['nazwa']
    extra = 0
    verbose_name_plural = 'Gminy'


class OkregInline(admin.TabularInline):
    model = Okreg
    readonly_fields = ['numer']
    ordering = ['numer']
    extra = 0
    verbose_name_plural = 'Okręgi'
    verbose_name = 'Okręg'


class ObwodAdmin(admin.ModelAdmin):
    fields = ['nazwa', 'gmina']
    inlines = [WynikInline]
    list_filter = ['gmina__okreg__wojewodztwo', 'gmina__okreg']
    search_fields = ['nazwa', 'gmina__nazwa']
    ordering = ['gmina__nazwa', 'nazwa']
    list_display = ['nazwa', 'gmina']


class GminaAdmin(admin.ModelAdmin):
    fields = ['nazwa', 'okreg']
    inlines = [ObwodInline]
    list_filter = ['okreg__wojewodztwo', 'okreg']
    list_display = ['nazwa', 'okreg']
    search_fields = ['nazwa', 'okreg__numer']
    # list_filter = [MyListFilter]


class OkregAdmin(admin.ModelAdmin):
    fields = ['numer', 'wojewodztwo']
    inlines = [GminaInline]
    list_filter = ['wojewodztwo']
    list_display = ['numer', 'wojewodztwo']
    list_display_links = ['numer', 'wojewodztwo']
    search_fields = ['numer', 'wojewodztwo__nazwa']
    readonly_fields = ['numer']


class WojewodztwoAdmin(admin.ModelAdmin):
    fields = ['numer', 'nazwa']
    readonly_fields = ['numer']
    list_display = ['numer', 'nazwa']
    list_display_links = ['numer', 'nazwa']
    search_fields = ['numer', 'nazwa']
    inlines = [OkregInline]


class KandydatAdmin(admin.ModelAdmin):
    list_display = ['nazwisko', 'imie']
    search_fields = ['nazwisko', 'imie']
    list_display_links = ['nazwisko', 'imie']


class StatystykiDlaObwodu(Obwod):
    class Meta:
        proxy = True
        verbose_name_plural = 'Statystyki dla obwodów'


class StatystykiDlaObwoduAdmin(ObwodAdmin):
    inlines = [StatystykiInline]


admin.site.register(Obwod, ObwodAdmin)
admin.site.register(StatystykiDlaObwodu, StatystykiDlaObwoduAdmin)
admin.site.register(Gmina, GminaAdmin)
admin.site.register(Okreg, OkregAdmin)
admin.site.register(Wojewodztwo, WojewodztwoAdmin)
admin.site.register(Kandydat, KandydatAdmin)