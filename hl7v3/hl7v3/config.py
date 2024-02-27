# -*- coding: utf-8 -*-
#

import os
import logging
import logging.config



settings = {
    # czas pomiędzy sprawdzeniem zleceń w katalogu
    'TIMEOUT': '5',

    # format czasu do konwerowania pomiędzy systemami
    'FORMAT_CZASU_BAZA': "%Y-%m-%d %H:%M:%S",
    'CDA_FORMAT_CZASU': '%Y%m%d%H%M%S',


    # id automatycznego systemu inf w bazie med-star
    'PERSONEL_ID_SYSTEM-pop-rawny z medtary': '8999',
    'PERSONEL_ID_SYSTEM': '9002',

    # lokalizacja katalogów ze zleceniami i wynikami, rozszeżenia
    'KATALOG_NOWYCH_ZLECEN': 'media/zlecenia_nowe',
    'KATALOG_ARCHIWUM_ZLECEN': 'media/zlecenia_archiwum',
    'KATALOG_BLEDNYCH_ZLECEN': 'media/zlecenia_bledne',
    'ROZSZERZENIE_ZLECENIE': '.ord',
    'ROZSZERZENIE_WYNIK': '.res',

    # logowanie
    'POZIOM_LOGOWANIA': 'DEBUG',
    'POZIOM_LOGOWANIA_KONSOLA': 'DEBUG',
    'POZIOM_LOGOWANIA_PLIK': 'DEBUG',
    'PLIK_LOGOWANIA': 'hl7ms.log',
    'LOGGER_NAZWA': 'hl7v3',
}


# wrzucam setting do zmiennych środowiskowych
for k, v in settings.items():    
    os.environ[k] = v

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
#'server':'127.0.0.1',
#'port':11433,
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


# konfiguracja logowania
logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'default': {'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'}
    },
    'handlers': {
        'console': {
            'level': os.getenv('POZIOM_LOGOWANIA_KONSOLA'),
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'level': os.getenv('POZIOM_LOGOWANIA_PLIK'),
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'default',
            'filename': os.getenv('PLIK_LOGOWANIA'),
            'maxBytes': 1024*1024,
            'backupCount': 10
        }
    },
    'loggers': {
        os.getenv('LOGGER_NAZWA'): {
            'level': os.getenv('POZIOM_LOGOWANIA'),
            'handlers': ['console', 'file']
        }
    },
    'disable_existing_loggers': False
})
