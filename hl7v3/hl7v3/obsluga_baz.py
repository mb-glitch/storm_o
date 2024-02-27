# -*- coding: utf-8 -*-
#

import os
import datetime
import pymssql
import logging

class ObslugaBaz:
    logger = logging.getLogger(__name__)
    # configuracja baz
    ms = {
    'server':'192.168.2.110',
    'port':1433,
    'user':'ADMIN',
    'password':'***',
    'database':'lab3000',
    'charset':'cp1250'
    }

    pp = {
    'server':'192.168.0.128',
    'port':1433,
    'user':'ADMIN',
    'password':'***',
    'database':'punktp',
    'charset':'cp1250'
    }

    pp_remote = {
    'server':'127.0.0.1',
    'port':11433,
    'user':'ADMIN',
    'password':'***',
    'database':'punktp',
    'charset':'cp1250'
    }
    db = pp

    #def __init__(self):

    def select(self, sql):
        try:
            with pymssql.connect(**self.db) as conn:
                with conn.cursor(as_dict=True) as cursor:
                    self.logger.debug('ob select: {sql}'.format(sql=sql))
                    cursor.execute(sql)
                    rows = cursor.fetchall()
                    self.logger.debug('ob select: {rows}'.format(rows=rows))
                    return rows
        except Exception as e:
            self.logger.error(e)

    def insert(self, sql):
        try:
            with pymssql.connect(**self.db) as conn:
                with conn.cursor(as_dict=True) as cursor:
                    self.logger.debug('ob insert: {sql}'.format(sql=sql))
                    cursor.execute(sql)
                    conn.commit()
        except Exception as e:
            self.logger.error(e)

    def wstaw_zlecenie(self, lista, nr_ref):
        try:
            with pymssql.connect(**self.db) as conn:
                with conn.cursor(as_dict=True) as cursor:
                    sql = "update zlecenie_badania set NR_REF='{nr_ref}' where NUMER_ZLECENIA={nr_zlec}"
                    sql = sql.format(nr_ref=nr_ref, nr_zlec=lista[1])
                    # uwaga trzeba usunąć z procedury procWstawZlecenie tworzenie daty pobrania, bo daje błąd
                    cursor.callproc('procWstawZlecenie2', (lista))
                    cursor.execute(sql)
                    conn.commit()
                    return True
        except Exception as e:
            self.logger.error(e)

    def przenies_nieprzyjete_na_jutro(self):
        dzis = datetime.date.today()
        jutro = dzis + datetime.timedelta(days=1)
        miec_temu_2 = dzis - datetime.timedelta(days=60)
        jutro = jutro.strftime(os.getenv('FORMAT_CZASU_BAZA'))
        dawno = datetime.date(2001, 1, 1)
        sql = "update zlecenie_badania set ZLECENIE_NA_DZIEN=CAST('{jutro}' as datetime) "\
              "where NUMER_ZLECENIA < 10000 "\
              "and ZREALIZOWANE='N' and WYKONANE='N'"\
              "and DATA_ZLECENIA>CAST('{miec_temu_2}' as datetime)"
        sql = sql.format(jutro=jutro, miec_temu_2=miec_temu_2)
        sql2 = "update zlecenie_badania set ZLECENIE_NA_DZIEN=CAST('{dawno}' as datetime) "\
              "where NUMER_ZLECENIA < 10000 "\
              "and ZREALIZOWANE='N' and WYKONANE='N'"\
              "and DATA_ZLECENIA<=CAST('{miec_temu_2}' as datetime)"
        sql2 = sql2.format(dawno=dawno, miec_temu_2=miec_temu_2)
        try:
            with pymssql.connect(**self.db) as conn:
                with conn.cursor(as_dict=True) as cursor:
                    self.logger.debug('ob update: {sql}'.format(sql=sql))
                    cursor.execute(sql)
                    self.logger.debug('ob update: {sql}'.format(sql=sql2))
                    cursor.execute(sql2)
                    conn.commit()
        except Exception as e:
            self.logger.error(e)

    def przenies_przyjete_na_dzis(self):
        now = datetime.datetime.now().strftime(os.getenv('FORMAT_CZASU_BAZA'))
        dzis = datetime.date.today()
        jutro = dzis + datetime.timedelta(days=1)
        jutro = jutro.strftime(os.getenv('FORMAT_CZASU_BAZA'))
        sql1 = "select ID_ZLECENIA from zlecenie_badania "\
              "where NUMER_ZLECENIA > 10000 "\
              "and ZREALIZOWANE='N' and WYKONANE='N' "\
              "and ZLECENIE_NA_DZIEN>=CAST('{jutro}' as datetime)"
        sql2 = "update zlecenie_badania set ZLECENIE_NA_DZIEN=CAST('{dzis}' as datetime), "\
              "DATA_POBRANIA=CAST('{now}' as datetime) "\
              "where ID_ZLECENIA in ({zlecenia})"
        sql3 = "update probki set DATA_POBRANIA=CAST('{now}' as datetime) "\
              "where ID_ZLECENIA in ({zlecenia})"
        sql1 = sql1.format(jutro=jutro)
        try:
            with pymssql.connect(**self.db) as conn:
                with conn.cursor(as_dict=True) as cursor:
                    self.logger.debug('ob select: {sql}'.format(sql=sql1))
                    cursor.execute(sql1)
                    rows = cursor.fetchall()
                    if rows:
                        zlec = []
                        for row in rows:
                            zlec.append(str(row['ID_ZLECENIA']))
                        zlecenia = ', '.join(zlec)
                        sql2 = sql2.format(dzis=dzis, now=now, zlecenia=zlecenia)
                        sql3 = sql3.format(now=now, zlecenia=zlecenia)
                        self.logger.debug('ob update: {sql}'.format(sql=sql2))
                        cursor.execute(sql2)
                        self.logger.debug('ob update: {sql}'.format(sql=sql3))
                        cursor.execute(sql3)
                        conn.commit()
        except Exception as e:
            self.logger.error(e)



