import uuid
import binascii
import os, shutil
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage

from PyPDF2 import PdfFileReader

 
class Kontrahent(models.Model):
    nazwa = models.CharField(max_length=100)
    drukowac_wyniki = models.BooleanField(default=False)

    # pola z lab3000
    id_platnika = models.IntegerField()

    def __str__(self):
        return self.nazwa

    class Meta:
        verbose_name_plural = "Płatnicy"

class MyUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name="myuser")
    kontrahent = models.ForeignKey(Kontrahent, on_delete=models.PROTECT, related_name="myuser")
    pwzdl = models.CharField(max_length=6, blank=True, default='')
    katalog_ps = models.CharField(max_length=3, blank=True, default='')

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = "Użytkownicy"

class Pacjent(models.Model):
    imie = models.CharField(max_length=200, null=True, blank=True)
    nazwisko = models.CharField(max_length=200, null=True, blank=True)
    pesel = models.CharField(max_length=20, null=True, blank=True)
    data_urodzenia = models.DateField(null=True, blank=True)
    
    # pola z lab3000
    id_pacjenta = models.IntegerField()
    miejsce_zam = models.CharField(max_length=200, null=True, blank=True)

    @property
    def nazwa(self):
        return self.imie + ' ' + self.nazwisko

    def __str__(self):
        data_urodzenia = self.data_urodzenia.strftime("%Y-%m-%d") if self.data_urodzenia else 'nie podano'
        pesel_lub_rok = self.pesel if self.pesel else data_urodzenia
        adres = self.miejsce_zam if self.miejsce_zam else 'nie podano'
        return '{nazwisko} {imie} ({pesel}) adres: {adres}'.format(imie=self.imie,
                nazwisko=self.nazwisko,
                pesel=pesel_lub_rok,
                adres=adres)

    class Meta:
        verbose_name_plural = "Pacjenci"

class Zlecenie(models.Model):
    numer = models.IntegerField()
    zlecone = models.DateTimeField()
    pacjent = models.ForeignKey(Pacjent, on_delete=models.PROTECT)
    owner = models.ForeignKey(Kontrahent, on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)
    na_dzien = models.DateTimeField(blank=True, null=True, default=None)
    zrealizowane = models.DateTimeField(blank=True, null=True, default=None)
    anulowane = models.BooleanField(default=False)

    # pola z lab3000
    id_zlecenia = models.IntegerField()

    def __str__(self):
        return str(self.numer)


    class Meta:
        ordering = ['-created']
        verbose_name_plural = "Zlecenia"


class GrupaBadan(models.Model):
    nazwa = models.CharField(max_length=200)
    nazwa_krotka = models.CharField(max_length=50)
    id_badania = models.IntegerField(null=True)

    def __str__(self):
        return str(self.nazwa)

    class Meta:
        verbose_name_plural = "Grupy Badań"

class Badanie(models.Model):
    nazwa = models.CharField(max_length=200)
    nazwa_krotka = models.CharField(max_length=50)
    icd = models.CharField(max_length=10, blank=True, default='')
    children = models.ManyToManyField('self')
    grupabadan = models.ForeignKey(GrupaBadan, blank=True, null=True, default=None, on_delete=models.PROTECT)
    zlec_w_calosci = models.BooleanField(default=False)
    jednostka = models.CharField(max_length=20, blank=True, default='')

    # pola z lab3000
    id_badania = models.IntegerField(null=True)

    def __str__(self):
        return str(self.nazwa_krotka)

    class Meta:
        verbose_name_plural = "Badania"


class WartosciReferencyjne(models.Model):
    od = models.CharField(max_length=10, blank=True, default ='')
    do = models.CharField(max_length=10, blank=True, default ='')
    wydruk = models.CharField(max_length=50, blank=True, default ='')

    # pola z lab3000
    id_tabeli = models.IntegerField()

    def __str__(self):
        return str(self.wydruk)

    class Meta:
        verbose_name_plural = "Wartości referencyjne"


class Probka(models.Model):
    numer = models.CharField(max_length=20, blank=True, default='')
    pobrana = models.DateTimeField(blank=True, null=True, default=None)
    
    def __str__(self):
        return self.numer

    class Meta:
        verbose_name_plural = "Próbki"

class WynikManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(parent=None)

class Wynik(models.Model):
    badanie = models.ForeignKey(Badanie, on_delete=models.PROTECT, related_name="wynik_badanie")
    grupa = models.ForeignKey(GrupaBadan, on_delete=models.PROTECT, related_name="wynik_grupa")
    zlecenie = models.ForeignKey(Zlecenie, on_delete=models.PROTECT, related_name="wyniki")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name="children")
    probka = models.ForeignKey(Probka, on_delete=models.PROTECT, null=True, blank=True, default=None)
    wartosci_referencyjne = models.ForeignKey(WartosciReferencyjne, on_delete=models.PROTECT, blank=True, null=True)
    tekstowy = models.CharField(max_length=50, blank=True, default='')
    flaga = models.CharField(max_length=1, blank=True, default='')
    wykonany = models.DateTimeField(blank=True, null=True, default=None)
    odprawiony = models.DateTimeField(blank=True, null=True, default=None)
    wydrukowany = models.DateTimeField(blank=True, null=True, default=None)
    anulowany = models.BooleanField(default=False)
    gotowy_do_hl7 = models.BooleanField(default=False)
    wyslany_do_hl7 = models.BooleanField(default=False)
    # pola z lab3000
    id_tabeli = models.IntegerField(blank=True, null=True, default=None)

    #managers
    #badania_etykiety = WynikManager()

    def __str__(self):
        if self.tekstowy:
            jednostka = '[{}]'.format(self.badanie.jednostka) if self.badanie.jednostka else ''
            return '{wynik} {jednostka}'.format(wynik=self.tekstowy, jednostka=jednostka)
        else:
            return ''

    class Meta:
        ordering = ['badanie__nazwa_krotka']
        verbose_name_plural = "Wyniki"


class WynikPDF(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    anulowany = models.BooleanField(default=False)
    do_sprawdzenia = models.BooleanField(default=True)
    sprawdzony = models.BooleanField(default=False)
    podpisany = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    wydrukowany = models.DateTimeField(null=True)
    pdf = models.FileField(null=True, upload_to='pdf/%Y/%m/%d/')
    ps = models.FileField(null=True, upload_to='ps/')
    zlecenie = models.ForeignKey(Zlecenie, on_delete=models.PROTECT)
    owner = models.ForeignKey(User, null=True, on_delete=models.PROTECT)
    pobrany = models.BooleanField(default=False)
    wyniki = models.ManyToManyField(Wynik)

    def przenies_do_podpisania(self):
        user_folder = self.owner.myuser.katalog_ps
        nazwa = str(self.id) + '.ps'
        new_path = os.path.join(settings.PS_IN, user_folder, nazwa)
        shutil.copy2(self.pdf.path, new_path)
        self.do_sprawdzenia = False
        self.sprawdzony = True   
    
    class Meta:
        ordering = ['created']
        verbose_name_plural = "Wyniki PDF"
  

class WynikPNG(models.Model):
    pdf = models.ForeignKey(WynikPDF, on_delete=models.CASCADE, related_name="img")
    img = models.ImageField(upload_to='img/%Y/%m/%d')
    
    class Meta:
        verbose_name_plural = "Wynik PNG"

