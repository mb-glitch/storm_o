# -*- coding: utf-8 -*-
#

import csv
from hl7v3.obsluga_baz import ObslugaBaz

ob = ObslugaBaz()

sql_del = "IF EXISTS (SELECT TOP 1 * from mb_mapowania) DROP TABLE mb_mapowania;"

sql_create = "CREATE TABLE mb_mapowania (platnik int, badanie int, grupa int, kod_platnika varchar(20));"

sql_insert = "INSERT INTO mb_mapowania VALUES ({platnik}, {badanie}, {grupa}, '{kod_platnika}');"



ob.insert(sql_del)
ob.insert(sql_create)

with open('media/mapowania/mapowania.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        sql = sql_insert.format(
                platnik=row['platnik'],
                badanie=row['badanie'],
                grupa=row['grupa'],
                kod_platnika=row['kod_platnika']
            )
        ob.insert(sql)


