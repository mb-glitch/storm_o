import json
import os
import shutil
import re
import logging
import time
import subprocess
import datetime

from .obslugabaz import ObslugaBaz
from PyPDF2 import PdfFileReader
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from wyniki.models import Zlecenie, Pacjent, Badanie, Wynik, Kontrahent, WartosciReferencyjne, Probka, WynikPDF, WynikPNG, Zlecenie, MyUser, GrupaBadan
from django.core.files import File

# Get an instance of a logger
logger = logging.getLogger(__name__)

class Dispatcher:
    def __init__(self):
        pass

    def WARTOSCI_REFER(self, row):
        if row['mb_task'] == 'i':
            w = WartosciReferencyjne.objects.create(od=row['WARTOSC_OD'], do=row['WARTOSC_DO'], wydruk=row['NA_WYDR'], id_tabeli=row['ID_TABELI'])
            w.save()      

    def WYNIKI_BADAN(self, row):
        flaga = row['FLAGA'] if row['FLAGA'] else ''
        wr = WartosciReferencyjne.objects.get(id_tabeli=row['ID_WARTOSCI_REF']) if row['ID_WARTOSCI_REF'] else None
        z = Zlecenie.objects.get(id_zlecenia=int(row['ID_ZLECENIA']))
        b = Badanie.objects.get(id_badania=row['ID_BADANIA'])
        id_profilu = -row['ID_PROFILU']
        p = None
        logger.debug('próbuje znaleźć bg')
        bg = GrupaBadan.objects.get(id_badania=id_profilu)
        try:
            etykieta = Badanie.objects.get(id_badania=id_profilu)
            if etykieta.zlec_w_calosci:
                p, created = Wynik.objects.get_or_create(zlecenie=z, badanie=etykieta, grupa=bg)
        except Badanie.DoesNotExist:
            pass
            
        data_wyniku = row['DATA_WYNIKU'] if row['DATA_WYNIKU'] else None
        if row['mb_task'] == 'i':
            logger.debug('i próbuje stworzyć nowy Wynik')
            w = Wynik.objects.create(badanie=b, grupa=bg, parent=p, zlecenie=z, wartosci_referencyjne=wr, flaga=flaga, id_tabeli=row['ID_TABELI'])
            w.save()
        elif row['mb_task'] == 'u':    
            w = Wynik.objects.get(id_tabeli=row['ID_TABELI'])    
            if w.tekstowy not in ['', None, row['WYNIK_ZN']]:
                w.anulowany = True
                w.save()
                w = Wynik.objects.create(badanie=b, grupa=bg, parent=p, zlecenie=z, wartosci_referencyjne=wr, flaga=flaga, id_tabeli=row['ID_TABELI'])
            w.flaga = flaga
            w.wartosci_referencyjne = wr
            w.tekstowy = row['WYNIK_ZN']
            w.wykonany = data_wyniku
            w.save()
        elif row['mb_task'] == 'd':
            w = Wynik.objects.get(id_tabeli=row['ID_TABELI'])
            w.anulowany = True
            w.save()

    def probki(self, row):
        z = Zlecenie.objects.get(id_zlecenia=int(row['ID_ZLECENIA']))
        id_profilu = -row['ID_PROFILU']
        bg = GrupaBadan.objects.get(id_badania=id_profilu)
        w = Wynik.objects.filter(grupa=bg, zlecenie=z)
        data_pobrania = row['DATA_POBRANIA'] if row['DATA_POBRANIA'] else None
        data_odprawienia = row['DATA_ODPRAWIENIA'] if row['DATA_ODPRAWIENIA'] else None
        data_wydruku = row['DATA_WYDRUKU'] if row['DATA_WYDRUKU'] else None
        numer_probki = row['NR_PROBKI'] if row['NR_PROBKI'] else str(z.numer).zfill(10)
        if row['mb_task'] == 'i':
            p, created = Probka.objects.get_or_create(numer=numer_probki, pobrana=data_pobrania)
            w.update(odprawiony=data_odprawienia, wydrukowany=data_wydruku, probka=p)
        
        elif row['mb_task'] == 'u':
            p, created = Probka.objects.get_or_create(numer=numer_probki, pobrana=data_pobrania)
            w.update(odprawiony=data_odprawienia, wydrukowany=data_wydruku, probka=p)
    
    def zlecenie_badania(self, row):
        p = Pacjent.objects.get(id_pacjenta=row['ID_PACJENTA'])
        k = Kontrahent.objects.get(id_platnika=row['ID_PLATNIKA'])
        data_zlecenia = row['DATA_ZLECENIA']
        na_dzien = row['ZLECENIE_NA_DZIEN'] if row['ZLECENIE_NA_DZIEN'] else None
        zrealizowane = row['DATA_ZREALIZOWANIA'] if row['DATA_ZREALIZOWANIA'] else None
        if row['mb_task'] == 'i':
            z = Zlecenie.objects.create(
                    id_zlecenia=row['ID_ZLECENIA'],
                    numer=row['NUMER_ZLECENIA'],
                    zlecone=data_zlecenia,
                    na_dzien=na_dzien,
                    zrealizowane=zrealizowane,
                    pacjent=p, 
                    owner=k)
            z.save()
        elif row['mb_task'] == 'u':
            z = Zlecenie.objects.get(id_zlecenia=row['ID_ZLECENIA'])
            z.numer = row['NUMER_ZLECENIA']
            z.zlecone = data_zlecenia
            z.na_dzien = na_dzien
            z.zrealizowane = zrealizowane
            z.pacjent = p
            z.owner = k
            z.save()


    def PACJENCI(self, row):
        if row['mb_task'] == 'i':
            p = Pacjent.objects.create(pesel=row['PESEL'], imie=row['IMIE'], nazwisko=row['NAZWISKO'], miejsce_zam=row['MIEJSCE_ZAM'], id_pacjenta=row['ID_PACJENTA'])
            p.save()
        elif row['mb_task'] == 'u':
            p = Pacjent.objects.get(id_pacjenta=row['ID_PACJENTA'])
            p.imie = row['IMIE']
            p.nazwisko = row['NAZWISKO']
            p.pesel= row['PESEL']
            p.miejsce_zam = row['MIEJSCE_ZAM']
            p.save()

    def GRUPY_BADAN(self, row):
        pattern = r'\[(.*?)\]'
        match = re.findall(pattern, row['NAZWA_GRUPY'])
        icd = match[0] if match else ''
        if row['mb_task'] == 'i':
            id_profilu = -row['ID_GRUPY']  # daje ujemną, żeby id profilu nie mieszały się z id_badania
            g = GrupaBadan.objects.create(nazwa_krotka=row['SKROT'], id_badania=id_profilu)
            g.nazwa = row['NAZWA_GRUPY']
            g.save()
            if row['ZLEC_W_CAL'] == 'T': 
                b = Badanie.objects.create(nazwa_krotka=row['SKROT'], zlec_w_calosci=True, id_badania=id_profilu)
                b.nazwa = row['NAZWA_GRUPY']
                b.icd = icd          
                b.grupabadan=g
                b.save()
        elif row['mb_task'] == 'u':
            id_profilu = -row['ID_GRUPY']  # daje ujemną, żeby id profilu nie mieszały się z id_badania
            g = GrupaBadan.objects.get(id_badania=id_profilu)
            g.nazwa = row['NAZWA_GRUPY']
            g.save()
            if row['ZLEC_W_CAL'] == 'T': 
                b = Badanie.objects.get(id_badania=id_profilu)
                b.nazwa = row['NAZWA_GRUPY']
                b.icd = icd
                b.grupabadan=g
                b.save()

    def BADANIA(self, row):
        #pattern = '\[P\].+?\[\/P\]'
        pattern = r'\[(.*?)\]'
        match = re.findall(pattern, row['NAZWA_BADANIA'])
        icd = match[0] if match else ''
        jednostka = row['JM'] if row['JM'] else ''
        if row['mb_task'] == 'i':
            b = Badanie.objects.create(nazwa=row['NAZWA_BADANIA'], nazwa_krotka=row['KOD_BADANIA'], id_badania=row['ID_BADANIA'], icd=icd, jednostka=jednostka)
            b.save()
        elif row['mb_task'] == 'u':
            b = Badanie.objects.get(id_badania=row['ID_BADANIA'])
            b.nazwa = row['NAZWA_BADANIA']
            b.icd = icd
            b.jednostka = jednostka
            b.save()

    def badanie_profil(self, row):
        if row['mb_task'] == 'i':
            b = Badanie.objects.get(id_badania=row['ID_BADANIA'])
            id_profilu = -row['ID_PROFILU']
            bg = None
            try:
                bg = Badanie.objects.get(id_badania=id_profilu)
                logger.debug('dodaje badanie {b} do profilu {p}'.format(b=b.nazwa, p=bg.nazwa))

                bg.children.add(b)
                bg.save()
            except Badanie.DoesNotExist:
                bg = GrupaBadan.objects.get(id_badania=id_profilu)
                logger.debug('badanie złożone {b} nie istnieje, dodaję do grupybadan {g}'.format(b=b.nazwa, g=bg.nazwa))
                b.grupabadan = bg
                b.save()

    def platnik(self, row):
        if row['mb_task'] == 'i':
            b = Kontrahent.objects.create(id_platnika=row['ID_PLATNIKA'], nazwa=row['NAZWA_PLATNIKA'])
            b.save()


