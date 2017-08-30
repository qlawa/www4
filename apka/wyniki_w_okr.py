from apka.models import *

l_okregow = 68

kandydaci = Kandydat.objects.all()
staty_info = ['Uprawnieni', 'Wydane karty', 'Głosy oddane', 'Głosy nieważne', 'Głosy ważne']


for i in range(5, l_okregow+1):
    print(i)
    okr = Okreg.objects.get(numer=i)
    wyniki = {i: 0 for i in kandydaci}
    staty = {i: 0 for i in staty_info}
    gm = Gmina.objects.filter(okreg=i)
    obw = Obwod.objects.filter(gmina__in=gm)
    wyn = Wynik.objects.filter(obwod__in=obw)
    sta = Statystyka.objects.filter(obwod__in=obw)
    for k in kandydaci:
        w = wyn.filter(kandydat=k)
        w2 = [x.liczba_glosow for x in w]
        WynikOkr(kandydat=k, okreg=okr, liczba_glosow=sum(w2)).save()
    for s in staty_info:
        ss = sta.filter(etykieta=s)
        s2 = [y.liczba for y in ss]
        StatystykaOkr(etykieta=s, okreg=okr, liczba=sum(s2)).save()

