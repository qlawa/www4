from django.contrib.auth.models import User
from django.core.serializers import json
from django.db import transaction
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json

from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import *

staty_info = ['Uprawnieni', 'Wydane karty', 'Głosy oddane', 'Głosy ważne', 'Głosy nieważne']


def kraj(request):
    return render(request, 'kraj.html')


@csrf_exempt
def new_login(request):
    return render(request, 'rest_login.html')


def daj_slownik_kandydatow_z_wynikiem(wyniki_do_posortowania):
    kandydaci = Kandydat.objects.all()
    wyniki = {i: 0 for i in kandydaci}
    for j in kandydaci:
        wyniki[j] = wyniki_do_posortowania.filter(kandydat=j).aggregate(Sum('liczba'))['liczba__sum']
    return_value = []
    for j in kandydaci:
        return_value.append({'kandydat': j.id, 'wynik': wyniki[j]})
    return return_value


def daj_slownik_statystyk(statystyki_do_posortowania):
    staty = {i: 0 for i in staty_info}
    for j in staty_info:
        staty[j] = statystyki_do_posortowania.filter(etykieta=j).aggregate(Sum('liczba'))['liczba__sum']
    return_value = []
    for j in staty_info:
        return_value.append({'etykieta': j, 'liczba': staty[j]})
    return return_value


@api_view(['GET'])
def kraj_json(request):
    wyniki = {'wynik': daj_slownik_kandydatow_z_wynikiem(Wynik.objects.all()),
              'statystyki': daj_slownik_statystyk(Statystyka.objects.all()),
              'zasieg': 'KRAJ',
              'id_terenu': '0'}

    wyniki_serialized = MyWynikSerializer(wyniki)
    context = {
        'dane': wyniki_serialized.data,
        'odnosniki': '',
    }
    return Response(context)


@api_view(['GET'])
def wojewodztwo_json(request, wojewodztwo_nr):
    woj = get_object_or_404(Wojewodztwo, numer=wojewodztwo_nr)
    odnosniki = Okreg.objects.filter(wojewodztwo=woj)
    odnosniki_serialized = OkregSerializer(odnosniki, many=True)

    wyniki = {'wynik': daj_slownik_kandydatow_z_wynikiem(Wynik.objects.filter(obwod__gmina__okreg__in=odnosniki)),
              'statystyki': daj_slownik_statystyk(Statystyka.objects.filter(obwod__gmina__okreg__in=odnosniki)),
              'zasieg': 'WOJEWODZTWO',
              'id_terenu': wojewodztwo_nr}

    wyniki_serialized = MyWynikSerializer(wyniki)
    context = {
        'dane': wyniki_serialized.data,
        'odnosniki': odnosniki_serialized.data,
    }
    return Response(context)


@api_view(['POST'])
def szukaj_gminy_json(request, nazwa):
    print('Gdzie są moje gminy')
    gminy = Gmina.objects.filter(nazwa__contains=nazwa)
    gminy_serialized = GminaSerializer(gminy, many=True)
    print('gminy_serialized')
    print(gminy_serialized)
    return Response(gminy_serialized.data)


@api_view(['GET'])
def okreg_json(request, okreg_nr):
    okr = get_object_or_404(Okreg, numer=okreg_nr)
    odnosniki = Gmina.objects.filter(okreg=okr)
    odnosniki_serialized = GminaSerializer(odnosniki, many=True)

    wyniki = {'wynik': daj_slownik_kandydatow_z_wynikiem(Wynik.objects.filter(obwod__gmina__in=odnosniki)),
              'statystyki': daj_slownik_statystyk(Statystyka.objects.filter(obwod__gmina__in=odnosniki)),
              'zasieg': 'OKREG',
              'id_terenu': okreg_nr}

    wyniki_serialized = MyWynikSerializer(wyniki)
    context = {
        'dane': wyniki_serialized.data,
        'odnosniki': odnosniki_serialized.data,
    }
    return Response(context)


@api_view(['GET'])
def gmina_json(request, gmina_nr):
    gmina = get_object_or_404(Gmina, numer=gmina_nr)
    obwody = Obwod.objects.filter(gmina=gmina)

    wyniki = {'wynik': daj_slownik_kandydatow_z_wynikiem(Wynik.objects.filter(obwod__gmina=gmina)),
              'statystyki': daj_slownik_statystyk(Statystyka.objects.filter(obwod__gmina=gmina)),
              'zasieg': 'GMINA',
              'id_terenu': gmina_nr}
    print(wyniki)
    wyniki_obwodow = []
    for i in obwody:
        wyniki_obwodow.append(
            {
                'wynik': daj_slownik_kandydatow_z_wynikiem(Wynik.objects.filter(obwod=i)),
                'statystyki': daj_slownik_statystyk(Statystyka.objects.filter(obwod=i)),
                'zasieg': 'OBWOD',
                'id_terenu': i.id,
            }
        )

    wyniki_obwodow_serialized = MyWynikSerializer(wyniki_obwodow, many=True)

    wyniki_serialized = MyWynikSerializer(wyniki)
    context = {
        'dane': wyniki_serialized.data,
        'obwody': wyniki_obwodow_serialized.data,
    }
    return Response(context)


