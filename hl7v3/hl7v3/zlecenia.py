# -*- coding: utf-8 -*-
#
import datetime, time
import os
import re
import shutil
import logging
from bs4 import BeautifulSoup
import jinja2

from .obsluga_baz import ObslugaBaz

class Personel:
    def __init__(self):
        self.imie = None
        self.nazwisko = None
        self.pwz = None
        self.tytul = None


class Laboratorium:
    def __init__(self):
        self.nazwa = 'Laboratorium BDL'
        self.kod_pocztowy = '27-200'
        self.miasto = 'Starachowice'
        self.ulica = 'Radomska'
        self.ulica_numer = '35'
        self.lokal = None
        self.tel = '412741563'
        self.id_lab = 2  # LAB ANALITYKI MEDYCZNEJ
        self.id_miejsca_pobrania = 93  # MED-STAR 


class Wykonawca:
    ob = ObslugaBaz()

    def __init__(self):
        self.nazwa = 'Biglo Diagnostyka Laboratoryjna sp. z o.o.'
        self.rej_czesc_5 = '02'
        self.rej_nr = '0019619'
        self.regon_9 = '015594367'
        self.regon_14 = '01559436700024'
        self.lab = Laboratorium()
        self.osoba = Personel()
    
    def uzupelnij_z_bazy(self, row):
        self.osoba.imie = row['IMIE']
        self.osoba.nazwisko = row['NAZWISKO']
        self.osoba.pwz = row['PWZ']
        self.osoba.tytul = row['TYTUL_NAUKOWY']           


class Badanie:
    ob = ObslugaBaz()

    def __init__(self):
        self.icd = None
        self.id_badania = None
        self.id_grupy = None
        self.badanie_lp_wyd = None        
        self.grupa_lp_wyd = 99  # jakby nie było to lepiej tak
        self.nazwa = None
        self.pk = None
        self.obs_id = None
        self.data = None
        self.wynik_wartosc = None
        self.jednostka = None
        self.ref_min = None
        self.ref_max = None
        
        # jeżeli zlecone w całości to traktujemy jako profil
        self.oddzielny_profil = False  # profil dynamiczny potrzebuje oddzielnych zleceń
        self.zlecone_w_calosci = False
        self.badania = []

        self.code_system = None
        self.odbiorca = None
        self.display_name = None
        self.n_kod_badania = None
        self.n_kod_profilu = None
        self.n_zlecone_w_calosci = False

    def __lt__(self, other):
        return (self.grupa_lp_wyd, self.badanie_lp_wyd) < (other.grupa_lp_wyd, other.badanie_lp_wyd)

    def uzupelnij_info_grupa(self, row):
        self.zlecone_w_calosci = True
        self.icd = row.get('ICD', 'PROC1')
        self.kod_platnika = row.get('kod_platnika')
        self.nazwa = row['NAZWA_GRUPY']
        #self.pk = row['ID_TABELI']
        #self.data = row['DATA_WYNIKU']
        self.nr_zlecenia = row['NUMER_ZLECENIA']
        self.zlecenie_id = row['ID_ZLECENIA']
        self.platnik = row['ID_PLATNIKA']
        self.grupa = row['ID_GRUPY']
        self.grupa_lp_wyd = row['grupa_lp_wyd']

    def uzupelnij_info_badanie(self, row):
        self.icd = row.get('ICD', 'PROC1')
        self.kod_platnika = row['kod_platnika'] if row['kod_platnika'] else row['KOD_BADANIA']
        self.nazwa = row['NAZWA_BADANIA']
        if row['CZESTOTLIWOSC']:
            self.nazwa = '{nazwa} {opis}'.format(nazwa=row['NAZWA_BADANIA'], opis=row['CZESTOTLIWOSC'])
        self.pk = row['ID_TABELI']
        self.data = row['DATA_WYNIKU']
        self.wynik_wartosc = row['WYNIK_ZN']
        self.jednostka = row['JM'] if row['JM'] else ''
        self.flaga = row['FLAGA'] if row['FLAGA'] else ''
        self.ref_min = row['WARTOSC_OD'] if row['WARTOSC_OD'] else ''
        self.ref_max = row['WARTOSC_DO'] if row['WARTOSC_DO'] else ''
        self.wynik_data = row['DATA_WYNIKU'].strftime(os.getenv('CDA_FORMAT_CZASU'))
        self.nr_zlecenia = row['NUMER_ZLECENIA']
        self.badanie_lp_wyd = row['badanie_lp_wyd']


    @property
    def wynik_z_jednostkami(self):
        return '{wynik} {jednostka}'.format(wynik=self.wynik_wartosc, jednostka=self.jednostka)

    @property
    def zakres_referencyjny(self):
        return '{ref_min} - {ref_max}'.format(ref_min=self.ref_min, ref_max=self.ref_max)

    def zmapuj(self):
        sql =   "select "\
                "mb_mapowania.badanie, "\
                "mb_mapowania.grupa, "\
                "mb_mapowania.kod_platnika, "\
                "GRUPY_BADAN.PROF_DYN, "\
                "GRUPY_BADAN.LP_WYD as grupa_lp_wyd, "\
                "badanie_profil.LP_WYD as badanie_lp_wyd "\
                "from mb_mapowania "\
                "join GRUPY_BADAN on GRUPY_BADAN.ID_GRUPY = mb_mapowania.grupa "\
                "left join badanie_profil on badanie_profil.ID_BADANIA = mb_mapowania.badanie "\
                "and badanie_profil.ID_PROFILU = mb_mapowania.grupa "\
                "where mb_mapowania.kod_platnika='{kod}' "

        zmapowane = self.ob.select(sql.format(kod=self.icd))           
        if len(zmapowane) == 1:
            b = zmapowane[0]
            self.icd = b['kod_platnika']
            self.id_badania = b['badanie']
            if b['badanie'] == 0:  # dodałem do mapowań kod badania 0 jako oznaczenie grupy badań zlecanych w całości
                self.zlecone_w_calosci = True
            if b['PROF_DYN'] == 'T':
                self.oddzielny_profil = True  # wydaje mi sie że dolny elif len(zmapowane) > 1 jest niepotrzebny bo był na to inny pomysł
            self.id_grupy = b['grupa']
            self.badanie_lp_wyd = b['badanie_lp_wyd'] if b['badanie_lp_wyd'] else 99  # 99 to tak tylko dla niepożądku, może powinno być zero?  
            self.grupa_lp_wyd = b['grupa_lp_wyd'] if b['grupa_lp_wyd'] else 99  # 99 to tak tylko dla niepożądku, może powinno być zero?       
        

