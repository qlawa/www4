#from apka.models import *
#import xlrd
#from django.db import transaction
#from apka.models import Obwod, Wynik, Statystyka

#l_okregow = 68
#imie = ['Dariusz Maciej', 'Piotr', 'Jaroslaw', 'Janusz', 'Marian', 'Aleksander', 'Andrzej', 'Jan', 'Andrzej Marian', 'Bogdan', 'Lech', 'Tadeusz Adam']
#nazwisko = ['Grabowski', 'Ikonowicz', 'Kalinowski', 'Korwin-Mikke', 'Krzaklewski', 'Kwasniewski', 'Lepper', 'Lopuszanski', 'Olechowski', 'Pawłowski', 'Walesa', 'Wilecki']
#wojewodztwa = ['Dolnośląskie', 'Kujawsko-Pomorskie', 'Lubelskie', 'Lubuskie', 'Łódzkie', 'Małopolskie', 'Mazowieckie', 'Opolskie', 'Podkarpackie', 'Podlaskie', 'Pomorskie', 'Śląskie', 'Świętokrzyskie', 'Warmińsko-Mazurskie', 'Wielkopolskie', 'Zachodniopomorskie']
#
#Kandydat.objects.all().delete()
# Wojewodztwo.objects.all().delete()
# Okreg.objects.all().delete()
# Gmina.objects.all().delete()
#Obwod.objects.all().delete()
#Wynik.objects.all().delete()
#kandydaci_ref = []


#for l in range(0, len(imie)):
#   k = Kandydat(imie=imie[l], nazwisko=nazwisko[l])
#    k.save()
#    kandydaci_ref.append(k)



# # wojewodztwa:
# nr = 2
# for i in wojewodztwa: Wojewodztwo(numer=nr, nazwa=i).save(); print("{} - {}".format(nr, i)); nr=nr+2
# print(Wojewodztwo.objects.all())
# xls = xlrd.open_workbook("../untitled1/excele/gm-kraj.xls").sheet_by_index(0)
#
# # okregi i gminy
# poprz = -1
# o = ''
# for i in range(1, xls.nrows):
#     nr_okregu = int(xls.row(i)[0].value)
#     if poprz != nr_okregu:
#         wojewodztwo = wojewodztwa[int(int(xls.row(i)[1].value)/20000)-1]
#         w = Wojewodztwo.objects.filter(nazwa=wojewodztwo).first()
#
#         o = Okreg(numer=nr_okregu, wojewodztwo=w)
#         o.save()
#     Gmina(nazwa=xls.row(i)[2].value, numer=int(xls.row(i)[1].value), okreg=o).save()

# etykiety = ['Uprawnieni', 'Wydane karty', 'Głosy oddane', 'Głosy nieważne', 'Głosy ważne']

#
# @transaction.atomic
# def jazda():
#     from apka.models import Gmina, Obwod, Wynik, Kandydat, Statystyka
#     import xlrd
#     l_okregow = 68
#     kandydaci = Kandydat.objects.all()
#     etykiety = ['Uprawnieni', 'Wydane karty', 'Głosy oddane', 'Głosy nieważne', 'Głosy ważne']
#     print("Start")
#     # obwody i wyniki
#     for nr in range(1, l_okregow + 1):
#         #o = Okreg.objects.get(numer=nr)
#         xls = xlrd.open_workbook("../untitled1/excele/obw/obw" + "{0:02d}".format(nr) + ".xls").sheet_by_index(0)
#         poprz_kod_gminy = -1
#         g = 0
#         for l in range(1, xls.nrows):
#             print("{}/{}: {}/{}".format(nr, l_okregow, l, xls.nrows))
#             wiersz = [j.value for j in xls.row(l)]
#             kod_gminy = wiersz[1]
#             if kod_gminy != poprz_kod_gminy:
#                 g = Gmina.objects.get(numer=kod_gminy)
#                 poprz_kod_gminy = kod_gminy
#             obw = Obwod(gmina=g, numer=int(wiersz[1])*1000+int(wiersz[4]), nazwa=wiersz[6])
#             #obw = Obwod.objects.get(numer=int(wiersz[1])*1000+int(wiersz[4]))
#             obw.save()
#             wiersz = wiersz[7:]
#             for j in range(5):
#                 Statystyka(etykieta=etykiety[j], liczba=wiersz[j], obwod=obw).save()
#             wiersz = wiersz[5:]
#             j = 0
#             for ll in kandydaci:
#                 Wynik(kandydat=ll, obwod=obw, liczba=wiersz[j]).save()
#                 #w = Wynik.objects.get(kandydat=ll, obwod=obw).liczba = wiersz[j]
#                 j = j+1
#
# @transaction.atomic
# def daj_odwod_id_w_miejsce_numer():
#     #for obwod in Obwod.objects.all():
#         obwod = Obwod.objects.first()
#         wyniki = Wynik.objects.filter(obwod=obwod)
#         staty = Statystyka.objects.filter(obwod=obwod)
#         print(wyniki)
#         print(staty)
# #jazda()
#
# daj_odwod_id_w_miejsce_numer()