class PrzyjmijPS:
    PDF_TIMEOUT = 60  # wiek podpisanego pliku pdf, pdfcreator musi się wyrobić
    ps_in_path = settings.PS_ALL
    pdf_in_path = os.path.join(settings.MEDIA_ROOT, 'pdf_in')
    img_in_path = os.path.join(settings.MEDIA_ROOT, 'img_tmp')
    pdf_podpisany_path = settings.PDF_PODPISANY

    def __init__(self):
        pass


    def newest_valid_date(self, string):
        mat = re.findall(r'(\d{2})[-](\d{2})[-](\d{4})[\s](\d{2})[:](\d{2})', string)
        daty = []
        for dt in mat:
            try:
                dt = [int(x) for x in dt]
                a = datetime.datetime(dt[2], dt[1], dt[0], dt[3], dt[4])
                daty.append(a)
            except ValueError:
                pass
        return max(dt for dt in daty)

    def get_nr_pwzdl(self, string):
        podpis = string.find('Autoryzow')  # dolna część wyniku z tekstek kto autoryzuje
        string = string[podpis:]  # w tej części szukam numeru pwzdl i przypisuje mu użytkownika
        pwzdls = MyUser.objects.values_list('pwzdl', flat=True)
        for e in pwzdls:
            if e in string:
                mu = MyUser.objects.get(pwzdl=e)
                return User.objects.get(myuser=mu)

    def get_lista_icd(self, string):
        pattern = r'\[(.*?)\]'
        match = re.findall(pattern, string)
        return match  # obdzieram nawiasy i zostawiam same numery icd 

    def przypisz_wyniki_do_pdf(self, lista_icd, data_wydruku, pdf, zlecenie):
        wyniki = Wynik.objects.filter(zlecenie=zlecenie)
        for w in wyniki:
            if not w.odprawiony:
                return
            if w.badanie.icd in lista_icd or w.grupa.icd in lista_icd:
                if w.odprawiony < data_wydruku:
                    pdf.wyniki.add(w)
                    pdf.save()

    def get_nr_zlecenia_i_data(self, file_path):
        """ Pobieram pierszych 7 znaków z pdf'a,
        jeżeli wszystkie są cyframi to zwracam nr zlecenia do dict zlecenie,
        jeżeli nie są to zwracam False
        """
        with open(file_path, "rb") as pdfFile:
            pdf = PdfFileReader(pdfFile)
            if pdf.isEncrypted:
                pdf.decrypt('')
            pdf_text_all = ''
            count = pdf.numPages
            for i in range(count):
                page = pdf.getPage(i)
                pdf_text_all += page.extractText()
            pdf_text = pdf.getPage(0).extractText()
            nr_zlecenia = pdf_text[:7]
            # sprawdzam czy pobrany text jest 7 cyfrowym numerem, \D szuka wszystkiego oprócz liczby
            match = re.search('\D', nr_zlecenia)
            zle = ['', 0, None]
            if nr_zlecenia in zle:
                return False
            elif not match:
                lista_icd = self.get_lista_icd(pdf_text_all)
                data_wydruku = self.newest_valid_date(pdf_text)
                autoryzujacy = self.get_nr_pwzdl(pdf_text)
                return nr_zlecenia, data_wydruku, autoryzujacy, lista_icd
            else:
                return False

    def get_pdf_files_name_in_order_wait(self, katalog, rozszezenie):
        files = []
        file_names = os.listdir(katalog)
        for f in file_names:
            if f.endswith(rozszezenie):
                fpath = os.path.join(katalog, f)
                now = time.time()
                fage = now - os.stat(fpath).st_mtime
                logger.debug('Plik {fname} ma {age} sekund'.format(fname=f, age=fage)) 
                if fage > 60:   # czas żeby pdfy zdążyły się podpisać
                    files.append(fpath)
        files.sort(key=lambda x: os.path.getmtime(x))
        return files

        

    def get_files_name_in_order(self, katalog, rozszezenie):
        files = []
        file_names = os.listdir(katalog)
        for f in file_names:
            if f.endswith(rozszezenie):
                fpath = os.path.join(katalog, f)
                files.append(fpath)
        files.sort(key=lambda x: os.path.getmtime(x))
        return files

    def clean_temp_files(self):
        logger.debug('Czyszczę katalogi z tymczasowymi plikami jakby zostało coś po błądzie')
        a = self.get_files_name_in_order(self.pdf_in_path, '.pdf')
        b = self.get_files_name_in_order(self.img_in_path, '.png')
        c = a + b
        for f in c:
            logger.debug(f)
            os.remove(f)

    def convert_to_png_and_pdf(self, ps_path):
        head, tail = os.path.split(ps_path)
        png_path = os.path.join(self.img_in_path, tail.replace('.ps', ''))
        png_output = '-sOutputFile={fn}-%d.png'.format(fn=png_path)
        pdf_path = os.path.join(self.pdf_in_path, tail.replace('.ps', '.pdf'))
        pdf_output = '-sOutputFile={fn}'.format(fn=pdf_path)

        convert_pdf = ['gs', '-sDEVICE=pdfwrite', pdf_output, '-dBATCH', '-dNOPAUSE', ps_path]
        convert_png = ['gs', '-sDEVICE=pnggray', '-r300', png_output, '-dBATCH', '-dNOPAUSE', ps_path]
        mogrify = ['mogrify', '-resize', 'x700', self.img_in_path + '/*.png']

        subprocess.run(convert_pdf)
        subprocess.run(convert_png)
        subprocess.run(mogrify)
        
    def save_pdf_to_db(self, ps_path, pdf_path, data_wydruku, zlecenie, user):
        ps_head, ps_tail = os.path.split(ps_path)
        pdf_head, pdf_tail = os.path.split(pdf_path)
        p, created = WynikPDF.objects.get_or_create(wydrukowany=data_wydruku, zlecenie=zlecenie, owner=user)
        with open(ps_path, 'rb') as f:     
            p.ps.save(ps_tail, File(f))
        with open(pdf_path, 'rb') as f:     
            p.pdf.save(pdf_tail, File(f))
        p.save()
        os.remove(pdf_path)
        os.remove(ps_path)
        return p

    def save_podpisany_pdf_to_db(self, pdf_path, data_wydruku, zlecenie, user):
        pdf_head, pdf_tail = os.path.split(pdf_path)
        p = WynikPDF.objects.get(wydrukowany=data_wydruku, zlecenie=zlecenie, owner=user, sprawdzony=True)
        with open(pdf_path, 'rb') as f:     
            p.pdf.delete()
            p.ps.delete()
            p.pdf.save(pdf_tail, File(f))
            p.podpisany = True
        p.save()
        w = p.wyniki.all()
        w.update(gotowy_do_hl7=True)
        if p.zlecenie.owner.drukowac_wyniki:
            shutil.move(pdf_path, settings.PDF_DOWYDRUKU)
        else:
            os.remove(pdf_path)
        return p

    def save_png_to_db(self, png_path, p):
        head, tail = os.path.split(png_path)
        with open(png_path, 'rb') as f:
            o = WynikPNG.objects.create(pdf=p)
            o.img.save(tail, File(f))
            o.save()
            os.remove(png_path)
            return o


            