class Lekarz:
    ob = ObslugaBaz()

    def __init__(self):
        self.imie = None
        self.nazwisko = None
        self.pwz = None
        self.tytul = None
        self.pk = None

    def uzupelnij_z_bazy(self, row):
        self.imie = row['LEKARZ_IMIE']
        self.nazwisko = row['LEKARZ_NAZWISKO']
        self.pwz = row['LEKARZ_PWZ']
        self.tytul = row['LEKARZ_TYTUL_NAUKOWY']

    def zmapuj(self):
        row = self.ob.select("select ID_PERSONELU from dane_personelu where NR_SPECJALIZACJI = '{pwz}'".format(pwz=self.pwz))
        self.pk = row[0]['ID_PERSONELU']

class Pacjent:    
    ob = ObslugaBaz()
    logger = logging.getLogger(__name__)

    def __init__(self):  
        self.pk = ''
        self.imie = ''
        self.imie_drugie = ''
        self.nazwisko = ''
        self.pesel = ''
        self.plec = ''
        self.panstwo = ''
        self.miasto = ''
        self.ulica = ''
        self.kod_pocztowy = ''
        self.numer_domu = ''
        self.lokal = ''
        self.zmapowane = ''
        self.uwagi = ''

    def uzupelnij_z_bazy(self, row):
        self.pk = row['ID_PACJENTA']
        self.imie = row['IMIE']
        self.imie_drugie = ''
        self.nazwisko = row['NAZWISKO']
        self.pesel = row['PESEL'][:-1]
        if row['PLEC']=='M':
            self.plec = row['PLEC']
        elif row['PLEC']=='K':
            self.plec = 'F'
        self.panstwo = 'Polska'
        self.miasto = row['MIASTO']
        self.ulica = row['ULICA']
        self.kod_pocztowy = row['KOD_POCZTOWY']
        self.numer_domu = row['NR_DOMU']
        self.lokal = row['LOKAL']
        self.zmapowane = ''
    
    def zmapuj(self):
        sql = """
select ID_PACJENTA from PACJENCI 
where PESEL like ('{pesel} ')
and
NAZWISKO='{nazwisko}'
and
IMIE='{imie}'
and
MIEJSCE_ZAM = '{adres}'
"""
        self.adres = '{kod} {miasto}, {ulica} {numer_u}/{numer_m}'
        numer_m = '/' + self.lokal if self.lokal else ''
        self.adres = self.adres.format(kod=self.kod_pocztowy, miasto=self.miasto.title(),
                            ulica=self.ulica.title(), numer_u=self.numer_domu,
                            numer_m=self.lokal)
        sql = sql.format(pesel=self.pesel, adres=self.adres, 
                nazwisko=self.nazwisko, imie=self.imie)
        rows = self.ob.select(sql)
        self.logger.debug(rows)
        if len(rows) > 0:
            self.zmapowane = rows[0]['ID_PACJENTA']
        else:
            self.dodaj_pacjenta()

    @property
    def wiek(self):
        data_urodzenia_datetime = datetime.datetime.strptime(
                self.data_urodzenia_lab, os.getenv('FORMAT_CZASU_BAZA')
                )
        wiek = datetime.datetime.now() - data_urodzenia_datetime
        dni = wiek / datetime.timedelta(days=1)
        tygodni = wiek / datetime.timedelta(weeks=1)
        lat = dni / 365.2524  # średnio ile dni w roku
        
        if dni < 31:
            self.wsk_wiek = 'D'
            return int(dni)
        elif tygodni < 53:
            self.wsk_wiek = 'T'
            return int(tygodni)
        else:
            self.wsk_wiek = 'L'
            return int(lat)


    @property
    def data_urodzenia_lab(self):
        rok, msc, dzien = self.pesel[:2], self.pesel[2:4], self.pesel[4:6]
        msc = int(msc)
        if msc <= 12:
            rok = '19' + rok
        elif msc <= 32:
            msc = msc - 20
            rok = '20' + rok
        data_urodzenia = '{rok}-{msc}-{dzien} 00:00:00'.format(rok=rok, msc=msc, dzien=dzien)
        return data_urodzenia

    @property
    def data_urodzenia(self):
        rok, msc, dzien = self.pesel[:2], self.pesel[2:4], self.pesel[4:6]
        msc = int(msc)
        if msc <= 12:
            rok = '19' + rok
        elif msc <= 32:
            msc = msc - 20
            rok = '20' + rok
        data_urodzenia = '{rok}{msc}{dzien}'.format(rok=rok, msc=msc, dzien=dzien)
        return data_urodzenia

    def dodaj_pacjenta(self):        
        sql = """
declare @nr_pacjenta int
declare @id_pacjenta int
select @nr_pacjenta = max(NR_PACJENTA) + 1 from PACJENCI
select @id_pacjenta = max(ID_PACJENTA) + 1 from PACJENCI

begin
insert into PACJENCI (PESEL, NR_DOWODU, NAZWISKO, IMIE, DATA_URODZENIA, PLEC, MIEJSCE_ZAM, TYP_UBEZPIECZENIA, NUMER_UBEZPIECZENIA, RUM, ID_INSTYTUCJI_UBEZP, ID_PLATNIKA, ID_PACJENTA, NR_PACJENTA, INICJALY_PAC, KOD_PAC, ID_ODDZ_REJ, NR_HCH, OS_WPROWADZAJACA, DATA_WPROWADZENIA, NIP, GRUPA_KRWI, RH, POPRZEDNIE_NAZWISKO, DATA_MODYFIKACJI, ID_OSOBY_MODYF, KOD_POCZTOWY, MIASTO, NR_DOMU, ULICA, ID_SZPITALA, EMAIL, PACJENT_BAD_SRODOW, VIP)
    values ('{pesel}', NULL, '{nazwisko}', '{imie}', '{data_urodzenia}', '{plec}', '{adres}', NULL, NULL, NULL, NULL, NULL, @id_pacjenta, @nr_pacjenta, NULL, NULL, NULL, NULL, '{wprowadzajacy}', '{created}', NULL, NULL, NULL, NULL, NULL, NULL, '{kod_pocztowy}', '{miasto}', '{numer_domu}', '{ulica}', NULL, NULL, NULL, NULL)
end
"""
        sql = sql.format(pesel=self.pesel,
                    nazwisko=self.nazwisko,
                    imie=self.imie,
                    data_urodzenia=self.data_urodzenia_lab,
                    plec=self.plec,
                    adres=self.adres,
                    wprowadzajacy=os.getenv('PERSONEL_ID_SYSTEM'),
                    created=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    kod_pocztowy=self.kod_pocztowy,
                    miasto=self.miasto,
                    numer_domu=self.numer_domu,
                    ulica=self.ulica
                    )
        self.ob.insert(sql)
        self.zmapuj()

