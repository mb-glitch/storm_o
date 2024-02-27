import os
import time
import logging

from .mssql import Mssql
from django.db import models

logger = logging.getLogger(__name__)

class Aparat(models.Model):
    nazwa = models.CharField(max_length=100)
    # wzór do odpowiedzi na zapytania q
    header = models.CharField(max_length=300, null=True, blank=True)
    patient = models.CharField(max_length=300, null=True, blank=True)
    order = models.CharField(max_length=300, null=True, blank=True)
    no_order = models.CharField(max_length=300, null=True, blank=True)
    ender = models.CharField(max_length=300, null=True, blank=True)
    # stan aparatu
    status = models.DateTimeField(auto_now=True)
    astm = models.BooleanField(default=False)
    astm_msg = models.CharField(max_length=300, null=True, blank=True)
    # pola z lab3000
    id_aparatu = models.IntegerField()
    # pola do wykorzystania w ramkach danych
    pattern = models.CharField(max_length=100, null=True, blank=True)
    pole_numery_zlecenia_order = models.IntegerField()
    pole_numery_zlecenia_question = models.IntegerField()
    pole_data_wyniku = models.IntegerField()
    pole_nazwa_badania = models.IntegerField()
    pole_wynik = models.IntegerField()
    pole_jednostki = models.IntegerField()
    pole_flaga = models.IntegerField()

    def __str__(self):
        return self.nazwa

    class Meta:
        verbose_name_plural = "Aparaty"
 

class TestZnakowy(models.Model):
    tid = models.IntegerField()
    nazwa = models.CharField(max_length=100)
    nazwa_wydruk = models.CharField(max_length=100, null=True, blank=True)
    jednostki = models.CharField(max_length=20, null=True, blank=True)
    typ_wyniku = models.CharField(max_length=1, default='N')
    wynik_numeryczny = models.CharField(max_length=1, default='T')
    nadpisz = models.CharField(max_length=1, default='T')
    aparat = models.ForeignKey(Aparat, on_delete=models.CASCADE)

    def __str__(self):
        return self.nazwa_wydruk

    class Meta:
        verbose_name_plural = "Testy znakowe przypisane do aparatu"

class Wynik(models.Model):
    # pid = models.IntegerField()
    pid = models.CharField(max_length=20)
    data = models.DateTimeField(null=True, blank=True)
    wynik = models.CharField(max_length=200, null=True, blank=True)
    wyslany = models.BooleanField(default=False)
    obrazek = models.FileField(null=True, blank=True, upload_to='wynik_obrazkowy/')
    created = models.DateTimeField(auto_now_add=True)
    # do tworzenia opisów
    test_znakowy = models.ForeignKey(TestZnakowy, on_delete=models.CASCADE)


    @property
    def wynik_slownik(self):
        wynik = self.wynik
        s = {
            #'-': 'nieobecne',
            #'+': 'pojedyncze',
            #'++': 'nieliczne',
            #'+++': 'liczne',
            #'++++': 'b. liczne',
            'neg': 'ujemny',
            'norm': 'w normie'
            }
        if wynik in s:  # tłumaczę plusy na opisy
            wynik = s[wynik]
        return wynik

    class Meta:
        verbose_name_plural = "Wyniki lokalnie"
        ordering = ['-created']
    
    def __str__(self):
        return self.created.strftime("%Y-%m-%d %H:%M:%S")

    @property
    def wynik_as_dict(self):
        d = {
        'pid': str(self.pid).zfill(10),
        'tid': self.test_znakowy.tid,
        'data': self.data.strftime("%Y-%m-%d %H:%M:%S"),
        'typ_wyniku': self.test_znakowy.typ_wyniku,
        'wynik': self.wynik_slownik,
        'wynik_numeryczny': self.test_znakowy.wynik_numeryczny,
        'nadpisz': self.test_znakowy.nadpisz,
        'id_aparatu': self.test_znakowy.aparat.id_aparatu,
        # w innych celach niż wstaw wyniki
        'numer_zlecenia': self.pid,
        }
        return d