class Worker:
    def __init__(self):
        self.ob = ObslugaBaz()
        self.dispatcher = Dispatcher()
        logger.debug('worker start')

    def wpisz_do_storm(self):
        a = self.ob.pobierz_replikacje_czynnosci()
        dodane = set()  # nie chce wrzucać zdublowanych wierszy do bazy
        do_usuniecia = []
        for task in a:
            id_wiersza = task.pop('id')
            task_json = json.dumps(task, default=str)
            if task_json in dodane:
                do_usuniecia.append(id_wiersza)
            else:
                rows = self.ob.replikuj_wiersz(task)
                for row in rows:
                    try:
                        getattr(self.dispatcher, row['mb_nazwa_tabeli'])(row)
                        logger.debug('Tabela: {tab} zadanie: {z}'.format(tab=row['mb_nazwa_tabeli'], z=row['mb_task']))
                        do_usuniecia.append(id_wiersza)
                        dodane.add(task_json)
                    except Exception as e:
                        logger.error('błąd: ', e)
        if do_usuniecia:
            self.ob.usun_replikacje_czynnosci(do_usuniecia)

    def przyjmij_ps(self):
        logger.debug('sprawdzam katalog ps')
        ps = PrzyjmijPS()
        # The continue statement, also borrowed from C, continues with the next iteration of the loop:
        files_ps = ps.get_files_name_in_order(ps.ps_in_path, '.ps')
        if files_ps:
            ps.clean_temp_files()
        for ps_path in files_ps:
            logger.debug('konweruje do pdf i png')
            ps.convert_to_png_and_pdf(ps_path)
            files_pdf = ps.get_files_name_in_order(ps.pdf_in_path, '.pdf')
            for pdf_path in files_pdf:
                nr_zlecenia, data_wydruku, autoryzujacy, lista_icd = ps.get_nr_zlecenia_i_data(pdf_path)
                if not nr_zlecenia:
                    continue
                try:
                    z = Zlecenie.objects.get(numer=nr_zlecenia)
                    u = autoryzujacy
                    p = ps.save_pdf_to_db(ps_path, pdf_path, data_wydruku, z, u)
                    pngs = ps.get_files_name_in_order(ps.img_in_path, '.png')
                    for png_path in pngs:
                        o = ps.save_png_to_db(png_path, p)
                    ps.przypisz_wyniki_do_pdf(lista_icd, data_wydruku, p, z)
                except Zlecenie.DoesNotExist:
                    pass

    def przyjmij_pdf(self):
        logger.debug('sprawdzam katalog pdf')
        pdf = PrzyjmijPS()
        # The continue statement, also borrowed from C, continues with the next iteration of the loop:
        files_pdf = pdf.get_pdf_files_name_in_order_wait(pdf.pdf_podpisany_path, '.pdf')
        for pdf_path in files_pdf:
            nr_zlecenia, data_wydruku, autoryzujacy, lista_icd = pdf.get_nr_zlecenia_i_data(pdf_path)
            if not nr_zlecenia:
                continue
            try:
                z = Zlecenie.objects.get(numer=nr_zlecenia)
                u = User.objects.get(username=autoryzujacy)
                p = pdf.save_podpisany_pdf_to_db(pdf_path, data_wydruku, z, u)
            except Zlecenie.DoesNotExist:
                pass


    def pracuj(self):      
        logger.debug('pracuje')
        self.wpisz_do_storm()
        self.przyjmij_ps()
        self.przyjmij_pdf()
        time.sleep(5)  # śpimy tutaj żeby pdfy zdążyły się podpisać

class Command(BaseCommand):
    help = 'Aktualizuje wszystkie zlecenia w bazie'
    def handle(self, *args, **options):
        w = Worker()
        while True:
            w.pracuj()
        