class Zleceniodawca:
    def __init__(self):
        self.pk = 99  # id_platnika zrób zmapuj
        self.nazwa = None
        self.oddzial = None
        self.oddzial_kod = 9128  # kod MED-STAR?  # kod oddziału na podstawie księgi rejesrowej zrób zmapuj
        self.regon_9 = None
        self.regon_14 = None
        self.panstwo = None
        self.miasto = None
        self.ulica = None
        self.kod_pocztowy = None
        self.numer_domu = None
        self.numer_mieszkania = None
        self.czesc_7_nazwa = None
        self.czesc_7_nr = None
        self.czesc_8_nazwa = None
        self.czesc_8_nr = None

    def uzupelnij_z_bazy(self, row):
        self.nazwa = row['PELNA_NAZWA_PLATNIKA']
        self.oddzial = row['NAZWA_ODDZIALU']
        self.oddzial_kod = ''  # None
        self.regon_9 = row['REGON']
        self.regon_14 = 26007678600029
        self.panstwo = 'Polska'
        self.miasto = ''  # row['']
        self.ulica = ''  # row['']row['']
        self.kod_pocztowy = ''  # row['']row['']
        self.numer_domu = ''  # row['']row['']
        self.numer_mieszkania = ''  # row['']row['']
        self.czesc_7_nazwa = ''  # row['']row['']
        self.czesc_7_nr = row['SYGNATURA']
        self.czesc_8_nazwa = None
        self.czesc_8_nr = None


