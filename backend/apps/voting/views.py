from django.shortcuts import render


def ballot_page(request, election_uuid):
    return render(request, "voting/ballot.html", {"election_uuid": election_uuid})


def ballot_confirmation_page(request, election_uuid):
    return render(request, "voting/ballot_confirmation.html", {"election_uuid": election_uuid})


def my_votes_page(request, election_uuid):
    return render(request, "voting/my_votes.html", {"election_uuid": election_uuid})
