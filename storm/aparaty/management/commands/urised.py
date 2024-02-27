import logging
import time
import datetime

from django.core.management.base import BaseCommand
from aparaty.models import Wynik, TestZnakowy, Aparat
from aparaty.management.commands.astm.astm_urised import ASTM

# Get an instance of a logger
logger = logging.getLogger(__name__)

def znajdz_numer_zlecenia(pozycja_z_numerem):
    # nr_zlecenia = nr_zlecenia[-10:-2]  # poprawić w jakiśrozsądniejszy sposób
    nr_zlecenia = str(pozycja_z_numerem)
    for n in nr_zlecenia:
        if n not in ['0','1','2','3','4','5','6','7','8','9']:
            nr_zlecenia = nr_zlecenia.replace(n, '')
    nr_zlecenia = nr_zlecenia.zfill(10)
    return nr_zlecenia

def consume(new_data, aparat):
    numer_zlecenia = ''
    data_wyniku = None
    frame_index_poprzedni = ''
    wyniki = []
    response = None

    for frame in new_data:
        frame_index =  frame[0]
        logger.debug('new data = {}'.format(frame))    
        if frame_index == 'H':
            numer_zlecenia = ''
            wyniki = []
        elif frame_index == 'P':
            pass
        elif frame_index == 'O':
            numer_zlecenia = znajdz_numer_zlecenia(frame[aparat.pole_numery_zlecenia_order])
            data_wyniku = frame[aparat.pole_data_wyniku]
            data_wyniku = datetime.datetime.strptime(data_wyniku, "%Y%m%d%H%M%S")
        elif frame_index == 'Q':
            pass
        elif frame_index == 'R':
            try:
                nazwa = frame[aparat.pole_nazwa_badania]
                wynik = frame[aparat.pole_wynik]

                jednostki = frame[aparat.pole_jednostki]
                if not jednostki:
                    if wynik in ['-', '+', '++', '+++', '++++', '+++++']:
                        jednostki = 'plusowe'
                flaga = frame[aparat.pole_flaga]
                w = TestZnakowy.objects.filter(nazwa=nazwa)
                if w.count() > 1:
                    w = w.filter(jednostki=jednostki)
                w = w[0]
                wyniki.append(
                    Wynik.objects.create(
                        pid=numer_zlecenia,
                        data = data_wyniku,
                        wynik = wynik,
                        obrazek = '',
                        test_znakowy = w,
                        )
                )
            except Exception as e:
                logger.error('Błąd przy przypisywaniu do Wynik')
                logger.error(e)
        elif frame_index == 'C':
            if frame_index_poprzedni == 'R':
                frame_index = 'R'  # jakby było więcej niż jeden komentarz to chce dopisać do tego samego wyniku
        elif frame_index == 'L':
            for w in wyniki:
                w.save()
        frame_index_poprzedni = frame_index  # jakbym chciał dopisać komentarz do wyniku
    return response


class Command(BaseCommand):
    help = 'Zarządza komunikacją z aparatem'
    
    def handle(self, *args, **options):
        astm = ASTM(serwer=True, port=5003)
        aparat = Aparat.objects.get(nazwa='urised')
        while True:
            try:
                data = None
                response = None
                while not data:
                    # status połączenia
                    aparat.astm = astm.connected_v
                    aparat.astm_msg = astm.error_msg
                    aparat.save()
                    # pętla połączenia i odbierania z aparatu
                    data = astm.loop()
                if data:
                    response = consume(data, aparat)
                if response:
                    astm.send(response)
            except Exception as e:
                logger.error(e)
                astm._close
