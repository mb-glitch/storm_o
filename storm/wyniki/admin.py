from django.contrib import admin

from .models import Wynik
from .models import Badanie, GrupaBadan
from .models import Pacjent
from .models import Zlecenie
from .models import WynikPDF, WynikPNG
from .models import Kontrahent
from .models import MyUser
from .models import WartosciReferencyjne
from .models import Probka


class BadanieAdmin(admin.ModelAdmin):
    search_fields = ('nazwa', 'nazwa_krotka')
    autocomplete_fields = ['children']

class ZlecenieAdmin(admin.ModelAdmin):
    search_fields = ('numer', )
    autocomplete_fields = ['pacjent']

class PacjentAdmin(admin.ModelAdmin):
    search_fields = ('pesel', 'nazwisko', 'imie')

admin.site.register(Wynik)

admin.site.register(Badanie, BadanieAdmin)

admin.site.register(GrupaBadan)

admin.site.register(Pacjent, PacjentAdmin)
admin.site.register(Zlecenie, ZlecenieAdmin)
admin.site.register(WynikPDF)
admin.site.register(WynikPNG)
admin.site.register(Kontrahent)
admin.site.register(MyUser)
admin.site.register(WartosciReferencyjne)
admin.site.register(Probka)
