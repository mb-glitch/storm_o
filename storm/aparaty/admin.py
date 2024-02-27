from django.contrib import admin

from .models import Aparat, Wynik, TestZnakowy

admin.site.register(Wynik)
admin.site.register(TestZnakowy)


class TestZnakowyInline(admin.TabularInline):
    model = TestZnakowy
    extra = 1


class AparatAdmin(admin.ModelAdmin):
    inlines = [TestZnakowyInline]

admin.site.register(Aparat, AparatAdmin)

