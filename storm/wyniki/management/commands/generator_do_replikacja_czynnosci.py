import pymssql
import json

from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.core.management.base import BaseCommand, CommandError


from wyniki.models import Zlecenie, Pacjent, Badanie, Wynik, WynikPDF, Kontrahent, WartosciReferencyjne, Badanie, GrupaBadan

class ObslugaBazBakter:
    bdl = {
    'server':'127.0.0.1',
    'port':11433,
    #'server':'192.168.0.128',
    #'port':1433,
    'user':'ADMIN',
    'password':'***',
    'database':'punktp',
    'charset':'cp1250'
    }
    ms = {
    'server':'192.168.2.110',
    'port':1433,
    'user':'ADMIN',
    'password':'***',
    'database':'lab3000',
    'charset':'cp1250'
    }
    pp =  {
    'server':'192.168.0.128',
    'port':1433,
    'user':'ADMIN',
    'password':'***',
    'database':'punktp',
    'charset':'cp1250'
    }



    def __init__(self):
        self.conn = pymssql.connect(**self.pp)
        # self.conn = pymssql.connect(**self.bdl)
        # self.conn = pymssql.connect(**self.ms)

    def insert_all(self, tabela, kolumna_id):
        sql = "select {tabela} from {kolumna_id}".format(tabela=tabela, kolumna_id=kolumna_id)
        with self.conn.cursor(as_dict=True) as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                sql = "insert into replikacja_czynnosci values ('{tabela}', '{kolumna_id}', {id}, 'i')"
                sql = sql.format(id=row[kolumna_id], tabela=tabela, kolumna_id=kolumna_id)
                cursor.execute(sql)
            self.conn.commit()


    def probki_insert_all(self):
        sql = "select ID_TABELI from probki"  # where ZLEC_W_CAL='T'"
        with self.conn.cursor(as_dict=True) as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                sql = "insert into replikacja_czynnosci values ('probki', 'ID_TABELI', {id}, 'i')"
                sql = sql.format(id=row['ID_TABELI'])
                cursor.execute(sql)
            self.conn.commit()

    def wyniki_insert_all(self):
        sql = "select ID_TABELI from WYNIKI_BADAN"  # where ZLEC_W_CAL='T'"
        with self.conn.cursor(as_dict=True) as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                sql = "insert into replikacja_czynnosci values ('WYNIKI_BADAN', 'ID_TABELI', {id}, 'i')"
                sql = sql.format(id=row['ID_TABELI'])
                cursor.execute(sql)
            self.conn.commit()

    def zlecenia_insert_all(self):
        sql = "select ID_ZLECENIA from zlecenie_badania"  # where ZLEC_W_CAL='T'"
        with self.conn.cursor(as_dict=True) as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                sql = "insert into replikacja_czynnosci values ('zlecenie_badania', 'ID_ZLECENIA', {id}, 'i')"
                sql = sql.format(id=row['ID_ZLECENIA'])
                cursor.execute(sql)
            self.conn.commit()

    def profile_insert_all(self):
        sql = "select ID_GRUPY from GRUPY_BADAN"  # where ZLEC_W_CAL='T'"
        with self.conn.cursor(as_dict=True) as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                sql = "insert into replikacja_czynnosci values ('GRUPY_BADAN', 'ID_GRUPY', {id}, 'i')"
                sql = sql.format(id=row['ID_GRUPY'])
                cursor.execute(sql)
            self.conn.commit()

    def profile_update_all(self):
        sql = "select ID_GRUPY from GRUPY_BADAN"  # where ZLEC_W_CAL='T'"
        with self.conn.cursor(as_dict=True) as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                sql = "insert into replikacja_czynnosci values ('GRUPY_BADAN', 'ID_GRUPY', {id}, 'u')"
                sql = sql.format(id=row['ID_GRUPY'])
                cursor.execute(sql)
            self.conn.commit()

    def wartosci_referencyjne(self):
        sql = "select ID_TABELI from WARTOSCI_REFER"
        with self.conn.cursor(as_dict=True) as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                sql = "insert into replikacja_czynnosci values ('WARTOSCI_REFER', 'ID_TABELI', {id}, 'i')"
                sql = sql.format(id=row['ID_TABELI'])
                cursor.execute(sql)
            self.conn.commit()

    
    def badania_insert_all(self):
        sql = 'select ID_BADANIA from BADANIA'
        with self.conn.cursor(as_dict=True) as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                sql = "insert into replikacja_czynnosci values ('BADANIA', 'ID_BADANIA', {id}, 'i')"
                sql = sql.format(id=row['ID_BADANIA'])
                cursor.execute(sql)
            self.conn.commit()

    def badania_update_all(self):
        sql = 'select ID_BADANIA from BADANIA'
        with self.conn.cursor(as_dict=True) as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                sql = "insert into replikacja_czynnosci values ('BADANIA', 'ID_BADANIA', {id}, 'u')"
                sql = sql.format(id=row['ID_BADANIA'])
                cursor.execute(sql)
            self.conn.commit()

    def badanie_profil_insert_all(self):
        sql = 'select ID_BADANIA, ID_PROFILU from badanie_profil'
        with self.conn.cursor(as_dict=True) as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                sql = "insert into replikacja_czynnosci values ('badanie_profil', 'ID_BADANIA', {id}, 'i')"
                sql = sql.format(id=row['ID_BADANIA'])
                cursor.execute(sql)
            self.conn.commit()

    def pacjenci_insert_all(self):
        sql = 'select ID_PACJENTA from PACJENCI order by ID_PACJENTA'
        with self.conn.cursor(as_dict=True) as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                sql = "insert into replikacja_czynnosci values ('PACJENCI', 'ID_PACJENTA', {id}, 'i')"
                sql = sql.format(id=row['ID_PACJENTA'])
                cursor.execute(sql)
            self.conn.commit()

    def pacjenci_update_all(self):
        sql = 'select ID_PACJENTA from PACJENCI order by ID_PACJENTA'
        with self.conn.cursor(as_dict=True) as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                sql = "insert into replikacja_czynnosci values ('PACJENCI', 'ID_PACJENTA', {id}, 'u')"
                sql = sql.format(id=row['ID_PACJENTA'])
                cursor.execute(sql)
            self.conn.commit()

    def kontrahent_insert_all(self):
        sql = 'select ID_PLATNIKA from platnik'
        with self.conn.cursor(as_dict=True) as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                sql = "insert into replikacja_czynnosci values ('platnik', 'ID_PLATNIKA', {id}, 'i')"
                sql = sql.format(id=row['ID_PLATNIKA'])
                cursor.execute(sql)
            self.conn.commit()

    def wprowadz_triggery_do_bazy(self):
        tabele = [('WYNIKI_BADAN', 'ID_TABELI'),
                 ]
        czynnosci = [('INSERT', 'i', 'inserted'),
                     ('UPDATE', 'u', 'inserted'),
                     ('DELETE', 'd', 'deleted')
                    ]
        sql_drop = '''
IF  EXISTS (SELECT * FROM sys.triggers WHERE object_id = OBJECT_ID(N'[dbo].[{t0}_after_{c1}]'))
DROP TRIGGER [dbo].[{t0}_after_{c1}]
'''
        sql_create = '''
CREATE TRIGGER [dbo].[{t0}_after_{c1}]
ON [dbo].[{t0}] 
FOR {c0} AS
insert replikacja_czynnosci
Select '{t0}', '{t1}', {t1}, '{c1}'
from {c2}
'''
        with self.conn.cursor(as_dict=True) as cursor:
            for t in tabele:
                for c in czynnosci:
                    sql = sql_drop.format(t0=t[0], c1=c[1])
                    cursor.execute(sql)
                    sql = sql_create.format(t0=t[0], t1=t[1], c0=c[0], c1=c[1], c2=c[2])
                    cursor.execute(sql)
            self.conn.commit()
                    



class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        Wynik.objects.all().delete()
        Badanie.objects.all().delete()
        GrupaBadan.objects.all().delete()
        
        WynikPDF.objects.all().delete()
        Zlecenie.objects.all().delete()
        #Pacjent.objects.all().delete()
        #WartosciReferencyjne.objects.all().delete()
        
        ob = ObslugaBazBakter()
        #ob.badania_update_all()
        #ob.profile_update_all()
        ob.badania_insert_all()
        ob.profile_insert_all()
        #ob.pacjenci_insert_all()
        #ob.pacjenci_update_all()
        #ob.kontrahent_insert_all()
        ob.badanie_profil_insert_all()
        #ob.wartosci_referencyjne()
        #ob.zlecenia_insert_all()
        #ob.wyniki_insert_all()
        #ob.probki_insert_all()