class Zlecenie:
    ob = ObslugaBaz()

    def __init__(self):
        # ustawiam czas
        self.now = datetime.datetime.now()
        self.now_str = self.now.strftime(os.getenv('CDA_FORMAT_CZASU'))
        self.now_str_do_db = self.now.strftime(os.getenv('FORMAT_CZASU_BAZA'))
        self.jutro = datetime.datetime.today() + datetime.timedelta(days=1)
        self.jutro_str_do_db = self.jutro.strftime(os.getenv('FORMAT_CZASU_BAZA'))
        self.zlecenia_nr = []  # może być wiecej niż jedno
        self.zlecenia_id = []  # może być wiecej niż jedno        
        self.pacjent = None
        self.lekarz = None
        self.zleceniodawca = None
        self.wykonawca = Wykonawca()
        self.badania = []
        self.badania_str = []  # lista str do wpisania badań do bazy (oddzielnie dla każdego testu dynamicznego)


class ZlecenieExport(Zlecenie):
    obs_id = 1
    res_id = None

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.rejestracja_data = None
        self.pobranie_data = None
        self.odprawienie_data = None
        self.dokument_data = self.now_str
        self.wydruk_data = self.now_str
        self.wersja = 1  # jeżeli dokument będzie anulowany i wydany powtórnie to trzeba zwiększyć
         
    def pobierz_obs_id(self):
        obs = self.obs_id
        self.obs_id += 1        
        return obs
    
    def pobierz_res_id(self):
        return 1

    def analizuj_zlecenie(self, nr_sys_zleceniodawcy):  # nr referencyjny odnosi się do zlecenia (połączyć wszystkie nasze numery w jeden)
        self.nr_sys_zleceniodawcy = nr_sys_zleceniodawcy
        self.pobierz_zlecenie_info(nr_sys_zleceniodawcy)
        self.pobierz_badania()

    def pobierz_badania(self):

    # grupy badań
        sql_gr = """
    select distinct
    GRUPY_BADAN.NAZWA_GRUPY,
    GRUPY_BADAN.NR_PROC1 as ICD,
    GRUPY_BADAN.ZLEC_W_CAL,
    GRUPY_BADAN.ID_GRUPY,
    probki.ILOSC_WYKONAN,
    probki.DATA_ODPRAWIENIA,
    dane_personelu.NAZWISKO,
    dane_personelu.IMIE,
    dane_personelu.NR_SPECJALIZACJI as PWZ,
    dane_personelu.TYTUL_NAUKOWY,
    listamaterialow.NAZWA as NAZWA_MATERIALU,
    posiew_master.ID_MASTER_POSIEW,
    zlecenie_badania.ID_ZLECENIA,
    zlecenie_badania.NUMER_ZLECENIA,
    platnik.ID_PLATNIKA, 
    platnik.NAZWA_PLATNIKA,
    platnik.REGON,
    oddzialy.NAZWA_ODDZIALU,
    GRUPY_BADAN.LP_WYD as grupa_lp_wyd
    from zlecenie_badania
    join platnik on platnik.ID_PLATNIKA = zlecenie_badania.ID_PLATNIKA
    join oddzialy on oddzialy.ID_ODDZIALU = zlecenie_badania.ID_ODDZIALU
    join probki on zlecenie_badania.ID_ZLECENIA = probki.ID_ZLECENIA
    join GRUPY_BADAN on GRUPY_BADAN.ID_GRUPY = probki.ID_PROFILU
    join dane_personelu on dane_personelu.ID_PERSONELU = probki.ID_ODPRAWIAJACEGO
    full outer join listamaterialow on probki.KOD_MATERIALU = listamaterialow.KOD
    full outer join posiew_master on zlecenie_badania.ID_ZLECENIA = posiew_master.ID_ZLECENIA
    where
    zlecenie_badania.ID_ZLECENIA in ({})
    and
    probki.PROF_ODPRAWIONY = 'T'
    """

    # badania
        sql_bad = """
    select distinct
    BADANIA.NAZWA_BADANIA,
    BADANIA.KOD_BADANIA,
    BADANIA.NR_PROC1 as ICD,
    BADANIA.JM,
    WYNIKI_BADAN.ID_TABELI,
    WYNIKI_BADAN.ILOSC_WYKONAN,
    WYNIKI_BADAN.WYNIK_ZN,
    WYNIKI_BADAN.DATA_WYNIKU,
    WYNIKI_BADAN.FLAGA,
    WARTOSCI_REFER.WARTOSC_OD,
    WARTOSCI_REFER.WARTOSC_DO,
    listamaterialow.NAZWA as NAZWA_MATERIALU,
    zlecenie_badania.NUMER_ZLECENIA,
    posiew_master.ID_MASTER_POSIEW,
    mb_mapowania.kod_platnika,
    badanie_profil.LP_WYD as badanie_lp_wyd,
    test_dynamiczny.CZESTOTLIWOSC
    from WYNIKI_BADAN
    left outer join WARTOSCI_REFER on WYNIKI_BADAN.ID_WARTOSCI_REF = WARTOSCI_REFER.ID_TABELI
    join zlecenie_badania on zlecenie_badania.ID_ZLECENIA = WYNIKI_BADAN.ID_ZLECENIA
    join platnik on platnik.ID_PLATNIKA = zlecenie_badania.ID_PLATNIKA
    join probki on WYNIKI_BADAN.ID_ZLECENIA = probki.ID_ZLECENIA
    and WYNIKI_BADAN.ID_PROFILU = probki.ID_PROFILU
    join GRUPY_BADAN on GRUPY_BADAN.ID_GRUPY = probki.ID_PROFILU
    join BADANIA on BADANIA.ID_BADANIA = WYNIKI_BADAN.ID_BADANIA
    full outer join listamaterialow on probki.KOD_MATERIALU = listamaterialow.KOD
    full outer join posiew_master on zlecenie_badania.ID_ZLECENIA = posiew_master.ID_ZLECENIA
    full outer join test_dynamiczny on WYNIKI_BADAN.ID_TAB_TEST_DYN = test_dynamiczny.ID_TABELI
    left join mb_mapowania on WYNIKI_BADAN.ID_BADANIA = mb_mapowania.badanie
    and probki.ID_PROFILU = mb_mapowania.grupa
    and platnik.ID_PLATNIKA = mb_mapowania.platnik
    left join badanie_profil on badanie_profil.ID_BADANIA = WYNIKI_BADAN.ID_BADANIA
    and badanie_profil.ID_PROFILU = GRUPY_BADAN.ID_GRUPY
    where
    probki.ID_ZLECENIA = '{zlecenie_id}'
    and
    probki.ID_PROFILU = '{grupa_id}'
"""



        zlecenie_id_list = ', '.join(map(str, self.zlecenia_id))
        grupy_badan = self.ob.select(sql_gr.format(zlecenie_id_list))
        for grupa in grupy_badan:
            self.wykonawca.uzupelnij_z_bazy(grupa)
            if grupa['ZLEC_W_CAL'] == 'T':
                g = Badanie()
                g.uzupelnij_info_grupa(grupa)
                g.obs_id = self.pobierz_obs_id
                g.kod_platnika = self.ob.select('select kod_platnika from mb_mapowania where mb_mapowania.platnik={platnik} and mb_mapowania.grupa={grupa}'.format(platnik=g.platnik, grupa=g.grupa))
                g.kod_platnika = g.kod_platnika[0]['kod_platnika']  # ten potworek pobiera kod płatnika dla grupy zlecanej w całości
                g.opis = self.ob.select('select OPIS from WYNIKI_ODP where WYNIKI_ODP.ID_ZLECENIA={zlecenie} and WYNIKI_ODP.ID_PROFILU={grupa}'.format(zlecenie=g.zlecenie_id, grupa=g.grupa))  
                g.opis = g.opis[0]['OPIS'] if g.opis else None  # ten potworek pobiera OPIS dla grupy zlecanej w całości
                badania_grupy = self.ob.select(sql_bad.format(grupa_id=grupa['ID_GRUPY'], zlecenie_id=grupa['ID_ZLECENIA']))
                for badanie in badania_grupy:
                    b = Badanie()
                    b.uzupelnij_info_badanie(badanie)
                    b.obs_id = self.pobierz_obs_id()
                    g.badania.append(b)
                self.badania.append(g)
            elif grupa['ZLEC_W_CAL'] == 'N':
                badania_grupy = self.ob.select(sql_bad.format(grupa_id=grupa['ID_GRUPY'], zlecenie_id=grupa['ID_ZLECENIA']))
                for badanie in badania_grupy:
                    b = Badanie()
                    b.uzupelnij_info_badanie(badanie)
                    b.obs_id = self.pobierz_obs_id()
                    self.badania.append(b)
            self.badania.sort()  # powinno posortować kolejność badań w wyniku
            for badanie in self.badania:
                badanie.badania.sort()
            
        

    def pobierz_zlecenie_info(self, nr_sys_zleceniodawcy):
        sql = """
select distinct
oddzialy.NAZWA_ODDZIALU,
oddzialy.ID_ODDZIALU,
oddzialy.SYGNATURA,
zlecenie_badania.DATA_ZLECENIA,
probki.DATA_POBRANIA,
zlecenie_badania.NUMER_ZLECENIA,
zlecenie_badania.ID_ZLECENIA,
PACJENCI.ID_PACJENTA,
PACJENCI.NAZWISKO,
PACJENCI.IMIE,
PACJENCI.PESEL,
PACJENCI.DATA_URODZENIA,
PACJENCI.PLEC,
PACJENCI.KOD_POCZTOWY,
PACJENCI.NR_DOMU,
PACJENCI.ULICA,
PACJENCI.MIASTO,
PACJENCI.LOKAL,
PACJENCI.MIEJSCE_ZAM,
dane_personelu.NAZWISKO as LEKARZ_NAZWISKO,
dane_personelu.IMIE as LEKARZ_IMIE,
dane_personelu.NR_SPECJALIZACJI as LEKARZ_PWZ,
dane_personelu.TYTUL_NAUKOWY as LEKARZ_TYTUL_NAUKOWY,
platnik.PELNA_NAZWA_PLATNIKA,
platnik.ID_PLATNIKA,
platnik.REGON

from zlecenie_badania

join PACJENCI ON PACJENCI.ID_PACJENTA = zlecenie_badania.ID_PACJENTA
join dane_personelu on dane_personelu.ID_PERSONELU = zlecenie_badania.LEKARZ_ZLECAJACY
join oddzialy on oddzialy.ID_ODDZIALU = zlecenie_badania.ID_ODDZIALU
join probki on zlecenie_badania.ID_ZLECENIA = probki.ID_ZLECENIA
join platnik on zlecenie_badania.ID_PLATNIKA = platnik.ID_PLATNIKA
where zlecenie_badania.NR_REF = '{nr_sys_zleceniodawcy}'
"""

        rows = self.ob.select(sql.format(nr_sys_zleceniodawcy=nr_sys_zleceniodawcy))
        for idx, row in enumerate(rows):             
            self.zlecenia_nr.append(row['NUMER_ZLECENIA'])
            self.zlecenia_id.append(row['ID_ZLECENIA'])
            self.numer_zlecenia = row['NUMER_ZLECENIA']
            if idx == 0:
                # TODO jeszcze podzielić na próbki !
                self.rejestracja_data = row['DATA_ZLECENIA']
                self.pobranie_data = row['DATA_POBRANIA']
                # self.odprawienie_data = row['NUMER_ZLECENIA']

                self.numer_dokumentu = ''  # numer identyfikacjyny dokumentu cda
                self.numer_zleceniodawcy = nr_sys_zleceniodawcy
                self.numer_zleceniodawcy_str = str(self.numer_zleceniodawcy).zfill(20)

                self.dokument_data = self.now_str
                self.pacjent = Pacjent()
                self.pacjent.uzupelnij_z_bazy(row)
                self.lekarz = Lekarz()
                self.lekarz.uzupelnij_z_bazy(row)
                self.zleceniodawca = Zleceniodawca()
                self.zleceniodawca.uzupelnij_z_bazy(row)

    def generuj(self):
        def kolejny_numer():
            lista_plikow = os.listdir('media/wyniki_nowe/')
            lista_plikow += os.listdir('media/wyniki_archiwum/')
            lista_numerow = []
            for fn in lista_plikow:
                try:
                    lista_numerow.append(int(re.search('(\d+)\.res$', fn).group(1)))
                except Exception as e:
                    #self.logger.debug(e)
                    pass
            return max(lista_numerow) + 1
        
        def render(tpl_path, context):
            path, filename = os.path.split(tpl_path)
            return jinja2.Environment(
                loader=jinja2.FileSystemLoader(path or './')
            ).get_template(filename).render(context)  
        nr = kolejny_numer()
        self.numer_dokumentu = nr
        context = {
            'zlecenie': self
        }
        result = render('templates/sprawozdanie.res', context)
        nazwa_pliku = 'media/wyniki_nowe/LAB_{now}-{nr}.res'.format(now=self.now_str, nr=nr)
        with open(nazwa_pliku, 'w') as f:
            f.write(result)
        