@api_view(['GET', 'POST'])
def edycja_json(request, obwod_id):

    if request.method == 'POST':
        print(request.POST)

        my_data = [key for key in request.POST]
        my_data = my_data[0]
        request_data = json.loads(my_data)

        data = []
        for i in range(0, len(Kandydat.objects.all())):
            data.append({
                'liczba': request_data[4*i]['value'],
                'kandydat': request_data[4*i + 1]['value'],
                'id': request_data[4*i + 2]['value'],
                'obwod': request_data[4*i + 3]['value'],
            })

        serializer = WynikSerializer(data=data, many=True)

        with transaction.atomic():
            dict_z_wynikami_i_statami = blokada(obwod_id)
            if serializer.is_valid() and my_validation(serializer):
                aktualizuj_wyniki(serializer, dict_z_wynikami_i_statami, serializer.data[0]['obwod'])
                print('ok')
                return Response(serializer.data, status=HTTP_200_OK)
            else:
                print('nie ok')
                return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        obwod = Obwod.objects.get(id=obwod_id)

        dane = {'wynik': '',
                'statystyki': daj_slownik_statystyk(Statystyka.objects.filter(obwod=obwod)),
                'zasieg': 'OBWOD',
                'id_terenu': obwod_id,
                }
        dane_serialized = MyWynikSerializer(dane)

        wyniki = []
        for i in Wynik.objects.filter(obwod=obwod):
            wyniki.append({
                'kandydat': i.kandydat,
                'id': i.id,
                'liczba': i.liczba,
                'obwod': i.obwod
            })
        wyniki_serialized = WynikSerializer(wyniki, many=True)

        context = {'dane': dane_serialized.data,
                   'wyniki': wyniki_serialized.data,
                   }
        return Response(context, status=HTTP_200_OK)


def my_validation(serializer):
    suma = 0
    obwod = serializer.data[0]['obwod']
    for i in serializer.data:
        suma += i['liczba']
    niewazne = Statystyka.objects.get(etykieta='Głosy nieważne', obwod=obwod).liczba
    wydane = Statystyka.objects.get(etykieta='Wydane karty', obwod=obwod).liczba
    if niewazne + suma > wydane:
        raise serializers.ValidationError('Suma głosów ważnych i nieważnych ({}) przekracza liczbę wydanych kart ({})'.
                                          format(suma + niewazne, wydane))
    return True


def blokada(obwod_id):
    obwod = Obwod.objects.get(id=obwod_id)

    staty = Statystyka.objects.select_for_update().filter(obwod=obwod)
    wyniki = Wynik.objects.select_for_update().filter(obwod=obwod)

    ret = {
        'wyniki_qs': wyniki,
        'staty_qs': staty,
    }
    return ret


def aktualizuj_wyniki(serializer, my_dict, id_obwodu):
    suma = 0
    for i in serializer.data:
        wynik = my_dict['wyniki_qs'].get(kandydat=i['kandydat'])
        wynik.liczba = i['liczba']
        suma += i['liczba']
        wynik.save()

    if my_dict['staty_qs'] != suma:
        print('naprawiam sume')
        print('suma = {}'.format(suma))
        s = Statystyka.objects.filter(obwod=id_obwodu)
        s2 = s.get(etykieta='Głosy ważne')
        print('wazne = {}'.format(s2.liczba))
        s2.liczba = suma
        s2.save()
        s2 = s.get(etykieta='Głosy oddane')
        s2.liczba = suma + s.get(etykieta='Głosy nieważne').liczba
        s2.save()



@api_view(['GET'])
def kandydaci_json(request):
    kandydaci = Kandydat.objects.all()
    kandydaci_serialized = KandydatSerializer(kandydaci, many=True)
    return Response(kandydaci_serialized.data)


@api_view(['GET'])
def statystyka_json(request, obwod_id):
    staty = Statystyka.objects.filter(obwod__id=obwod_id)
    data = {'Uprawnieni': staty.get(etykieta='Uprawnieni').liczba,
            'Wydane karty': staty.get(etykieta='Wydane karty').liczba,
            'Głosy oddane': staty.get(etykieta='Głosy oddane').liczba,
            'Głosy ważne': staty.get(etykieta='Głosy ważne').liczba,
            'Głosy nieważne': staty.get(etykieta='Głosy nieważne').liczba}

    staty_serialized = ObwodStatystykaSerializer(data)
    return Response(staty_serialized.data)


@api_view(['POST'])
def rest_login(request):
    my_data = [key for key in request.data]
    my_data = my_data[0]
    data = json.loads(my_data)

    uzytkownik = data['uzytkownik']
    czynnosc = data['czynnosc']

    if czynnosc == 'login':
        haslo = data['haslo']
        if czy_passy_popawne(uzytkownik, haslo):
            context = {'zalogowany': True}
            return Response(context, status=HTTP_200_OK)
        else:
            context = {'Nieprawidłowe dane logowania'}
            return Response(context, status=HTTP_400_BAD_REQUEST)
    else:
        return Response(status=HTTP_200_OK)


def czy_passy_popawne(uzytkownik, haslo):
    user = User.objects.filter(username=uzytkownik)
    if len(user) != 1:
        return False
    user = user[0]
    if user.check_password(haslo):
        return True
    else:
        return False
