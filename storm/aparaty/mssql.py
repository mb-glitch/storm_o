import _mssql  #pymssql nie obsługuje dużych wyników obrazkowych
from PIL import Image, ImageOps
import binascii
import logging


logger = logging.getLogger(__name__)

class Mssql:
    mssql_sql_insert_wyniki = """
        exec proc_wstaw_wyniki_comdata 
        @PID='{pid}', 
        @TID={tid}, 
        @data_wyniku='{data}', 
        @typ_wyniku='{typ_wyniku}', 
        @flaga='', 
        @wynik='{wynik}', 
        @opis='', 
        @flaga_typu='W', 
        @wynik_numeryczny='{wynik_numeryczny}', 
        @nadpisz='{nadpisz}', 
        @obrazek=null, 
        @id_aparatu={id_aparatu}, 
        @info='', 
        @statyw=''
        """

    def __init__(self):
        self._conn_mssql = None
        self.db = 'lab3000'
        self.comdata = 'comdata'
        self.mssql_db = {
        'server':'192.168.2.110',
        #'server':'192.168.0.128',
        'port':1433,
        'user':'ADMIN',
        'password':'***',
        'database':self.db,
        'charset':'cp1250'
        }
        
    def _mssql_connect(self):
        try:
            if not self._conn_mssql:
                self._conn_mssql = _mssql.connect(**self.mssql_db)
            elif not self._conn_mssql.connected:
                self._conn_mssql = _mssql.connect(**self.mssql_db)
            logger.info('Połączyłem się z mssql')
        except Exception as e:
            self._conn_mssql = None
            logger.error(e)
            print(e)

    @property
    def _connected(self):
        if self._conn_mssql:
            return self._conn_mssql.connected
        else:
            self._conn_mssql = None
            return False
        
    def _mssql_disconnect(self):
        self._conn_mssql.close()
        self._conn_mssql = None

    def _execute(self, sqlcmd, db='lab3000'):
        """
        Wykonuje zapytanie sqlcmd

        Args:
            sciezka: w pełni sformatowane zapytanie sql

        Returns:
            response: zwraca listę dict w formacie
            [{0: 'wartość', 'NAZWA_KOLUMNY': 'wartość'}]

        Raises:
            KeyError: Raises an exception.
        """
        sqlcmd = sqlcmd
        if not self._connected:
            self._mssql_connect()
        self._conn_mssql.select_db(db)
        response = []
        try:
            self._conn_mssql.execute_query(sqlcmd)
            logger.debug('Wysłałem zapytanie do mssql: {sqlcmd}'.format(sqlcmd=sqlcmd))    
            response = [row for row in self._conn_mssql]
            logger.debug('Odpowiedź mssql: {response}'.format(response=response))    
        except Exception as e:
            logger.error('Błąd zapytania do mssql: {sqlcmd}'.format(sqlcmd=sqlcmd))    
            logger.error(e)    
            # self._mssql_execute(sqlcmd)
        return response
