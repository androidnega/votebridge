from django.shortcuts import render


def election_list_page(request):
    return render(request, "elections/list.html")


def election_create_page(request):
    return render(request, "elections/create.html")


def election_detail_page(request, uuid):
    return render(request, "elections/detail.html", {"election_uuid": uuid})


def election_edit_page(request, uuid):
    return render(request, "elections/edit.html", {"election_uuid": uuid})


def candidate_list_page(request, election_uuid):
    return render(
        request,
        "elections/candidates/list.html",
        {"election_uuid": election_uuid},
    )


def candidate_create_page(request, election_uuid):
    return render(
        request,
        "elections/candidates/create.html",
        {"election_uuid": election_uuid},
    )


def candidate_edit_page(request, uuid):
    return render(request, "elections/candidates/edit.html", {"candidate_uuid": uuid})


def position_list_page(request, election_uuid):
    return render(
        request,
        "elections/positions/list.html",
        {"election_uuid": election_uuid},
    )


def position_create_page(request, election_uuid):
    return render(
        request,
        "elections/positions/create.html",
        {"election_uuid": election_uuid},
    )


def position_edit_page(request, election_uuid, uuid):
    return render(
        request,
        "elections/positions/edit.html",
        {"election_uuid": election_uuid, "position_uuid": uuid},
    )


def eligibility_list_page(request, election_uuid):
    return render(
        request,
        "elections/eligibility/list.html",
        {"election_uuid": election_uuid},
    )


def eligibility_manage_page(request, election_uuid):
    return render(
        request,
        "elections/eligibility/manage.html",
        {"election_uuid": election_uuid},
    )