class ZlecenieImport(Zlecenie):
    def __init__(self, path):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.zarejestrowane = False
        self.problem = False
        self.path = path

    def analizuj(self):
        with open(self.path) as fxml:
            # wrzucam xml do parsera
            self.soup = BeautifulSoup(fxml.read(), 'xml')
        self.cda = self.soup.ClinicalDocument
        self.logger.debug('pobieram pacjenta')
        self.pobierz_pacjenta()
        self.logger.debug('pobieram lekarza')
        self.pobierz_lekarza()
        self.logger.debug('pobieram zleceniodawce')
        self.pobierz_zleceniodawce()
        self.logger.debug('pobieram badania')
        self.pobierz_badania()
        self.logger.debug('pobieram zlecenie_info')
        self.pobierz_zlecenie_info()
        self.logger.debug('tworzę str z badaniami')
        self.stworz_str_badan()
        self.logger.debug('rejestruje zlecenie')
        for badania_str in self.badania_str:
            self.logger.debug(badania_str)
            self.zarejestruj_zlecenie(badania_str)
        if self.zarejestrowane and not self.problem:
            self.przenies_do_archiwum()

    def pobierz_lekarza(self):
        self.lekarz = Lekarz()
        self.lek = self.cda.author.assignedAuthor
        self.lekarz.imie = self.lek.find('given').text
        self.lekarz.nazwisko = self.lek.find('family').text
        self.lekarz.pwz = self.lek.find('id')['extension'] 
        self.lekarz.zmapuj()

    def pobierz_pacjenta(self):
        self.pacjent = Pacjent()
        self.pac = self.cda.recordTarget.patientRole
        if self.pac.patient.guardian:
            # g = self.pac.patient.guardian
            # self.guardian = Pacjent()
            # self.guardian.imie = g.find('given').text
            # self.guardian.nazwisko = g.find('family').text
            # pesel = g.find('id')['extension'] if g.find('id') else ''
            # self.guardian.pesel = g.find('id')['extension']
            # plec = g.find('administrativeGenderCode')['code'] if g.find('administrativeGenderCode') else 'K'
            # self.guardian.plec = plec if self.guardian.imie.upper().endswith('A') else 'M'
            # self.guardian.panstwo = g.find('country').text
            # self.guardian.miasto = g.find('city').text
            # self.guardian.ulica = g.find('streetName').text
            # self.guardian.kod_pocztowy = g.find('postalCode').text
            # self.guardian.numer_domu = g.find('houseNumber').text
            # self.guardian.lokal = g.find('unitID').text
            # self.guardian.zmapuj()
            self.logger.debug('########################################## w zleceniu był opiekun ##########################################')
            self.pac.patient.guardian.decompose()  # usuwa z zupy cały tag guardian
        self.pacjent.imie = self.pac.find('given').text
        self.pacjent.nazwisko = self.pac.find('family').text
        pesel = self.pac.find('id')['extension'] if self.pac.find('id') else ''
        self.pacjent.pesel = pesel
        plec = self.pac.find('administrativeGenderCode')['code'] if self.pac.find('administrativeGenderCode') else 'K'
        self.pacjent.plec = plec if self.pacjent.imie.upper().endswith('A') else 'M'
        self.pacjent.panstwo = self.pac.find('country').text
        self.pacjent.miasto = self.pac.find('city').text
        self.pacjent.ulica = self.pac.find('streetName').text
        self.pacjent.kod_pocztowy = self.pac.find('postalCode').text
        self.pacjent.numer_domu = self.pac.find('houseNumber').text
        self.pacjent.lokal = self.pac.find('unitID').text
        self.pacjent.zmapuj()

    def pobierz_zleceniodawce(self):
        self.zleceniodawca = Zleceniodawca()
        self.zlecd = self.cda.custodian
        self.zleceniodawca.nazwa = self.zlecd.find('name').text
        self.zleceniodawca.regon = self.zlecd.find(root='2.16.840.1.113883.3.4424.2.2')['extension']        
        self.zleceniodawca.pk = 99  # wpisuje na sztywno kod med-staru
        self.zleceniodawca.oddzial = self.zlecd.find(root='2.16.840.1.113883.3.4424.2.3.3')['extension']
        self.zleceniodawca.oddzial_kod = self.ob.select('select ID_ODDZIALU from oddzialy where SYGNATURA={kod}'.format(kod=self.zleceniodawca.oddzial))
        self.zleceniodawca.oddzial_kod = self.zleceniodawca.oddzial_kod[0]['ID_ODDZIALU']
        self.zleceniodawca.panstwo = self.zlecd.find('country').text
        self.zleceniodawca.miasto = self.zlecd.find('city').text
        self.zleceniodawca.ulica = self.zlecd.find('streetName').text
        self.zleceniodawca.kod_pocztowy = self.zlecd.find('postalCode').text
        #self.zleceniodawca.numer_domu = self.zlecd.find('houseNumber').text
        #self.zleceniodawca.numer_mieszkania = self.zlecd.find('unitID').text

    def pobierz_badania(self):
        self.badania = []
        #self.bad = self.cda.component.structuredBody.component.section.entry
        #self.bad = self.bad.find_all('observation')
        self.bad = self.cda.component.structuredBody.component.section
        entry = self.bad.find_all('observation')
        for b in entry:
            badanie = Badanie()
            badanie.icd = b.code['code']
            badanie.code_system = b.code['codeSystem']
            badanie.odbiorca = b.code['codeSystemName']
            badanie.display_name = b.code['displayName']
            badanie.zmapuj()
            # self.logger.debug('badanie')
            # self.logger.debug(badanie)  
            self.badania.append(badanie)

    def pobierz_zlecenie_info(self):
        self.nr_sys_zleceniodawcy = self.cda.id['extension'] 
        self.data_zlecenia_cda = self.cda.effectiveTime['value'] 
        self.data_zlecenia_cda_datetime = datetime.datetime.strptime(
                self.data_zlecenia_cda, os.getenv('CDA_FORMAT_CZASU')
                )
        self.data_zlecenia_db = self.data_zlecenia_cda_datetime.strftime(os.getenv('FORMAT_CZASU_BAZA'))
        self.rok = str(self.data_zlecenia_cda_datetime.year)
        self.miesiac = str(self.data_zlecenia_cda_datetime.month)

    def przenies_do_archiwum(self):
        rok = self.rok
        miesiac = self.miesiac.zfill(2)
        now = self.now_str
        head, tail = os.path.split(self.path)
        tail = tail.replace('.ord', '_{now}.ord'.format(now=now))
        dest_folder = os.path.join(os.getenv('KATALOG_ARCHIWUM_ZLECEN'), rok, miesiac)
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)
        dest = os.path.join(dest_folder, tail)
        shutil.move(self.path, dest)   

    def ustal_numer_zlecenia(self):
        n = self.ob.select('select top 1 NUMER_ZLECENIA from zlecenie_badania where NUMER_ZLECENIA < 10000 order by NUMER_ZLECENIA desc') 
        n = n[0]['NUMER_ZLECENIA'] + 1 if n else 1 
        # TODO jeżeli numeracja dochodzi do 10000 to skasować najstarsze zlecenia i zacząć od początku
        return n

    def stworz_str_badan(self):
        # badania_str_example = '57-13,3,|'
        badania_str = ''
        # sortuje po kolejności rejestracji grup i badań def __lt__
        for badanie in sorted(self.badania):
            self.logger.debug('grupa: {grupa}    badanie: {badanie}'.format(grupa=badanie.grupa_lp_wyd, badanie=badanie.badanie_lp_wyd))
            if badanie.oddzielny_profil:
                if badanie.id_grupy == 78:  # glukoza krzywa
                    bs = '78-18,19,20,21,22,|'  # 18 na czczo, 19 30', 20 60', 21 90', 22 120'
                    self.logger.debug(bs) 
                    self.badania_str.append(bs)
            else:
                if badania_str:
                    # znacznik | na końcu badań grupy
                    badania_str += '|'
                badania_str += '{grupa}-'.format(grupa=badanie.id_grupy)
                if badanie.zlecone_w_calosci:
                    pass
                else:
                    badania_str += '{badanie},'.format(badanie=badanie.id_badania)
        if badania_str:
            # znacznik | na końcu wszystkiego
            badania_str += '|'
            self.logger.debug(badania_str) 
            self.badania_str.append(badania_str)

    def zarejestruj_zlecenie(self, badania_str):
        lista = []
        lista.append('')  # komunikat,
        lista.append(self.ustal_numer_zlecenia())  # nr_zlecenia,
        lista.append(None)  # id_zlecenia,
        lista.append(self.wykonawca.lab.id_lab)  # id_laboratorium,
        lista.append(badania_str)  # badania,   #badania = '57-1,2,3,4,|7-|'
        lista.append('N')  # test_kliniczny,
        lista.append(None)  # test_id_proby,
        lista.append(None)  # test_nr_wizyty,
        lista.append(self.pacjent.zmapowane)  # id_pacjenta,
        lista.append(self.data_zlecenia_db)  # data_zlecenia,
        lista.append(self.zleceniodawca.oddzial_kod)  # id_oddzialu,
        lista.append(None)  # waga,
        lista.append(None)  # dzien_cyklu,
        lista.append(int(self.rok))  # rok,
        lista.append(int(os.getenv('PERSONEL_ID_SYSTEM')))  # id_pracownika,
        lista.append(None)  # na_czczo,
        lista.append(self.lekarz.pk)  # id_lekarza_zlecajacego,
        lista.append(None)  # data_rozp_krw,
        lista.append(None)  # obj_moczu,
        lista.append(None)  # okres_zbiorki,
        lista.append(None)  # rozpoznanie,
        lista.append(None)  # podawane_leki,
        lista.append(None)  # wzrost,
        lista.append(self.pacjent.wiek)  # wiek,
        lista.append(self.pacjent.wsk_wiek)  # wsk_wiek,
        lista.append(self.pacjent.uwagi)  # uwagi,
        lista.append(self.wykonawca.lab.id_lab)  # id_lab_zlec,
        lista.append(self.wykonawca.lab.id_miejsca_pobrania)  # id_miejsca_pob,
        lista.append(self.zleceniodawca.pk)  # id_platnika,
        lista.append(None)  # faza_cyklu,
        lista.append(None)  # palacy,
        lista.append(None)  # ciaza,
        lista.append(None)  # nr_hch, ma 20 znaków więc można go wykożystać jako nr_sys_zleceniodawcy
        lista.append(None)  # id_osrodka,
        lista.append(None)  # id_zlecenia_cl,
        lista.append(None)  # data_rejestracji_cl,
        lista.append(None)  # cl_kod_odcinka,
        lista.append('R')  # tryb_zlecenia,
        lista.append(self.jutro_str_do_db)  # zlecenie_na_dzien,
        lista.append('WS')  # sp_wydania_wydr
        self.logger.debug(lista)
        self.zarejestrowane = self.ob.wstaw_zlecenie(lista, self.nr_sys_zleceniodawcy)
        if not self.zarejestrowane:
            self.problem = True
