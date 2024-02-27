
from django.urls import path

from . import views

app_name = 'wyniki'
urlpatterns = [
    path('rejestracja/', views.rejestracja, name='rejestracja'),
    path('pacjenci/', views.pacjenci, name='pacjenci'),
    path('niepobrane/', views.index_view, {'zakres_dat': 'niepobrane'}, name='index-niepobrane'),
    path('niepobrane/zip/', views.niepobrane_zip, name='niepobrane-zip'),
    path('dzisiaj/', views.index_view, {'zakres_dat': 'dzisiaj'}, name='index-dzisiaj'),
    path('7dni/', views.index_view, {'zakres_dat': '7dni'}, name='index-7dni'),
    path('30dni/', views.index_view, {'zakres_dat': '30dni'}, name='index-30dni'),
    path('rok/', views.index_view, {'zakres_dat': 'rok'}, name='index-rok'),
    path('wszystko/', views.index_view, {'zakres_dat': 'wszystkie'}, name='index-wszystkie'),
    path('zlecenie/<int:numer_zlecenia>/', views.zlecenie_view, name='zlecenie'),
    path('pdf/akceptujpdf/', views.akceptowanie_pdf, name='akceptowanie_pdf'),
    path('pdf/<uuid:wynikpdf_id>/', views.pdf_view, name='wynikpdf'),
    path('pdf/<uuid:wynikpdf_id>/pdf_vote/', views.pdf_vote, name='pdf_vote'),
    ]
