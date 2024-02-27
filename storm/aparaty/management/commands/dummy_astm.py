import logging
import time

from django.core.management.base import BaseCommand
from aparaty.models import Wynik
from .astm.astm_dummy import ASTM



# Get an instance of a logger
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Zarządza komunikacją z aparatem'
    
    def handle(self, *args, **options):
        astm = ASTM(klient=True, port=5003, host='127.0.0.1', dummy=True)
        parser = None
        data = None
        
        astm.loop()  # nawiązanie połączenia

        response = [
            'H|\^&|||LUP2^UA301000462^1.0.11^E77_int|||||||P|LIS2-A2|20190329105956',
            'P|1||03423421',
            'O|1|00077777|^^^^SAMPLE||R||||||X|||20190328121846',
            'M|1|RD|---|||||autologin||LabStripU11Plus',
            'R|1|1^^^Bil|neg|mg/dl||||||autologin|20190328121846|20190328121951',
            'R|2|2^^^Ubg|norm|mg/dl||||||autologin|20190328121846|20190328121951',
            'R|3|3^^^Ket|5|mg/dl||A||||autologin|20190328121846|20190328121951',
            'R|4|4^^^Asc|neg|mg/dl||||||autologin|20190328121846|20190328121951',
            'R|5|5^^^Glu|norm|mg/dl||||||autologin|20190328121846|20190328121951',
            'R|6|6^^^Pro|30|mg/dl||A||||autologin|20190328121846|20190328121951',
            'R|7|7^^^Ery|300|Ery/Âµl||A||||autologin|20190328121846|20190328121951',
            'R|8|8^^^pH|5.5|||||||autologin|20190328121846|20190328121951',
            'R|9|9^^^Nit|poz|||A||||autologin|20190328121846|20190328121951',
            'R|10|10^^^Leu|75|Leu/Âµl||A||||autologin|20190328121846|20190328121951',
            'R|11|11^^^SG|1.030|||||||autologin|20190328121846|20190328121951',
            'R|12|13^^^Col|krwisty|||||||autologin|20190328121846|20190328121951',
            'R|13|14^^^Cla|mÄ™tny|||||||autologin|20190328121846|20190328121951',
            'L|1|N'
            ]
    
        response = [
            'H|\^&|||UriSed mini^UriSed mini^3.2.19^1^UMI01000538|||||||P|LIS2-A2|20190329112545',
            'P|1||||-',
            'O|1|000077777|0^0^Service^SAMPLE|S|R||||||N|||20190328130052|||||||||||F',
            'R|1|46419-8^^^RBC|1477.40|p/HPF||A||F||Operator|||UriSed mini',
            'C|1|I|A|I',
            'R|2|798-9^^^RBC|6500.56|p/ul||A||F||Operator|||UriSed mini',
            'C|1|I|A|I',
            'R|3|^^^RBC|984.93|||A||F||Operator|||UriSed mini',
            'C|1|I|A|I',
            'R|4|53292-9^^^RBC|++++|||A||F||Operator|||UriSed mini',
            'C|1|I|A|I',
            'R|5|46702-7^^^WBC|0.00|p/HPF||N||F||Operator|||UriSed mini',
            'R|6|51487-7^^^WBC|0.00|p/ul||N||F||Operator|||UriSed mini',
            'R|7|^^^WBC|0.00|||N||F||Operator|||UriSed mini',
            'R|8|53316-6^^^WBC|-|||N||F||Operator|||UriSed mini',
            'R|9|53307-5^^^CRY|1.50|p/HPF||A||F||Operator|||UriSed mini',
            'C|1|I|A|I',
            'R|10|53297-8^^^CRY|6.60|p/ul||A||F||Operator|||UriSed mini',
            'C|1|I|A|I',
            'R|11|^^^CRY|1.00|||A||F||Operator|||UriSed mini',
            'C|1|I|A|I',
            'R|12|53334-9^^^CRY|+|||A||F||Operator|||UriSed mini',
            'C|1|I|A|I',
            'R|13|53307-5^^^.CRY|1.50|p/HPF||A||F||Operator|||UriSed mini',
            'C|1|I|A|I',
            'R|14|53297-8^^^.CRY|6.60|p/ul||A||F||Operator|||UriSed mini',
            'C|1|I|A|I',
            'R|15|^^^.CRY|1.00|||A||F||Operator|||UriSed mini',
            'C|1|I|A|I',
            'R|16|53334-9^^^.CRY|+|||A||F||Operator|||UriSed mini',
            'C|1|I|A|I',
            'R|17|^^^.CaOxm|15.00|p/HPF||N||F||Operator|||UriSed mini',
            'R|18|^^^.CaOxm|0.00|p/ul||N||F||Operator|||UriSed mini',
            'R|19|^^^.CaOxm|0.00|||N||F||Operator|||UriSed mini',
            'R|20|^^^.CaOxm|-|||N||F||Operator|||UriSed mini',
            'R|21|^^^.CaOxd|0.00|p/HPF||N||F||Operator|||UriSed mini',
            'R|22|^^^.CaOxd|0.00|p/ul||N||F||Operator|||UriSed mini',
            'R|23|^^^.CaOxd|0.00|||N||F||Operator|||UriSed mini',
            'R|24|38993-2^^^.CaOxd|-|||N||F||Operator|||UriSed mini',
            'R|25|33223-9^^^HYA|1.00|p/HPF||N||F||Operator|||UriSed mini',
            'R|26|51484-4^^^HYA|0.00|p/ul||N||F||Operator|||UriSed mini',
            'R|27|^^^HYA|0.00|||N||F||Operator|||UriSed mini',
            'R|28|50231-0^^^HYA|-|||N||F||Operator|||UriSed mini',
            'R|29|^^^PAT|5.00|p/HPF||N||F||Operator|||UriSed mini',
            'R|30|^^^PAT|0.00|p/ul||N||F||Operator|||UriSed mini',
            'R|31|^^^PAT|0.00|||N||F||Operator|||UriSed mini',
            'R|32|72224-9^^^PAT|-|||N||F||Operator|||UriSed mini',
            'R|33|53294-5^^^NEC|8.00|p/HPF||N||F||Operator|||UriSed mini',
            'R|34|51485-1^^^NEC|0.00|p/ul||N||F||Operator|||UriSed mini',
            'R|35|^^^NEC|0.00|||N||F||Operator|||UriSed mini',
            'R|36|50225-2^^^NEC|-|||N||F||Operator|||UriSed mini',
            'R|37|33219-7^^^EPI|0.00|p/HPF||N||F||Operator|||UriSed mini',
            'R|38|51486-9^^^EPI|0.00|p/ul||N||F||Operator|||UriSed mini',
            'R|39|^^^EPI|0.00|||N||F||Operator|||UriSed mini',
            'R|40|53318-2^^^EPI|-|||N||F||Operator|||UriSed mini',
            'R|41|^^^YEA|0.40|p/HPF||N||F||Operator|||UriSed mini',
            'R|42|51481-0^^^YEA|1.76|p/ul||N||F||Operator|||UriSed mini',
            'R|43|^^^YEA|0.27|||N||F||Operator|||UriSed mini',
            'R|44|72223-1^^^YEA|-|||N||F||Operator|||UriSed mini',
            'R|45|33218-9^^^BAC|1.90|p/HPF||N||F||Operator|||UriSed mini',
            'R|46|51480-2^^^BAC|8.36|p/ul||N||F||Operator|||UriSed mini',
            'R|47|^^^BAC|1.27|||N||F||Operator|||UriSed mini',
            'R|48|50221-1^^^BAC|-|||N||F||Operator|||UriSed mini',
            'R|49|33218-9^^^.BAC|0.00|p/HPF||N||F||Operator|||UriSed mini',
            'R|50|51480-2^^^.BAC|0.00|p/ul||N||F||Operator|||UriSed mini',
            'R|51|^^^.BAC|0.00|||N||F||Operator|||UriSed mini',
            'R|52|50221-1^^^.BAC|-|||N||F||Operator|||UriSed mini',
            'R|53|^^^.BACr|1.30|p/HPF||N||F||Operator|||UriSed mini',
            'R|54|^^^.BACr|5.72|p/ul||N||F||Operator|||UriSed mini',
            'R|55|^^^.BACr|0.87|||N||F||Operator|||UriSed mini',
            'R|56|^^^.BACr|-|||N||F||Operator|||UriSed mini',
            'R|57|^^^.BACc|0.60|p/HPF||N||F||Operator|||UriSed mini',
            'R|58|^^^.BACc|2.64|p/ul||N||F||Operator|||UriSed mini',
            'R|59|^^^.BACc|0.40|||N||F||Operator|||UriSed mini',
            'R|60|^^^.BACc|-|||N||F||Operator|||UriSed mini',
            'R|61|50235-1^^^MUC|0.00|p/HPF||N||F||Operator|||UriSed mini',
            'R|62|51478-6^^^MUC|0.00|p/ul||N||F||Operator|||UriSed mini',
            'R|63|^^^MUC|0.00|||N||F||Operator|||UriSed mini',
            'R|64|53321-6^^^MUC|-|||N||F||Operator|||UriSed mini',
            'L|1|N',
            'H|\^&|||LUP2^LUP2^1.0.11^1^UA301000462|||||||P|LIS2-A2|20190329112545',
            'P|1||||-',
            'O|1|000077777|0^0^Service^SAMPLE|C|R||||||N|||20190328130052|||||||||||F',
            'R|1|^^^Bil|neg|mg/dl||N||F||autologin|||LUP2',
            'R|2|^^^Ubg|norm|mg/dl||N||F||autologin|||LUP2',
            'R|3|^^^Ket|5|mg/dl||A||F||autologin|||LUP2',
            'C|1|I|A|I',
            'R|4|^^^Asc|neg|mg/dl||N||F||autologin|||LUP2',
            'R|5|^^^Glu|norm|mg/dl||N||F||autologin|||LUP2',
            'R|6|^^^Pro|30|mg/dl||A||F||autologin|||LUP2',
            'C|1|I|A|I',
            'R|7|^^^Ery|300|Ery/µl||A||F||autologin|||LUP2',
            'C|1|I|A|I',
            'R|8|^^^pH|5.5|||N||F||autologin|||LUP2',
            'R|9|^^^Nit|neg|||N||F||autologin|||LUP2',
            'R|10|^^^Leu|25|Leu/µl||A||F||autologin|||LUP2',
            'C|1|I|A|I',
            'R|11|^^^SG|1.030|||N||F||autologin|||LUP2',
            'R|12|^^^Col|wodojasny|||N||F||autologin|||LUP2',
            'R|13|^^^Cla|przejrzysty|||N||F||autologin|||LUP2',
            'L|1|N',
            ]

        astm.send(response)
        time.sleep(6)
