from django.shortcuts import render

def landing_page_view(request):
    """View para a página inicial (landing page)"""
    return render(request, 'landing.html')