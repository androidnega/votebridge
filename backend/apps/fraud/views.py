from django.shortcuts import render


def fraud_dashboard_page(request):
    return render(request, "fraud/dashboard.html")


def fraud_case_list_page(request):
    return render(request, "fraud/case_list.html")


def fraud_case_detail_page(request, fraud_case_id):
    return render(request, "fraud/case_detail.html", {"fraud_case_id": fraud_case_id})


def fraud_timeline_page(request, fraud_case_id):
    return render(request, "fraud/timeline.html", {"fraud_case_id": fraud_case_id})
