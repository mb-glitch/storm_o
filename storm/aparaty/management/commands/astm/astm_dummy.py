# -*- coding: utf-8 -*-
#
"""
Maciej Bilicki
program służy do odebrania wyników z aparatu sysmex-xs
i przesłania ich do systemu lab3000

wersja: 1.1
"""
import os
import re
import time
import unicodedata
import socket
import select
import logging

logger = logging.getLogger(__name__)

class ASTM:
    """
    Tworzy wiecznie aktywny socket serwer,
    który przyjmuje tylko jedno połączenie i obsługuje je
    resetując i wznawiając połączenie

    Args:
        None 

    Returns:
        None

    Raises:
        KeyError: Raises an exception.

    """

    CONN_IN_WAITING = 1  # parametr do listen() liczba połączeń
    DELAY = 10
    RAMKA_ROZMIAR_MAX = 233 # 240 - 6 znaków stx etx suma i crlf

    #: ASTM specification base encoding.
    ENCODING = 'latin-1'
    #: NULL BIT
    NULL = '\x00'
    #: Message start token.
    STX = '\x02'
    #: Message end token.
    ETX = '\x03'
    #: ASTM session termination token.
    EOT = '\x04'
    #: ASTM session initialization token.
    ENQ = '\x05'
    #: Command accepted token.
    ACK = '\x06'
    #: Command rejected token.
    NAK = '\x15'
    #: Message chunk end token.
    ETB = '\x17'
    LF  = '\x0A'
    CR  = '\x0D'
    # CR + LF shortcut
    CRLF = CR + LF
    #: Record fields delimiter.
    FIELD_SEP_BIN     = '\x7C' # |  #

    #: Message records delimiter.
    RECORD_SEP    = '\x0D' # \r #
    #: Record fields delimiter.
    FIELD_SEP     = '\x7C' # |  #
    #: Delimeter for repeated fields.
    REPEAT_SEP    = '\x5C' # \  #
    #: Field components delimiter.
    COMPONENT_SEP = '\x5E' # ^  #
    #: Date escape token.
    ESCAPE_SEP    = '\x26' # &  #

    slownik = {
            NULL: '<NULL>',
            STX: '<STX>',
            ETX: '<ETX>',
            EOT: '<EOT>',
            ENQ: '<ENQ>',
            ACK: '<ACK>',
            NAK: '<NAK>',
            ETB: '<ETB>',
            CR: '<CR>',
            LF: '<LF>',
            } 

    def translate(self, tekst):
        if tekst == '':
            return '<NULL>'
        for k in self.slownik:
            if k in tekst:
                tekst = re.sub(k, self.slownik[k], tekst)
        return tekst

    def retranslate(self, tekst):
        if tekst == '':
            return '<NULL>'
        for k in self.slownik:
            if slownik[k] in tekst:
                tekst = re.sub(self.slownik[k], k, tekst)
        return tekst
    
    def __init__(self, serwer=False, klient=False, port=5000, host='', dummy=False):
        self.serwer = serwer
        self.klient = klient
        self.host = host
        self.port = port
        self.dummy = dummy
        tryb = 'serwer' if self.serwer else 'klient'
        logger.info('Inicjalizuje nowy serwer astm, port: {port}, tryb: {tryb}'.format(port=self.port, tryb=tryb))
        self.soc, self.conn, self.addr = None, None, None
        self.inbuffer = []
        self.cleaned_data = []
        self.mam_wiadomosc = False
        self.connected_v = False
        self.time_point = time.time()
        self.time_conn = time.time()
        self.delay = 0 # pierwsze połączenie bez opóźnienia    
        self.error_msg = ''

    def loop(self):
        if self.conn and not self.dummy: 
            self._handle_receive(self._receive())
            if self.mam_wiadomosc:
                msg = self.cleaned_data
                self.cleaned_data = []
                self.mam_wiadomosc = False
                return msg 
        else:
            if self.serwer:
                if not self.soc:
                    self._serve()
                else:
                    self._handle_connect()
            if self.klient:
                self.connect()

    def _serve(self):
        logger.debug('_serve')
        self.soc, self.conn, self.addr = None, None, None
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.bind((self.host, self.port))
        self.soc.listen(self.CONN_IN_WAITING)
        self.soc.settimeout(60)

    def _handle_connect(self):
        try:
            logger.info('Czekam na połączenie')
            self.conn, self.addr = self.soc.accept()
            self.connected_v = True
            self.conn.settimeout(60)
            logger.info('Połączono z {addr}'.format(addr=self.addr))
            self.error_msg = ''
        except socket.timeout:
            self.error_msg = 'Czekam na połączenie...'
            logger.debug('soc timeout continue')
        except Exception as e:
            self.error_msg = e
            logger.error('Nie udało się nawiązać połączenia')
            logger.error(e)
            self._close()
            

    def connect(self):
        while not self.connected_v:
            time.sleep(self.delay)
            self.delay = self.DELAY
            try:
                self.error_msg = 'Czekam na połączenie...'
                logger.info('Czekam na połączenie...')
                self.conn = socket.create_connection((self.host, self.port))
                logger.info('Połączono z {addr}'.format(addr=self.conn.getpeername()[0]))
                self.conn.settimeout(60)
                self.connected_v = True
                self.error_msg = ''
            except Exception as e:
                self.error_msg = e
                logger.info('Nie udało się nawiązać połączenia. Błąd: {}'.format(e))
                if self.conn:
                    self._close()
                else:
                    self.connected_v = False

    def _close(self):
        try:
            logger.info('Zamykam połączenie')
            self.connected_v = False
            self.conn.close()
            self.conn, self.addr = None, None
        except Exception as e:
            self.error_msg = e
            logger.error(e)
            logger.error('Nie udało się zamknąć połączenia')
            time.sleep(10)

    def _handle_send(self, msg):
        while msg:
            do_wyslania = msg.pop(0)
            self._send_frame(do_wyslania)
            if do_wyslania == self.EOT:  # nie wymaga potwierdzania otrzymania eot
                return
            data = self._receive()
            while data == self.NAK:
                self._send_frame(do_wyslania)
                data = self._receive()
            if do_wyslania == data == self.ENQ: # wymuszenie przesylania przez aparat
                msg = []
                return
            if msg and data == self.ACK:  # kontynuj
                continue
            else:
                logger.error('Błąd przy wysyłaniu')
                msg = []
                return

    def _handle_receive(self, data):
        if not data:
            self._close
            return
        elif data == self.NULL:
            self._close
            return
        elif data == self.ENQ:
            poprawna_ramka = True
            self.inbuffer = []
        elif data == self.EOT:
            logger.debug('Koniec wiadomości')
            self._analizuj()
            return
        elif data == self.ACK:
            return
        else:
            poprawna_ramka = self._czy_ramka_poprawna(data)
        if poprawna_ramka:
            logger.debug('Odebrałem poprawną ramkę')
            self._send_frame(self.ACK)
            if data not in [self.ENQ]:
                self.inbuffer.append(data)
        else:
            logger.warning('Odebrałem błędną ramkę')
            self._send_frame(self.NAK)

    def _receive(self):
        """
        Odbiera dane z ustanowionego portu, w razie braku połączenia,
        próbuje je ponownie nawiązać i dalej czeka na dane

        Args:
            None 

        Returns:
            data: zwraca binarne dane odebrane z socket

        Raises:
            KeyError: Raises an exception.
        """
        logger.debug('Czekam na dane...')
        try:
            data = self.conn.recv(4096)
            logger.debug('Odebrałem: {data}'.format(data=self.translate(data.decode())))
            if not data:
                self._close()
            return data.decode()

        except socket.timeout:
            logger.debug('recv timeout continue')

        except Exception as e:
            self.error_msg = e
            logger.error('Błąd przy _receive')
            logger.error(e)
            self._close()
    
    def _czy_ramka_poprawna(self, msg):
        """ Sprawdza czy ramka rozpoczyna i kończy się odpowiednimi znakami,
        wysyła odpowiednią część wiadomości do sprawdzenia sumy kontrolnej
        """
        if msg in [self.ACK, self.NAK, self.ENQ, self.EOT]:
            return True
        if not msg.startswith(self.STX) and msg.endswith(self.CRLF):
            return False
        if len(msg) < 7:
            return False        
        stx, frame, chck, crlf = msg[0], msg[1:-4], msg[-4:-2], msg[-2:] 
        suma_kontrolna = self._make_checksum(frame)
        if not suma_kontrolna == chck:
            logger.debug('Błędna suma kontrolna')
            logger.debug('Suma kontrolna: {suma}'.format(suma=suma_kontrolna))
            logger.debug('Ramka kontrolna: {frame}'.format(frame=self.translate(frame)))
            return False
        else:
            return True

    def _czy_ramka_podzielona(self, msg):
        """Checks plain msg for chunked byte."""
        length = len(msg)
        if len(msg) < 5:
            return False
        if self.ETB not in msg:
            return False
        return msg.index(self.ETB) == length - 5
    
    @property
    def _seq(self):
        seq = self.numeracja_ramek % 8 + 1        
        self.numeracja_ramek += 1
        seq = 0 if seq == 8 else seq
        return seq
    
    def _przygotuj_ramke_etx(self, data):
        """Przygotowuje ramkę do wysłania w wersji całej zakończonej ETX"""
        ramka = data
        frame = '{index}{ramka}{etx}'.format(index=self._seq,
                                            ramka=ramka,
                                            etx=self.ETX)
        chck = self._make_checksum(frame)
        ramka = '{stx}{frame}{chck}{crlf}'.format(stx=self.STX,
                                                frame=frame,
                                                chck=chck,
                                                crlf=self.CRLF)
        return ramka

    def _przygotuj_ramke_etb(self, data):
        """Przygotowuje ramkę do wysłania w wersji częsciowej zakończonej ETB"""
        ramka = data
        frame = '{index}{ramka}{etb}'.format(index=self._seq,
                                            ramka=ramka,
                                            etb=self.ETB)
        chck = self._make_checksum(frame)
        ramka = '{stx}{frame}{chck}{crlf}'.format(stx=self.STX,
                                                frame=frame,
                                                chck=chck,
                                                crlf=self.CRLF)
        return ramka

    def _przygotuj_ramke(self, data):
        """Przygotowuje ramkę do wysłania z listy wiadomości od parsera"""
        if not data:
            return data
        data = '{data}{cr}'.format(data=data, cr=self.CR)  # dodaję znacznik cr na koniec każdej lini
        chunks = [data[i:i+self.RAMKA_ROZMIAR_MAX] \
                for i in range(0, len(data), self.RAMKA_ROZMIAR_MAX)]
        ile_ramek = len(chunks)
        lista_ramek = []
        if ile_ramek == 1:
            lista_ramek.append(self._przygotuj_ramke_etx(data))
            return lista_ramek
        else:
            i = 1
            for chunk in chunks:
                if i < ile_ramek:
                    lista_ramek.append(self._przygotuj_ramke_etb(chunk))
                    i += 1
                else:
                    lista_ramek.append(self._przygotuj_ramke_etx(chunk))
            return lista_ramek

    def _send_frame(self, ramka):
        """
        Wysyła dane do otwartego portu
        """
        ramka = ramka
        try:
            logger.debug('Wysyłam: {ramka}'.format(ramka=self.translate(ramka)))
            self.conn.sendall(ramka.encode())
            logger.debug('Wysłałem: {ramka}'.format(ramka=self.translate(ramka)))
        except Exception as e:
            self.error_msg = e
            logger.error('Wysyłam: {ramka}'.format(ramka=self.translate(ramka)))
            logger.error(e)
            self._close()

    def send(self, data):
        """
        Przygotowuje wiadomość do wysłania w formie listy kolejnych komunikatów

        Args:
            data: string dane do wysłania do socket 

        Returns:
            None

        Raises:
            KeyError: Raises an exception.
        """
        self.numeracja_ramek = 0
        data = data
        msg = []
        if type(data) in (list, tuple):
            msg.append(self.ENQ)
            for line in data:
                ramka = self._przygotuj_ramke(line)
                msg += ramka
            msg.append(self.EOT)
        logger.debug(msg)
        self._handle_send(msg)
        

    def _make_checksum(self, msg):
        """Calculates checksum for specified message.
        :param msg: ASTM message.
        :type msg: bytes
        :returns: Checksum value that is actually byte sized integer in hex base
        :rtype: bytes
        """
        if not isinstance(msg[0], int):
            msg = map(ord, msg)
        return hex(sum(msg) & 0xFF)[2:].upper().zfill(2)
    
    def _analizuj(self):
        """Analizuje odebrane ramki, łączy jeżeli były rozdzielone,
        dekoduje z binarnego,
        zamienia na listę - podział po | i wysyła do cleand data
        """
        chunks = []
        for msg in self.inbuffer:
            frame = msg[2:-5]
            if msg[-5] == self.ETB:
                chunks.append(frame)
            else:
                if chunks:
                    joined_chunks = ''.join(chunks)
                    frame = joined_chunks + frame
                    chunks = []
                frame = frame[:-1] if frame.endswith(self.RECORD_SEP) else frame
                if self.RECORD_SEP in frame:
                    frames = frame.split(self.RECORD_SEP)
                    for f in frames:
                        self.cleaned_data.append(f.split(self.FIELD_SEP))
                        
                else:
                    self.cleaned_data.append(frame.split(self.FIELD_SEP))
        self.mam_wiadomosc = True
        logger.debug('cleaned data')
        logger.debug(self.cleaned_data)
