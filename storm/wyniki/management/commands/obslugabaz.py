import pymssql
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)



class ObslugaBaz:
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
    pp = {
    'server':'192.168.0.128',
    'port':1433,
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

    def __init__(self):
        self._conn = None
        self._db = self.pp

    def connect(self):
        if not self._conn:
            self._conn = pymssql.connect(**self._db)
            logger.info('Połączyłem się z mssql') 
        
    def close(self):
        self._conn.close()
        self._conn = None

    def select(self, sqlcmd):
        self.connect()
        try:
            with self._conn.cursor(as_dict=True) as cursor:
                cursor.execute(sqlcmd)
                logger.debug('Wysłałem zapytanie do mssql: {sqlcmd}'.format(sqlcmd=sqlcmd))
                return cursor.fetchall()          
  
        except Exception as e:
            logger.error('Błąd zapytania do mssql: {sqlcmd}'.format(sqlcmd=sqlcmd))    
            logger.error(e)
            self.close()

    def insert(self, sqlcmd):
        self.connect()
        try:
            with self._conn.cursor(as_dict=True) as cursor:
                cursor.execute(sqlcmd)
                self._conn.commit()
                logger.debug('Wstawiam do mssql: {sqlcmd}'.format(sqlcmd=sqlcmd))         
  
        except Exception as e:
            logger.error('Błąd zapytania do mssql: {sqlcmd}'.format(sqlcmd=sqlcmd))    
            logger.error(e)
            self.close()
    
    def pobierz_replikacje_czynnosci(self):
        sql = 'select top 1000 * from replikacja_czynnosci order by id'
        return self.select(sql)

    def usun_replikacje_czynnosci(self, numery_wierszy_do_usuniecia):
        sql = 'delete from replikacja_czynnosci where id >= {id_min} and id <= {id_max}'
        sql = sql.format(id_min=min(numery_wierszy_do_usuniecia), id_max=max(numery_wierszy_do_usuniecia))
        self.insert(sql)

    def replikuj_wiersz(self, row):
        logger.debug('Replikuje wiersz: {row}'.format(row=row))         
        task = row['task']
        nazwa_tabeli = row['nazwa_tabeli']
        numer_wiersza = row['id_wiersza']
        if task in ('i', 'u'):
            sqlcmd = 'select * from {nazwa_tabeli} where {nazwa_wiersza_z_id}={id_wiersza}'
            sqlcmd = sqlcmd.format(**row)
            response = self.select(sqlcmd)
            for row in response:
                row['mb_nazwa_tabeli'] = nazwa_tabeli
                row['mb_task'] = task
            return response
        elif task == 'd':
            response = {}
            response['mb_nazwa_tabeli'] = nazwa_tabeli
            response['mb_task'] = task
            response['id_wiersza'] = numer_wiersza
            return response




