from rest_framework import serializers
from .models import *


class KandydatSerializer(serializers.ModelSerializer):

    class Meta:
        model = Kandydat
        fields = '__all__'


class WojewodztwoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Wojewodztwo


class OkregSerializer(serializers.ModelSerializer):

    class Meta:
        model = Okreg
        fields = '__all__'


class GminaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Gmina
        fields = '__all__'


class ObwodSerializer(serializers.ModelSerializer):

    class Meta:
        model = Obwod
        fields = '__all__'


class WynikSerializer(serializers.ModelSerializer):

    class Meta:
        model = Wynik
        fields = '__all__'
        validators = []


class StatystykaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Statystyka
        fields = ['etykieta', 'liczba']


etykiety_do_statystyk = ['Uprawnieni', 'Wydane karty', 'Głosy oddane', 'Głosy ważne', 'Głosy nieważne']


class ObwodStatystykaSerializer(serializers.Serializer):
        Uprawnieni = serializers.IntegerField()
        WydaneKarty = serializers.IntegerField()
        Oddane = serializers.IntegerField()
        Wazne = serializers.IntegerField()
        Niewazne = serializers.IntegerField()


class ProstaStatystykaSerializer(serializers.Serializer):
    etykieta = serializers.ChoiceField(choices=etykiety_do_statystyk, read_only=True)
    liczba = serializers.IntegerField()


class ProstyWynikSerializer(serializers.Serializer):
    wynik = serializers.IntegerField()
    kandydat = serializers.ChoiceField(choices=Kandydat.objects.all(), read_only=True)


class MyWynikSerializer(serializers.Serializer):
    wynik = ProstyWynikSerializer(many=True, required=False)
    statystyki = ProstaStatystykaSerializer(many=True, required=False)
    zasieg = serializers.ChoiceField(choices=['KRAJ', 'WOJEWODZTWO', 'OKREG', 'GMINA', 'OBWOD'])
    id_terenu = serializers.IntegerField()


