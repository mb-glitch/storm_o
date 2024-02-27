# -*- coding: utf-8 -*-
#
"""
Maciej Bilicki
program służy do odbiory zleceń z plików .ord
pliki znajdują się w katalogu
wymiana plików podlega innemu mechanizmowi (najchętniej pscp i scp i ssh)
wersja: 0.1
"""

import os
import time
import logging
from hl7v3 import zlecenia, obsluga_baz


logger = logging.getLogger('hl7v3')


def stworz_mapowania():
    from media.mapowania import mapowania

def analizuj_zlecenia():
    for f in os.listdir(os.getenv('KATALOG_NOWYCH_ZLECEN')):
        if f.endswith(os.getenv('ROZSZERZENIE_ZLECENIE')):
            path = os.path.join(os.getenv('KATALOG_NOWYCH_ZLECEN'), f)
            zlecenie = zlecenia.ZlecenieImport(path)
            zlecenie.analizuj()

def przenies_nieprzyjete_na_jutro():
    ob = obsluga_baz.ObslugaBaz()
    ob.przenies_nieprzyjete_na_jutro()

def przenies_przyjete_na_dzis():
    ob = obsluga_baz.ObslugaBaz()
    ob.przenies_przyjete_na_dzis()
    


if __name__ == "__main__":
    # tworzy i uzupełnia tabelę zgodnie z plikiem csv    
    # logger.debug('robię mapowania')
    # stworz_mapowania()

    # uruchomić raz dziennie, przenosi wszystkie przesłane zlecenia na jutro
    logger.debug('przenoszę nieprzyjęte na jutro')
    przenies_nieprzyjete_na_jutro()

    # uruchomić raz na parę minut przenosi przyjęte z jutra na dzisiaj
    logger.debug('przenieszę przyjęte na dzisiaj')
    przenies_przyjete_na_dzis()

    # generowanie wydruku
    logger.debug('generuje wyniki')
    zlec = ['00003237360599999999', '00003237550699999999', '00003237580799999999', '00003237620499999999', '00003237780599999999']
    zlec = ['00000000030000000000'] # na potrzeby testów do mmedici
    #zlec = ['00003288470799999999']
    #zlec = []    
    for a in zlec:
        z = zlecenia.ZlecenieExport()
        z.analizuj_zlecenie(a)
        z.generuj()

    logger.debug('importuje zlecenia')
    analizuj_zlecenia()
    time.sleep(int(os.getenv('TIMEOUT')))



