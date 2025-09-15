from django.shortcuts import render
from django.utils import timezone
# Create your views here.


def pantalla_view(request):
    codigo = request.GET.get('codigo', '')  # p.ej. /pantalla?codigo=123
    ts = int(timezone.now().timestamp())    # cache-busting
    return render(request, 'pantalla-comedor/pantalla.html', {'codigo': codigo, 'ts': ts})