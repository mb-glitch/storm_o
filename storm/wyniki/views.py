import datetime
import urllib
import os
from io import BytesIO
from zipfile import ZipFile
import logging

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import Zlecenie, WynikPDF, WynikPNG, Wynik, Pacjent
from .forms import PacjentForm

logger = logging.getLogger(__name__)


@login_required
def rejestracja(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = PacjentForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            print(request.POST)
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect(reverse('wyniki:rejestracja'))        

    # if a GET (or any other method) we'll create a blank form
    else:
        form = PacjentForm()

    return render(request, 'wyniki/rejestracja.html', {'form': form})

@login_required
def pacjenci(request):
    q = request.GET.get('q', None)
    qs = Pacjent.objects.all()
    for term in q.split():
        qs = qs.filter( Q(nazwisko__icontains = term) | Q(imie__icontains = term) | Q(pesel__icontains = term))
    lista = []
    for p in qs:
        lista.append({'id': p.id, 'text': p.__str__()})
    response = JsonResponse(
            {"results": lista,"pagination": {"more": True}},
            safe=False
            )
    return response

@login_required
def index_view(request, zakres_dat):
    context = {}
    teraz = timezone.now()
    dzis = teraz.replace(hour=0, minute=0, second=0, microsecond=0)
    jutro = dzis + datetime.timedelta(days=1)
    tydzien = dzis - datetime.timedelta(days=7)
    miesiac = dzis - datetime.timedelta(days=30)
    rok = dzis.replace(month=1, day=1)
    l = Zlecenie.objects.all().prefetch_related('wyniki')
    if not request.user.is_staff:
        l = l.filter(owner__myuser__user=request.user)
    if zakres_dat == 'niepobrane':
        l = l.filter(owner__myuser__user=request.user)
        l = l.filter(wynikpdf__pobrany=False, wynikpdf__podpisany=True).distinct()
    elif zakres_dat == 'dzisiaj':
        l = l.filter(na_dzien__gte=dzis, na_dzien__lte=teraz)
    elif zakres_dat == '7dni':
        l = l.filter(na_dzien__gte=tydzien, na_dzien__lte=teraz)
    elif zakres_dat == '30dni':
        l = l.filter(na_dzien__gte=miesiac, na_dzien__lte=teraz)
    elif zakres_dat == 'rok':
        l = l.filter(na_dzien__gte=rok, na_dzien__lte=teraz)
    elif zakres_dat == 'wszystkie':
        l = l
    context['tekst_wyszukiwania'] = ''
    context['zakres_dat'] = zakres_dat
    context['urlparams'] = urllib.parse.urlencode(request.GET)
    q = request.GET.get('q', None)    
    if q:
        context['tekst_wyszukiwania'] = q
        l1 = Zlecenie.objects.none()
        try:
            i = int(q)
            l1 = l.filter(numer__exact=i)
        except Exception as e:
            pass
        if not l1:
            for term in q.split():
                l = l.filter( Q(pacjent__nazwisko__icontains = term) | Q(pacjent__imie__icontains = term) | Q(pacjent__pesel__icontains = term))
        else:
            l = l1
    # ustawienia podziału wyświetlanej strony
    paginator = Paginator(l, 20)
    page = request.GET.get('page')
    zlecenia = paginator.get_page(page)
    context['lista_zlecen'] = zlecenia
    
    return render(request, 'wyniki/index.html', context)

@login_required
def zlecenie_view(request, numer_zlecenia):
    zlecenie = get_object_or_404(Zlecenie, numer=numer_zlecenia)
    
    w_all = zlecenie.wyniki.all() if zlecenie else None
    wyniki = zlecenie.wyniki.filter(parent=None) if zlecenie else None
    print(type(wyniki))
    for w in wyniki:
        print(w.badanie.nazwa)
        print(w.children.all())    
    return render(request, 'wyniki/zlecenie.html', {'zlecenie': zlecenie, 'wyniki': wyniki})


@login_required
def pdf_view(request, wynikpdf_id):
    # Create the HttpResponse object with the appropriate PDF headers.
    pdf_file = WynikPDF.objects.get(pk=wynikpdf_id)
    response = HttpResponse(pdf_file.pdf, content_type='application/pdf')
    name = pdf_file.pdf.name.split('/')[-1]
    response['Content-Disposition'] = 'attachment; filename={}'.format(name)
    pdf_file.pobrany = True
    pdf_file.save()
    return response

@login_required
def niepobrane_zip(request):
    # Files (local path) to put in the .zip
    # FIXME: Change this (get paths from DB etc)
    filenames = []
    pdfs = WynikPDF.objects.filter(zlecenie__owner__myuser__user=request.user, pobrany=False, podpisany=True)
    for f in pdfs:
        filenames.append(f.pdf.path)
        logger.debug(f.pdf.path)
    # Folder name in ZIP archive which contains the above files
    # E.g [thearchive.zip]/somefiles/file2.txt
    # FIXME: Set this to something better
    zip_filename = "wyniki.zip"
    # Open StringIO to grab in-memory ZIP contents
    s = BytesIO()
    # The zip compressor
    zf = ZipFile(s, "w")
    for fpath in filenames:
        # Calculate path for file in zip
        fdir, fname = os.path.split(fpath)
        # Add file, at correct path
        zf.write(fpath, fname)
    # Must close zip for all contents to be written
    zf.close()
    # Grab ZIP file from in-memory, make response with correct MIME-type
    response = HttpResponse(s.getvalue(), content_type = "application/x-zip-compressed")
    # ..and correct content-disposition
    response['Content-Disposition'] = 'attachment; filename={}'.format(zip_filename)
    pdfs.update(pobrany=True)
    return response

@login_required
def akceptowanie_pdf(request):
    if request.user.is_staff:
        context = {}
        l = WynikPDF.objects.order_by('created').prefetch_related('img')
        l = l.filter(do_sprawdzenia=True)
        do_sprawdzenia_ogolnie = l.count()
        l = l.filter(owner=request.user)
        do_sprawdzenia_user = l.count()
        l = l.first()
        w = l.wyniki.filter(anulowany=False) if l else None
        context = {'obrazek': l, 'wyniki': w,'do_sprawdzenia_ogolnie': do_sprawdzenia_ogolnie, 'do_sprawdzenia_user': do_sprawdzenia_user}
        return render(request, 'wyniki/akceptowanie_pdf.html', context)

@login_required
def pdf_vote(request, wynikpdf_id):
    try:
        pdf = get_object_or_404(WynikPDF, pk=wynikpdf_id)
        if request.POST.get('ok'):
            pdf.przenies_do_podpisania()
            pdf.save()
            return HttpResponseRedirect(reverse('wyniki:akceptowanie_pdf'))        
        elif request.POST.get('nie'):
            pdf.do_sprawdzenia = False
            pdf.anulowany = True
            pdf.save()
            return HttpResponseRedirect(reverse('wyniki:akceptowanie_pdf'))  
    except (KeyError, WynikPDF.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'wyniki/akceptowanie_pdf.html', {
            'error_message': "You didn't select a choice.",
        })
