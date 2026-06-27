from django.shortcuts import render


def dashboard_index(request):
    return render(request, "dashboard/index.html")


def login_page(request):
    return render(request, "auth/login.html")
