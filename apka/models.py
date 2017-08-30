from django.contrib.admin import models
from django.db import models


class Kandydat(models.Model):
    imie = models.CharField(max_length=64)
    nazwisko = models.CharField(max_length=64)

    def __str__(self):
        return str(self.imie + " " + self.nazwisko)

    class Meta:
        unique_together = ('imie', 'nazwisko')
        verbose_name_plural = 'Kandydaci'



class Wojewodztwo(models.Model):
    numer = models.IntegerField(unique=True, primary_key=True)
    nazwa = models.CharField(max_length=64)

    def __str__(self):
        return "Wojewodztwo " + self.nazwa

    class Meta:
        verbose_name_plural = 'Województwa'
        verbose_name = 'Województwo'


class Okreg(models.Model):
    numer = models.IntegerField(unique=True, primary_key=True)
    wojewodztwo = models.ForeignKey(Wojewodztwo)

    def __str__(self):
        return "Okreg " + str(self.numer)

    class Meta:
        verbose_name_plural = 'Okręgi'
        verbose_name = 'Okręg'


class Gmina(models.Model):
    nazwa = models.CharField(max_length=64)
    numer = models.IntegerField(unique=True, primary_key=True)
    okreg = models.ForeignKey(Okreg)

    def __str__(self):
        return self.nazwa

    class Meta:
        verbose_name_plural = 'Gminy'


class Obwod(models.Model):
    numer = models.IntegerField(unique=True)
    nazwa = models.CharField(max_length=128)
    gmina = models.ForeignKey(Gmina)

    def __str__(self):
        return "Obwod " + str(self.numer%1000)

    class Meta:
        unique_together = ('numer', 'gmina')
        verbose_name_plural = 'Obwody'
        verbose_name = 'Obwód'


class Wynik(models.Model):
    kandydat = models.ForeignKey(Kandydat)
    liczba = models.IntegerField()
    obwod = models.ForeignKey(Obwod)

    def __str__(self):
        return "W " + str(self.obwod) + " " + str(self.kandydat) + " otrzymał " + str(self.liczba)

    class Meta:
        unique_together = ('kandydat', 'obwod')
        verbose_name_plural = 'Wyniki'


class Statystyka(models.Model):
    etykieta = models.CharField(max_length=32)
    liczba = models.IntegerField()
    obwod = models.ForeignKey(Obwod)

    def __str__(self):
        return str(self.obwod) + ": " + str(self.etykieta) + " " + str(self.liczba)

    class Meta:
        unique_together = ('etykieta', 'obwod')
        verbose_name_plural = 'Statystyki'
