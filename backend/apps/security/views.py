from django.shortcuts import render


def svt_request_page(request, election_uuid):
    return render(request, "security/svt_request.html", {"election_uuid": election_uuid})


def svt_verify_page(request):
    return render(request, "security/svt_verify.html")


def svt_admin_list_page(request, election_uuid):
    return render(request, "security/svt_list.html", {"election_uuid": election_uuid})


def security_center_page(request):
    return render(request, "security/center.html")


def audit_logs_page(request):
    return render(request, "security/audit.html")


def device_monitoring_page(request):
    return render(request, "security/devices.html")


def location_monitoring_page(request):
    return render(request, "security/locations.html")


def security_alerts_page(request):
    return render(request, "security/alerts.html")
