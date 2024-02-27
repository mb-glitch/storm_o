import logging
import time

from django.core.management.base import BaseCommand
from aparaty.models import Wynik, Aparat, TestZnakowy
from aparaty.mssql import Mssql


# Get an instance of a logger
logger = logging.getLogger(__name__)
mssql = Mssql()

class Command(BaseCommand):
    help = ''
    PROFIL_MOCZU = 210

    def mssql_wstaw_wynik(self, wynik_as_dict):
        sqlcmd = mssql.mssql_sql_insert_wyniki
        sqlcmd = sqlcmd.format(**wynik_as_dict)     
        mssql._execute(sqlcmd, mssql.comdata)

    def wstaw_opis(self, numer_zlecenia):
        szablon_opisu = """
Barwa i przejrzystość:            {z1001}, {z1002}
{rbc:<33} {rbc_wynik}
{wbc:<33} {wbc_wynik}
{epi:<33} {epi_wynik}
{bac:<33} {bac_wynik}
{muc:<33} {muc_wynik}
"""

        sqlcmd = """select zlecenie_badania.ID_PACJENTA, zlecenie_badania.ID_ZLECENIA, probki.NR_WEWN 
        from zlecenie_badania 
        join probki on probki.ID_ZLECENIA = zlecenie_badania.ID_ZLECENIA 
        where zlecenie_badania.NUMER_ZLECENIA={numer_zlecenia}
        and probki.ID_PROFILU={profil}
        """     
        sqlcmd = sqlcmd.format(numer_zlecenia=numer_zlecenia, profil=self.PROFIL_MOCZU)
        dane = mssql._execute(sqlcmd)
        if dane:
            dane = dane[0]

            # pobieram wyniki opisowe dla zlecenia i wprowadzam je do szablonu opisu
            sqlcmd = """
            select WYNIKI_BADAN.ID_BADANIA, 
            WYNIKI_BADAN.WYNIK_ZN, 
            WARTOSCI_REFER.NA_WYDR, 
            WYNIKI_BADAN.FLAGA ,
            BADANIA.NAZWA_BADANIA
            from WYNIKI_BADAN
            left join WARTOSCI_REFER on WARTOSCI_REFER.ID_TABELI = WYNIKI_BADAN.ID_WARTOSCI_REF
            left join BADANIA on BADANIA.ID_BADANIA = WYNIKI_BADAN.ID_BADANIA
            WHERE ID_ZLECENIA = {id_zlecenia}
            """
            sqlcmd = sqlcmd.format(id_zlecenia=dane['ID_ZLECENIA'])
            wyniki = mssql._execute(sqlcmd)
            d = {}
            for w in wyniki:
                nazwa = 'n' + str(w['ID_BADANIA'])
                wynik_znakowy = 'z' + str(w['ID_BADANIA'])
                d[nazwa] = w['NAZWA_BADANIA']
                wz = w['WYNIK_ZN'] if w['WYNIK_ZN'] else ''
                if w['NAZWA_BADANIA'] in ['Barwa moczu', 'Przejrzystość moczu'] and not w['WYNIK_ZN']:
                    wz = 'nieoznaczona'
                d[wynik_znakowy] = wz
                d['na_wydruk'] = ''
            # rbc
            d['rbc'] = d['n937']
            try:
                rbc = float(d['z937'])
                if rbc == 0:
                    d['rbc_wynik'] = 'nieobecne w preparacie'
                elif rbc <= 1:
                    d['rbc_wynik'] = 'pojedyncze w preparacie'
                elif rbc <= 2:
                    d['rbc_wynik'] = '1 - 3 w polu widzenia'
                elif rbc <= 5:
                    d['rbc_wynik'] = '3 - 5 w polu widzenia'
                elif rbc <= 10:
                    d['rbc_wynik'] = '5 - 10 w polu widzenia'
                elif rbc <= 20:
                    d['rbc_wynik'] = '10 - 20 w polu widzenia'
                elif rbc <= 30:
                    d['rbc_wynik'] = '20 - 30 w polu widzenia'
                elif rbc <= 50:
                    d['rbc_wynik'] = '30 - 50 w polu widzenia'
                elif rbc <= 70:
                    d['rbc_wynik'] = '50 - 70 w polu widzenia'
                elif rbc <= 100:
                    d['rbc_wynik'] = '70 - 100 w polu widzenia'
                elif rbc > 100:
                    d['rbc_wynik'] = 'zalegają pole widzenia'
            except Exception as e:
                d['rbc_wynik'] = 'nieoznaczone'
                logger.error(e)
            # wbc
            d['wbc'] = d['n941']
            try:
                wbc = float(d['z941'])
                if wbc == 0:
                    d['wbc_wynik'] = 'nieobecne w preparacie'
                elif wbc <= 1:
                    d['wbc_wynik'] = 'pojedyncze w preparacie'
                elif wbc <= 2:
                    d['wbc_wynik'] = '1 - 3 w polu widzenia'
                elif wbc <= 5:
                    d['wbc_wynik'] = '3 - 5 w polu widzenia'
                elif wbc <= 10:
                    d['wbc_wynik'] = '5 - 10 w polu widzenia'
                elif wbc <= 20:
                    d['wbc_wynik'] = '10 - 20 w polu widzenia'
                elif wbc <= 30:
                    d['wbc_wynik'] = '20 - 30 w polu widzenia'
                elif wbc <= 50:
                    d['wbc_wynik'] = '30 - 50 w polu widzenia'
                elif wbc <= 70:
                    d['wbc_wynik'] = '50 - 70 w polu widzenia'
                elif wbc <= 100:
                    d['wbc_wynik'] = '70 - 100 w polu widzenia'
                elif wbc > 100:
                    d['wbc_wynik'] = 'zalegają pole widzenia'
            except Exception as e:
                d['wbc_wynik'] = 'nieoznaczone'
                logger.error(e)
            # epi
            d['epi'] = d['n973']
            try:
                epi = float(d['z973'])
                if epi == 0:
                    d['epi_wynik'] = 'nieobecne w preparacie'
                elif epi <= 1.12:
                    d['epi_wynik'] = 'pojedyncze w preparacie'
                elif epi <= 5.62:
                    d['epi_wynik'] = 'nieliczne w polu widzenia'
                elif epi <=16.87:
                    d['epi_wynik'] = 'dość liczne w polu widzenia'
                elif epi <=27:
                    d['epi_wynik'] = 'liczne w polu widzenia'
                elif epi > 27:
                    d['epi_wynik'] = 'bardzo liczne w polu widzenia'
            except Exception as e:
                d['epi_wynik'] = 'nieoznaczone'
                logger.error(e)
            # bac
            d['bac'] = d['n981']
            try:
                bac = float(d['z989']) + float(d['z993'])
                if bac == 0:
                    d['bac_wynik'] = 'nieobecne w preparacie'
                elif bac <= 29.25:
                    d['bac_wynik'] = 'pojedyncze w polu widzenia'
                elif bac <= 74.25:
                    d['bac_wynik'] = 'nieliczne w polu widzenia'
                elif bac <= 180:
                    d['bac_wynik'] = 'dość liczne w polu widzenia'
                elif bac <= 297:
                    d['bac_wynik'] = 'liczne w polu widzenia'
                elif bac > 297:
                    d['bac_wynik'] = 'bardzo liczne w polu widzenia'
            except Exception as e:
                d['bac_wynik'] = 'nieoznaczone'
                logger.error(e)
            # muc
            d['muc'] = d['n997']
            try:
                muc = float(d['z997'])
                if muc == 0:
                    d['muc_wynik'] = 'nieobecne w preparacie'
                elif muc <= 40:
                    d['muc_wynik'] = 'pojedyncze w polu widzenia'
                elif muc <= 101.2:
                    d['muc_wynik'] = 'nieliczne w polu widzenia'
                elif muc <= 180:
                    d['muc_wynik'] = 'dość liczne w polu widzenia'
                elif muc <= 247.5:
                    d['muc_wynik'] = 'liczne w polu widzenia'
                elif muc > 247.5:
                    d['muc_wynik'] = 'bardzo liczne w polu widzenia'
            except Exception as e:
                d['muc_wynik'] = 'nieoznaczone'
                logger.error(e)

            # pozycje fakultatywne - pojawiają się tylko kiedy są obecne
            # yea
            d['yea'] = d['n977']
            try:
                yea = float(d['z977'])
                if yea > 0:
                    szablon_opisu += '{yea:<33} {yea_wynik}\n'
                    if yea <= 0.67:
                        d['yea_wynik'] = 'pojedyncze w polu widzenia'
                    elif yea <= 2.25:
                        d['yea_wynik'] = 'nieliczne w polu widzenia'
                    elif yea <= 4.5:
                        d['yea_wynik'] = 'dość liczne w polu widzenia'
                    elif yea <= 11.25:
                        d['yea_wynik'] = 'liczne w polu widzenia'
                    elif yea > 11.25:
                        d['yea_wynik'] = 'bardzo liczne w polu widzenia'
            except Exception as e:
                logger.error(e)
            # nec
            d['nec'] = d['n969']
            try:
                nec = float(d['z969'])
                if nec > 0:
                    szablon_opisu += '{nec:<33} {nec_wynik}\n'
                    if nec <= 0.45:
                        d['nec_wynik'] = 'pojedyncze w polu widzenia'
                    elif nec <= 0.9:
                        d['nec_wynik'] = 'nieliczne w polu widzenia'
                    elif nec <= 1.8:
                        d['nec_wynik'] = 'dość liczne w polu widzenia'
                    elif nec > 1.8:
                        d['nec_wynik'] = 'liczne w polu widzenia'
            except Exception as e:
                logger.error(e)
            # caox
            d['caox'] = 'Kryształy szczawianu wapnia'
            try:
                caox = float(d['z953']) + float(d['z957'])
                if caox > 0:
                    szablon_opisu += '{caox:<33} {caox_wynik}\n'
                    if caox <= 1.35:
                        d['caox_wynik'] = 'pojedyncze w polu widzenia'
                    elif caox <= 4.05:
                        d['caox_wynik'] = 'nieliczne w polu widzenia'
                    elif caox <= 13.5:
                        d['caox_wynik'] = 'dość liczne w polu widzenia'
                    elif caox <= 29.7:
                        d['caox_wynik'] = 'liczne w polu widzenia'
                    elif caox > 29.7:
                        d['caox_wynik'] = 'bardzo liczne w polu widzenia'
            except Exception as e:
                logger.error(e)
            # uri
            d['uri'] = d['n1007']
            try:
                uri = float(d['z1007'])
                if uri > 0:
                    szablon_opisu += '{uri:<33} {uri_wynik}\n'
                    if uri <= 1.35:
                        d['uri_wynik'] = 'pojedyncze w polu widzenia'
                    elif uri <= 4.05:
                        d['uri_wynik'] = 'nieliczne w polu widzenia'
                    elif uri <= 13.5:
                        d['uri_wynik'] = 'dość liczne w polu widzenia'
                    elif uri <= 29.7:
                        d['uri_wynik'] = 'liczne w polu widzenia'
                    elif uri > 29.7:
                        d['uri_wynik'] = 'bardzo liczne w polu widzenia'
            except Exception as e:
                logger.error(e)
            # tri
            d['tri'] = d['n1003']
            try:
                tri = float(d['z1003'])
                if tri > 0:
                    szablon_opisu += '{tri:<45} {tri_wynik}\n'
                    if tri <= 1.35:
                        d['tri_wynik'] = 'pojedyncze w polu widzenia'
                    elif tri <= 4.05:
                        d['tri_wynik'] = 'nieliczne w polu widzenia'
                    elif tri <= 13.5:
                        d['tri_wynik'] = 'dość liczne w polu widzenia'
                    elif tri <= 29.7:
                        d['tri_wynik'] = 'liczne w polu widzenia'
                    elif tri > 29.7:
                        d['tri_wynik'] = 'bardzo liczne w polu widzenia'
            except Exception as e:
                logger.error(e)
            # hya
            d['hya'] = d['n961']
            try:
                hya = float(d['z961'])
                if hya > 0:
                    szablon_opisu += '{hya:<33} {hya_wynik}\n'
                    if hya <= 1:
                        d['hya_wynik'] = 'pojedyncze w polu widzenia'
                    elif hya <= 3:
                        d['hya_wynik'] = '1 - 3 w polu widzenia'
                    elif hya <= 5:
                        d['hya_wynik'] = '3 - 5 w polu widzenia'
                    elif hya <= 10:
                        d['hya_wynik'] = '5 - 10 w polu widzenia'
                    elif hya > 10:
                        d['hya_wynik'] = 'liczne w polu widzenia'
            except Exception as e:
                logger.error(e)
            # pat
            d['pat'] = d['n965']
            try:
                pat = float(d['z965'])
                if pat > 0:
                    szablon_opisu += '{pat:<33} {pat_wynik}\n'
                    if pat <= 1:
                        d['pat_wynik'] = 'pojedyncze w polu widzenia'
                    elif pat <= 3:
                        d['pat_wynik'] = '1 - 3 w polu widzenia'
                    elif pat <= 5:
                        d['pat_wynik'] = '3 - 5 w polu widzenia'
                    elif pat <= 10:
                        d['pat_wynik'] = '5 - 10 w polu widzenia'
                    elif pat > 10:
                        d['pat_wynik'] = 'liczne w polu widzenia'
            except Exception as e:
                logger.error(e)
            # uamo
            d['uamo'] = d['n1011']
            try:
                uamo = d['z1011']
                if uamo:
                    szablon_opisu += '{uamo:<33} {uamo_wynik}\n'
                    if uamo == '+':
                        d['uamo_wynik'] = 'pojedyncze w polu widzenia'
                    elif uamo == '++':
                        d['uamo_wynik'] = 'nieliczne w polu widzenia'
                    elif uamo == '+++':
                        d['uamo_wynik'] = 'liczne w polu widzenia'
                    elif uamo == '++++':
                        d['uamo_wynik'] = 'bardzo liczne w polu widzenia'
            except Exception as e:
                logger.error(e)
            # pamo
            d['pamo'] = d['n1015']
            try:
                pamo = d['z1015']
                if pamo:
                    szablon_opisu += '{pamo:<33} {pamo_wynik}\n'
                    if pamo == '+':
                        d['pamo_wynik'] = 'pojedyncze w polu widzenia'
                    elif pamo == '++':
                        d['pamo_wynik'] = 'nieliczne w polu widzenia'
                    elif pamo == '+++':
                        d['pamo_wynik'] = 'liczne w polu widzenia'
                    elif pamo == '++++':
                        d['pamo_wynik'] = 'bardzo liczne w polu widzenia'
            except Exception as e:
                logger.error(e)

           
            szablon_opisu = szablon_opisu.format(**d)
            # wstawiam opis do wyniu
            dane['ID_PROFILU'] = self.PROFIL_MOCZU
            dane['OPIS'] = szablon_opisu
            dane['ID_TABELI'] = ''  # ale wstawiam NULL, żeby było jak pozostałe
            sqlcmd = 'select * from WYNIKI_ODP where ID_ZLECENIA={ID_ZLECENIA} and ID_PACJENTA={ID_PACJENTA} and ID_PROFILU={ID_PROFILU} and NR_WEWN={NR_WEWN}' 
            sqlcmd = sqlcmd.format(**dane)
            opis = mssql._execute(sqlcmd)
            if opis:
                sqlcmd = "update WYNIKI_ODP set OPIS='{OPIS}' where ID_ZLECENIA={ID_ZLECENIA} and ID_PACJENTA={ID_PACJENTA} and ID_PROFILU={ID_PROFILU}"
                sqlcmd = sqlcmd.format(**dane)
                opis = mssql._execute(sqlcmd)
            else:
                sqlcmd = "insert into WYNIKI_ODP values ({ID_PROFILU}, '{OPIS}', {ID_PACJENTA}, NULL, {ID_ZLECENIA}, {NR_WEWN})"
                sqlcmd = sqlcmd.format(**dane)
                opis = mssql._execute(sqlcmd)

    
    
    def handle(self, *args, **options):
        aparat = Aparat.objects.get(nazwa='urised')
        while True:
            wyniki = Wynik.objects.filter(wyslany=False, test_znakowy__aparat=aparat)
            if wyniki:
                do_opisu = []
                for w in wyniki:
                    # wstawiam do bazy
                    self.mssql_wstaw_wynik(w.wynik_as_dict)
                    w.wyslany = True
                    w.save()
                    if w.pid not in do_opisu:
                        do_opisu.append(w.pid)
                # tworzę opis i wstawiam jak skończę
                time.sleep(10)  # czekam, żeby baza przetrawiła wszystkie wyniki i tworzę opis z selecta
                for numer_zlecenia in do_opisu:
                    self.wstaw_opis(numer_zlecenia)
            else:
                time.sleep(10)
